"""Prepare frozen, validated instance sets for (expensive) demand annotation.

The annotation run is the costly, hard-to-repeat step of the pipeline, so the
instances it consumes are treated like the rubrics: canonicalized, validated,
content-hashed and manifest-frozen *before* any judge call is made.

What `prepare()` guarantees:

1. **Canonical join keys.** Loader output (`adele.agentic.benchmarks`) uses
   loader-local names ("swebench", source_id "2025/3"); public results
   (`adele.results`) use canonical slugs ("swe-bench-verified", "aime-2025").
   Canonicalization happens HERE, once, so annotations and success flags join
   by (benchmark, instance_id) with no ad-hoc renaming at analysis time.
2. **Validation before spend.** Duplicate ids, empty/degenerate prompts and
   near-duplicate prompts fail or warn now, not after 5k judge calls.
3. **Reproducibility.** Each benchmark file is content-hashed into
   ``INSTANCES.tsv``; an annotation run records which manifest it consumed, so
   "which exact task text was judged" has a permanent answer.
4. **Cost visibility.** Token/cost estimates per benchmark × dimension count
   are printed before anything is spent.
"""

import hashlib
import logging
from pathlib import Path
from typing import Callable, Dict, Iterable, List, Optional, Tuple

import pandas as pd

logger = logging.getLogger(__name__)

INSTANCE_COLUMNS = ["benchmark", "instance_id", "prompt"]
MANIFEST_NAME = "INSTANCES.tsv"

# Overhead per judge call besides the task text itself (rubric + CoT scaffold),
# measured from build_annotation_prompt with a typical v2 rubric: ~7k chars.
_RUBRIC_PROMPT_CHARS = 7000
_CHARS_PER_TOKEN = 4.0
_TYPICAL_COMPLETION_TOKENS = 400

# Prompts beyond this are flagged: they still fit judge contexts, but cost and
# attention dilution grow; consider a documented truncation decision instead.
LONG_PROMPT_CHARS = 24_000


def _split_aime(row: pd.Series) -> Tuple[str, str]:
    year, _, idx = str(row["source_id"]).partition("/")
    return f"aime-{year}", idx


def _split_tau(row: pd.Series) -> Tuple[str, str]:
    domain, _, tid = str(row["source_id"]).partition("/")
    return f"tau2-{domain}", tid


# loader name -> (fn(row) -> (canonical_benchmark, instance_id))
CANONICALIZERS: Dict[str, Callable[[pd.Series], Tuple[str, str]]] = {
    "swebench": lambda r: ("swe-bench-verified", str(r["source_id"])),
    "terminalbench": lambda r: ("terminal-bench-2.0", str(r["source_id"])),
    "aime": _split_aime,
    "taubench": _split_tau,
    "usaco": lambda r: ("usaco", str(r["source_id"])),
    "assistantbench": lambda r: ("assistantbench", str(r["source_id"])),
}


def canonicalize(loader_name: str, frame: pd.DataFrame) -> pd.DataFrame:
    """Map a loader frame to the canonical (benchmark, instance_id, prompt)."""
    fn = CANONICALIZERS.get(loader_name)
    if fn is None:
        raise ValueError(
            f"no canonicalizer for loader '{loader_name}' — add one to "
            f"adele.instances.CANONICALIZERS (known: {sorted(CANONICALIZERS)})"
        )
    pairs = frame.apply(fn, axis=1, result_type="expand")
    out = pd.DataFrame({
        "benchmark": pairs[0],
        "instance_id": pairs[1],
        "prompt": frame["prompt"].astype(str),
    })
    out["prompt_sha12"] = out["prompt"].map(
        lambda t: hashlib.sha256(t.encode()).hexdigest()[:12])
    return out


