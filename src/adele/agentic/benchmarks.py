"""Whole-task ingest for a small cross-benchmark validation pilot.

Pulls task *inputs* (not rollouts) for four HAL benchmarks and draws a seeded
random sample, so one annotator can hand-label a diverse set and we can compute
judge-vs-human agreement across benchmarks. Each loader returns a frame with
``custom_id, prompt, benchmark, source_id``; ``custom_id`` is positional and
contains no ``__`` (the annotator appends ``__<demand>``), so it stays a safe
join key.

Sources (verified May 2026):
  - swebench       princeton-nlp/SWE-bench_Verified [test]      problem_statement
  - assistantbench AssistantBench/AssistantBench    [validation] task
  - usaco          rStar-Reasoning/usaco_2025       [test]       description
  - taubench       HuggingFaceH4/tau2-bench-data    domains/*/tasks.json (user goal)

τ-bench has no static prompt (it's an interactive user simulation), so we
annotate the *user scenario* the agent must satisfy.
"""

import json
from typing import Callable, Dict, List, Optional

import pandas as pd


def _frame(prompts: List[str], source_ids: List[str], benchmark: str, prefix: str) -> pd.DataFrame:
    """Assemble a loader frame with positional, ``__``-free custom_ids."""
    return pd.DataFrame({
        "custom_id": [f"{prefix}-{i:04d}" for i in range(len(prompts))],
        "prompt": prompts,
        "benchmark": benchmark,
        "source_id": source_ids,
    })


def _load_swebench() -> pd.DataFrame:
    from datasets import load_dataset
    ds = load_dataset("princeton-nlp/SWE-bench_Verified", split="test")
    ds = ds.select_columns(["instance_id", "problem_statement"]).to_pandas()
    return _frame(ds["problem_statement"].tolist(), ds["instance_id"].tolist(), "swebench", "swe")


def _load_assistantbench() -> pd.DataFrame:
    from datasets import load_dataset
    # validation is the public split that carries the task text.
    ds = load_dataset("AssistantBench/AssistantBench", split="validation")
    ds = ds.select_columns(["id", "task"]).to_pandas()
    return _frame(ds["task"].tolist(), ds["id"].tolist(), "assistantbench", "ab")


def _load_usaco() -> pd.DataFrame:
    from datasets import load_dataset
    # Heavy file (test blobs live in other columns); select first to stay light.
    ds = load_dataset("rStar-Reasoning/usaco_2025", split="test")
    ds = ds.select_columns(["name", "description"]).to_pandas()
    return _frame(ds["description"].tolist(), ds["name"].tolist(), "usaco", "usaco")


def _taubench_prompt(domain: str, instr: dict) -> str:
    """Render a τ-bench user scenario into the task an agent must satisfy."""
    parts = [f"[τ-bench: {domain}] A customer-service agent must assist a user."]
    for label, key in (
        ("Reason for the call", "reason_for_call"),
        ("Known information", "known_info"),
        ("Unknown information", "unknown_info"),
        ("What the user wants", "task_instructions"),
    ):
        val = (instr or {}).get(key)
        if val:
            parts.append(f"{label}: {val}")
    return "\n".join(parts)


def _load_taubench() -> pd.DataFrame:
    from huggingface_hub import hf_hub_download
    prompts, source_ids = [], []
    for domain in ("airline", "retail"):
        path = hf_hub_download(
            "HuggingFaceH4/tau2-bench-data",
            f"domains/{domain}/tasks.json",
            repo_type="dataset",
        )
        with open(path, encoding="utf-8") as f:
            tasks = json.load(f)
        for t in tasks:
            instr = t.get("user_scenario", {}).get("instructions", {})
            prompts.append(_taubench_prompt(domain, instr))
            source_ids.append(f"{domain}/{t.get('id', '')}")
    return _frame(prompts, source_ids, "taubench", "tau")


BENCH_LOADERS: Dict[str, Callable[[], pd.DataFrame]] = {
    "swebench": _load_swebench,
    "assistantbench": _load_assistantbench,
    "usaco": _load_usaco,
    "taubench": _load_taubench,
}


def sample_pilot(
    benchmarks: List[str],
    *,
    n_per: int = 5,
    seed: int = 0,
    loaders: Optional[Dict[str, Callable[[], pd.DataFrame]]] = None,
) -> pd.DataFrame:
    """Draw a seeded random sample of ``n_per`` tasks from each benchmark.

    Returns a concatenated frame (``custom_id, prompt, benchmark, source_id``).
    Reproducible: the same ``seed`` + dataset versions give the same rows.
    """
    loaders = loaders or BENCH_LOADERS
    frames = []
    for name in benchmarks:
        if name not in loaders:
            raise ValueError(f"Unknown benchmark '{name}'. Known: {sorted(loaders)}")
        full = loaders[name]()
        frames.append(full.sample(n=min(n_per, len(full)), random_state=seed))
    return pd.concat(frames, ignore_index=True)
