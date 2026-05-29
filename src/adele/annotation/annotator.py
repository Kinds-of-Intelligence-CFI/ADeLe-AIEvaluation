"""
High-level annotation orchestrator.

Provides the ``annotate()`` function that handles the full lifecycle:
    1. Build batch input files (one per demand × chunk)
    2. Upload and launch batch jobs via OpenAI Batch API — **or**
       call any model directly via litellm
    3. Poll for completion (batch) or collect results (direct)
    4. Download and parse results

Supports two backends:
    - ``"batch"``  — OpenAI Batch API (50% cheaper, higher limits, OpenAI only)
    - ``"direct"`` — Direct API calls via litellm (any model: Gemini, Claude, etc.)

Usage::

    from adele.annotation import annotate

    # OpenAI Batch API (cheapest, default for OpenAI models)
    results_df = annotate(data=benchmark_df, model="gpt-4o")

    # Any model via direct calls
    results_df = annotate(data=benchmark_df, model="gemini/gemini-2.0-flash")
    results_df = annotate(data=benchmark_df, model="claude-sonnet-4-20250514")

    # Explicit backend override
    results_df = annotate(data=benchmark_df, model="gpt-4o", backend="direct")
"""

import json
import time
import logging
from pathlib import Path
from typing import List, Optional

import pandas as pd
import openai
from tenacity import retry, retry_if_exception_type, wait_exponential, stop_after_attempt
from tqdm import tqdm

from adele.rubrics.catalog import RubricsCatalog
from adele.annotation.prompts import (
    build_annotation_prompt,
    build_batch_request,
    is_reasoning_model,
)
from adele.annotation.parsing import parse_multiple_outputs, to_wide_format

logger = logging.getLogger(__name__)

# Retry decorator for transient OpenAI errors
_retry_openai = retry(
    retry=retry_if_exception_type((
        openai.RateLimitError,
        openai.InternalServerError,
        openai.APIConnectionError,
        openai.APITimeoutError,
    )),
    wait=wait_exponential(multiplier=1, min=2, max=60),
    stop=stop_after_attempt(10),
    reraise=True,
)

# OpenAI model prefixes for auto-detecting batch eligibility
_OPENAI_PREFIXES = ("gpt-", "o1", "o3", "chatgpt-", "ft:gpt-")


def _is_openai_model(model: str) -> bool:
    """Check if a model string refers to an OpenAI model."""
    # Strip provider prefix if present
    bare = model.split("/", 1)[-1] if "/" in model else model
    return any(bare.startswith(p) for p in _OPENAI_PREFIXES)