def validate_instances(df: pd.DataFrame, *, where: str = "") -> List[str]:
    """Hard-fail on unusable data; return a list of soft warnings."""
    missing = [c for c in INSTANCE_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"{where}: missing columns {missing}")
    if len(df) == 0:
        raise ValueError(f"{where}: empty instance frame")
    dupes = df.duplicated(subset=["benchmark", "instance_id"])
    if dupes.any():
        raise ValueError(
            f"{where}: {int(dupes.sum())} duplicate (benchmark, instance_id) "
            f"rows, e.g. {df.loc[dupes, 'instance_id'].head(3).tolist()}"
        )
    empty = df["prompt"].str.strip().str.len() < 20
    if empty.any():
        raise ValueError(
            f"{where}: {int(empty.sum())} prompts shorter than 20 chars "
            f"(ids: {df.loc[empty, 'instance_id'].head(3).tolist()})"
        )
    warnings = []
    long = df["prompt"].str.len() > LONG_PROMPT_CHARS
    if long.any():
        warnings.append(
            f"{int(long.sum())} prompts exceed {LONG_PROMPT_CHARS} chars "
            f"(max {int(df['prompt'].str.len().max())}); consider a truncation decision"
        )
    text_dupes = df.duplicated(subset=["prompt"])
    if text_dupes.any():
        warnings.append(f"{int(text_dupes.sum())} instances share identical prompt text")
    return warnings


def estimate_cost(
    df: pd.DataFrame,
    *,
    n_dimensions: int,
    usd_per_mtok_in: Optional[float] = None,
    usd_per_mtok_out: Optional[float] = None,
) -> Dict[str, float]:
    """Tokens (and, given rates, dollars) for judging this frame once."""
    calls = len(df) * n_dimensions
    tokens_in = float(
        ((df["prompt"].str.len() + _RUBRIC_PROMPT_CHARS) / _CHARS_PER_TOKEN).sum()
    ) * n_dimensions
    tokens_out = float(calls * _TYPICAL_COMPLETION_TOKENS)
    out = {"calls": float(calls), "tokens_in": tokens_in, "tokens_out": tokens_out}
    if usd_per_mtok_in is not None and usd_per_mtok_out is not None:
        out["usd"] = tokens_in / 1e6 * usd_per_mtok_in + tokens_out / 1e6 * usd_per_mtok_out
    return out


def _frame_sha256(df: pd.DataFrame) -> str:
    canon = df.sort_values(["benchmark", "instance_id"])[INSTANCE_COLUMNS]
    return hashlib.sha256(canon.to_csv(index=False).encode()).hexdigest()


def prepare(
    loader_names: Iterable[str],
    out_dir: str | Path,
    *,
    loaders: Optional[Dict[str, Callable[[], pd.DataFrame]]] = None,
    n_dimensions: int = 7,
    sample: Optional[int] = None,
    seed: int = 0,
    fmt: str = "parquet",
) -> pd.DataFrame:
    """Run loaders, canonicalize, validate, freeze to parquet + manifest.

    Returns the manifest frame. Files written to ``out_dir``:
    ``instances_<slug>.parquet`` per canonical benchmark, plus ``INSTANCES.tsv``.
    """
    if loaders is None:
        from adele.agentic.benchmarks import BENCH_LOADERS
        loaders = BENCH_LOADERS
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    manifest_rows = []
    for name in loader_names:
        if name not in loaders:
            raise ValueError(f"unknown loader '{name}' (known: {sorted(loaders)})")
        raw = loaders[name]()
        df = canonicalize(name, raw)
        if sample is not None and sample < len(df):
            df = (
                df.groupby("benchmark", group_keys=False)
                .apply(lambda g: g.sample(min(sample, len(g)), random_state=seed))
                .reset_index(drop=True)
            )
        for slug, part in df.groupby("benchmark"):
            part = part.reset_index(drop=True)
            warnings = validate_instances(part, where=slug)
            for w in warnings:
                logger.warning("%s: %s", slug, w)
            est = estimate_cost(part, n_dimensions=n_dimensions)
            path = out / f"instances_{slug}.{fmt}"
            if fmt == "parquet":
                part.to_parquet(path)   # needs pyarrow (ships with the [annotate] extra)
            else:
                part.to_csv(path, index=False)
            manifest_rows.append({
                "benchmark": slug,
                "n_instances": len(part),
                "sha256": _frame_sha256(part),
                "loader": name,
                "median_prompt_chars": int(part["prompt"].str.len().median()),
                "max_prompt_chars": int(part["prompt"].str.len().max()),
                "est_calls": int(est["calls"]),
                "est_tokens_in": int(est["tokens_in"]),
                "warnings": "; ".join(warnings) or "-",
                "file": path.name,
            })
    manifest = pd.DataFrame(manifest_rows)
    manifest.to_csv(out / MANIFEST_NAME, sep="\t", index=False)
    logger.info("froze %d benchmarks (%d instances, ~%.1fM input tokens for %d dims) → %s",
                len(manifest), manifest["n_instances"].sum(),
                manifest["est_tokens_in"].sum() / 1e6, n_dimensions, out)
    return manifest