def annotate(
    data: pd.DataFrame,
    *,
    demands: Optional[List[str]] = None,
    rubrics_folder: Optional[str] = None,
    model: str = "gpt-4o",
    backend: Optional[str] = None,
    max_completion_tokens: int = 1000,
    api_key: Optional[str] = None,
    output_dir: str = "./adele_annotations",
    poll_interval: int = 60,
    max_concurrent: int = 10,
    batch_chunk_size: int = 50000,
    format: str = "wide",
) -> pd.DataFrame:
    """Annotate demand levels for a benchmark dataset.

    This is the main entry point for demand-level annotation. It:
    1. Loads rubrics
    2. Builds prompts for each instance × demand
    3. Sends them to the LLM (via batch or direct calls)
    4. Parses results into a DataFrame

    Args:
        data:           DataFrame with at least ``prompt`` and ``custom_id``
                        columns (as produced by ``adele.data.load_benchmark``).
        demands:        List of rubric acronyms to annotate (e.g. ["AS", "MCr"]).
                        If None, annotates all available rubrics.
        rubrics_folder: Path to custom rubrics folder. None = bundled rubrics.
        model:          Model to use for annotation. Supports any model that
                        litellm supports:

                        - OpenAI: ``"gpt-4o"``, ``"gpt-4o-mini"``
                        - Gemini: ``"gemini/gemini-2.0-flash"``
                        - Claude: ``"claude-sonnet-4-20250514"``
                        - Any litellm-supported model string.
        backend:        ``"batch"`` (OpenAI Batch API) or ``"direct"``
                        (litellm, any provider). If None, auto-detects:
                        uses ``"batch"`` for OpenAI models, ``"direct"``
                        for everything else.
        max_completion_tokens: Max tokens per response.
        api_key:        API key (for OpenAI batch mode). For other
                        providers, set the standard env variable
                        (GOOGLE_API_KEY, ANTHROPIC_API_KEY, etc.).
        output_dir:     Directory to save batch input/output files.
        poll_interval:  Seconds between status checks (batch mode only).
        max_concurrent: Max concurrent requests (direct mode only).
        batch_chunk_size: Max requests per batch job (batch mode only); each
                        demand is split into chunks of this size to stay under
                        the OpenAI Batch API's 50,000-request limit.
        format:         Output format: ``"wide"`` (one row per instance)
                        or ``"long"`` (one row per instance×demand).

    Returns:
        DataFrame with annotation results. In "wide" format, columns are:
        ``custom_id, AS, AT, CEc, ...`` (one column per demand).
    """
    # Validate input
    for col in ("prompt", "custom_id"):
        if col not in data.columns:
            raise ValueError(f"Input data must have a '{col}' column.")

    # Load rubrics
    catalog = RubricsCatalog(rubrics_folder)
    if demands is None:
        demands = catalog.acronyms
    else:
        for d in demands:
            if d not in catalog:
                raise ValueError(
                    f"Rubric '{d}' not found. Available: {catalog.acronyms}"
                )

    # Auto-detect backend
    if backend is None:
        backend = "batch" if _is_openai_model(model) else "direct"

    logger.info(
        "Annotating %d instances × %d demands (%d total requests) "
        "using model=%s, backend=%s",
        len(data), len(demands), len(data) * len(demands),
        model, backend,
    )

    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    if backend == "batch":
        result_df = _annotate_batch(
            data=data,
            catalog=catalog,
            demands=demands,
            model=model,
            max_completion_tokens=max_completion_tokens,
            api_key=api_key,
            output_path=output_path,
            poll_interval=poll_interval,
            chunk_size=batch_chunk_size,
        )
    elif backend == "direct":
        result_df = _annotate_direct(
            data=data,
            catalog=catalog,
            demands=demands,
            model=model,
            max_completion_tokens=max_completion_tokens,
            output_path=output_path,
            max_concurrent=max_concurrent,
        )
    else:
        raise ValueError(
            f"Unknown backend '{backend}'. Use 'batch' or 'direct'."
        )

    # Surface silent partial failures: a batch job that failed/expired (or a
    # provider error in every direct call) yields a result with whole demands
    # missing or all-NaN, which otherwise looks like a successful run.
    if "demand" in result_df.columns:
        present = set(result_df["demand"].unique())
        missing = [d for d in demands if d not in present]
        if missing:
            logger.warning(
                "No annotations returned for %d/%d demands: %s "
                "(batch jobs may have failed/expired, or all requests errored)",
                len(missing), len(demands), missing,
            )
    if "level" in result_df.columns and result_df["level"].notna().sum() == 0:
        logger.error(
            "All %d annotation requests failed — 0 valid levels extracted. "
            "Check the model name and API credentials.", len(result_df),
        )

    if format == "wide":
        result_df = to_wide_format(result_df)

    # Save results
    result_path = output_path / f"annotations_{format}.csv"
    result_df.to_csv(result_path, index=False)
    logger.info("Annotations saved to %s", result_path)

    return result_df


# ============================================================================
# Backend: Direct (any model via litellm)
# ============================================================================