def check_join(instances_dir: str | Path, results_parquet: str | Path) -> pd.DataFrame:
    """Report, per benchmark, how instance ids match the results matrix.

    Run this BEFORE annotating: a low match rate means canonicalization is
    wrong somewhere, and money spent on annotation would not join.
    """
    inst_dir = Path(instances_dir)
    rp = Path(results_parquet)
    results = (pd.read_parquet(rp) if rp.suffix == ".parquet"
               else pd.read_csv(rp, dtype={"instance_id": str}))
    rows = []
    files = sorted(inst_dir.glob("instances_*.parquet")) + sorted(inst_dir.glob("instances_*.csv"))
    for f in files:
        inst = pd.read_parquet(f) if f.suffix == ".parquet" else pd.read_csv(
            f, dtype={"instance_id": str})
        slug = inst["benchmark"].iloc[0]
        res_ids = set(results.loc[results["benchmark"] == slug, "instance_id"].astype(str))
        ids = set(inst["instance_id"].astype(str))
        rows.append({
            "benchmark": slug,
            "instances": len(ids),
            "in_results_matrix": len(ids & res_ids),
            "match_rate": round(len(ids & res_ids) / len(ids), 3) if ids else 0.0,
            "results_side_ids": len(res_ids),
        })
    report = pd.DataFrame(rows)
    for _, r in report.iterrows():
        if 0 < r["results_side_ids"] and r["match_rate"] < 0.9:
            logger.warning(
                "%s: only %.0f%% of instance ids join the results matrix — "
                "check canonicalization before spending on annotation",
                r["benchmark"], 100 * r["match_rate"],
            )
    return report


def unique_prompt_view(df: pd.DataFrame) -> pd.DataFrame:
    """One row per distinct prompt text — the frame to actually ANNOTATE.

    Some benchmarks (τ³ telecom: 2,285 tasks, ~5 scenario texts) vary only in
    hidden environment state, which task-text annotation cannot see; judging
    each duplicate separately would multiply cost for identical output. The
    returned frame uses ``prompt_sha12`` as ``instance_id`` (and custom_id);
    expand judgements back over the full set with :func:`propagate_labels`.
    """
    view = (
        df.sort_values(["benchmark", "instance_id"])
        .groupby(["benchmark", "prompt_sha12"], as_index=False)
        .agg(prompt=("prompt", "first"), n_duplicates=("instance_id", "size"),
             example_instance_id=("instance_id", "first"))
    )
    view["instance_id"] = view["prompt_sha12"]
    return view[["benchmark", "instance_id", "prompt", "n_duplicates",
                 "example_instance_id", "prompt_sha12"]]


def propagate_labels(labels: pd.DataFrame, instances: pd.DataFrame) -> pd.DataFrame:
    """Expand unique-prompt judge labels back to every original instance.

    Args:
        labels: wide frame keyed by ``custom_id`` == ``prompt_sha12`` (the
            output of judging :func:`unique_prompt_view`).
        instances: the frozen full instance frame (with ``prompt_sha12``).
    Returns: one row per original instance with the demand columns attached.
    """
    if "custom_id" in labels.columns and "prompt_sha12" not in labels.columns:
        labels = labels.rename(columns={"custom_id": "prompt_sha12"})
    out = instances.merge(labels, on="prompt_sha12", how="left",
                          suffixes=("", "_label"))
    missing = out[[c for c in labels.columns if c != "prompt_sha12"]].isna().all(axis=1)
    if missing.any():
        logger.warning("propagate_labels: %d instances have no matching judged prompt",
                       int(missing.sum()))
    return out.drop(columns=["prompt"], errors="ignore")