def _annotate_direct(
    data: pd.DataFrame,
    catalog: RubricsCatalog,
    demands: List[str],
    model: str,
    max_completion_tokens: int,
    output_path: Path,
    max_concurrent: int = 10,
) -> pd.DataFrame:
    """Annotate using direct API calls via litellm (parallelized).

    Works with any model provider (OpenAI, Google, Anthropic, etc.).
    """
    import litellm
    from concurrent.futures import ThreadPoolExecutor, as_completed
    from adele.annotation.parsing import extract_demand_level

    # Flatten the workload: (row_data, demand_acronym) tuples
    work_items = []
    for acronym in demands:
        rubric = catalog[acronym]
        for _, row in data.iterrows():
            work_items.append({
                "row": row,
                "acronym": acronym,
                "rubric": rubric,
            })

    results = []
    total = len(work_items)

    def _process_item(item):
        row = item["row"]
        acronym = item["acronym"]
        rubric = item["rubric"]

        prompt = build_annotation_prompt(
            demand_name=rubric.full_name,
            rubric_content=rubric.content,
            task_instance=row["prompt"],
        )

        completion_kwargs = dict(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_completion_tokens,
        )
        # Reasoning models (o1/o3/o4…) reject a non-default temperature.
        if not is_reasoning_model(model):
            completion_kwargs["temperature"] = 0.0

        try:
            response = litellm.completion(**completion_kwargs)
            content = response.choices[0].message.content or ""
        except Exception as exc:
            logger.warning(
                "Request failed for %s × %s: %s",
                row["custom_id"], acronym, exc,
            )
            content = ""

        level, ok = extract_demand_level(content)
        return {
            "custom_id": row["custom_id"],
            "demand": acronym,
            "level": level,
            "valid": ok,
            "response": content,
        }

    logger.info("Starting %d parallel requests (max_concurrent=%d)", total, max_concurrent)

    with ThreadPoolExecutor(max_workers=max_concurrent) as executor:
        futures = {executor.submit(_process_item, item): item for item in work_items}
        
        with tqdm(total=total, desc="Annotating", unit="req") as pbar:
            for future in as_completed(futures):
                results.append(future.result())
                pbar.update(1)

    # Save raw responses
    raw_path = output_path / "raw_responses.jsonl"
    with open(raw_path, "w") as f:
        for r in results:
            f.write(json.dumps(r, default=str) + "\n")

    return pd.DataFrame(results)


# ============================================================================
# Backend: OpenAI Batch API
# ============================================================================

def _annotate_batch(
    data: pd.DataFrame,
    catalog: RubricsCatalog,
    demands: List[str],
    model: str,
    max_completion_tokens: int,
    api_key: Optional[str],
    output_path: Path,
    poll_interval: int,
    chunk_size: int = 50000,
) -> pd.DataFrame:
    """Annotate using the OpenAI Batch API (50% cheaper, higher limits)."""
    # Strip "openai/" prefix if present
    bare_model = model.split("/", 1)[-1] if "/" in model else model

    client = openai.OpenAI(api_key=api_key)

    # Step 1: Build batch input files (one per demand × chunk)
    input_files = _create_input_files(
        data=data,
        catalog=catalog,
        demands=demands,
        model=bare_model,
        max_completion_tokens=max_completion_tokens,
        output_dir=output_path,
        chunk_size=chunk_size,
    )

    # Step 2: Upload and launch batch jobs
    batch_jobs = _launch_jobs(client, input_files)

    # Step 3: Poll until complete
    _wait_for_completion(client, batch_jobs, poll_interval=poll_interval)

    # Step 4: Download results
    output_files = _download_results(client, batch_jobs, output_path)

    # Step 5: Parse results
    return parse_multiple_outputs(output_files)


def _create_input_files(
    data: pd.DataFrame,
    catalog: RubricsCatalog,
    demands: List[str],
    model: str,
    max_completion_tokens: int,
    output_dir: Path,
    chunk_size: int = 50000,
) -> dict[str, Path]:
    """Create batch input JSONL files, one per (demand, chunk).

    The OpenAI Batch API caps a single job at 50,000 requests, so each demand's
    requests are split into chunks of at most ``chunk_size`` rows. The chunk's
    demand is recovered from each request's ``custom_id`` at parse time, so the
    extra files are transparent downstream.
    """
    input_files = {}
    n = len(data)

    for acronym in demands:
        rubric = catalog[acronym]
        for ci, start in enumerate(range(0, n, chunk_size)):
            chunk = data.iloc[start:start + chunk_size]
            # Keep the single-chunk filename identical to the old behavior.
            label = acronym if n <= chunk_size else f"{acronym}_{ci}"
            file_path = output_dir / f"input_{label}.jsonl"

            with open(file_path, "w", encoding="utf-8") as f:
                for _, row in chunk.iterrows():
                    prompt = build_annotation_prompt(
                        demand_name=rubric.full_name,
                        rubric_content=rubric.content,
                        task_instance=row["prompt"],
                    )
                    request = build_batch_request(
                        custom_id=row["custom_id"],
                        demand_acronym=acronym,
                        prompt=prompt,
                        model=model,
                        max_completion_tokens=max_completion_tokens,
                    )
                    f.write(json.dumps(request) + "\n")

            logger.info("Created input file: %s (%d requests)", file_path.name, len(chunk))
            input_files[label] = file_path

    return input_files


@_retry_openai
def _upload_and_launch(client: openai.OpenAI, input_file: Path) -> str:
    """Upload a JSONL file and create a batch job."""
    with open(input_file, "rb") as f:
        batch_file = client.files.create(file=f, purpose="batch")

    batch_job = client.batches.create(
        input_file_id=batch_file.id,
        endpoint="/v1/chat/completions",
        completion_window="24h",
    )

    logger.info("Launched batch job %s for %s", batch_job.id, input_file.name)
    return batch_job.id


def _launch_jobs(
    client: openai.OpenAI,
    input_files: dict[str, Path],
) -> dict[str, str]:
    """Launch batch jobs for all input files."""
    jobs = {}
    for acronym, file_path in input_files.items():
        job_id = _upload_and_launch(client, file_path)
        jobs[acronym] = job_id
    logger.info("Launched %d batch jobs", len(jobs))
    return jobs


@_retry_openai
def _check_status(client: openai.OpenAI, batch_id: str) -> str:
    """Check the status of a batch job."""
    batch = client.batches.retrieve(batch_id)
    return batch.status


def _wait_for_completion(
    client: openai.OpenAI,
    jobs: dict[str, str],
    poll_interval: int = 60,
):
    """Poll batch jobs until all are completed or failed."""
    pending = set(jobs.keys())

    while pending:
        for acronym in list(pending):
            status = _check_status(client, jobs[acronym])

            if status == "completed":
                logger.info("✓ Batch job for %s completed", acronym)
                pending.discard(acronym)
            elif status in ("failed", "expired", "cancelled"):
                logger.error("✗ Batch job for %s: %s", acronym, status)
                pending.discard(acronym)
            else:
                logger.debug("  Batch job for %s: %s", acronym, status)

        if pending:
            logger.info(
                "Waiting for %d/%d jobs... (checking again in %ds)",
                len(pending), len(jobs), poll_interval,
            )
            time.sleep(poll_interval)


@_retry_openai
def _download_result(
    client: openai.OpenAI,
    batch_id: str,
    output_path: Path,
    acronym: str,
) -> Optional[Path]:
    """Download the result of a completed batch job."""
    batch = client.batches.retrieve(batch_id)

    if not batch.output_file_id:
        logger.warning("No output file for batch %s (%s)", batch_id, acronym)
        return None

    content = client.files.content(batch.output_file_id).content
    result_file = output_path / f"output_{acronym}.jsonl"
    result_file.write_bytes(content)
    logger.info("Downloaded results to %s", result_file.name)
    return result_file


def _download_results(
    client: openai.OpenAI,
    jobs: dict[str, str],
    output_path: Path,
) -> List[Path]:
    """Download results for all completed batch jobs."""
    files = []
    for acronym, batch_id in jobs.items():
        result = _download_result(client, batch_id, output_path, acronym)
        if result:
            files.append(result)
    return files
