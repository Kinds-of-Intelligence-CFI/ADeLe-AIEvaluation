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


def _taubench_prompt(domain: str, instr) -> str:
    """Render a τ-bench user scenario into the task an agent must satisfy.

    Handles both scenario shapes in the wild: a structured dict
    (airline/retail/telecom) and a plain narrative string (banking_knowledge).
    """
    header = f"[τ-bench: {domain}] A customer-service agent must assist a user."
    if isinstance(instr, str):
        return header + "\n" + instr.strip()
    parts = [header]
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


TAU2_DOMAINS = ("airline", "retail", "telecom", "banking_knowledge")


def _load_taubench(local_repo: Optional[str] = None,
                   domains: tuple = TAU2_DOMAINS) -> pd.DataFrame:
    """τ-bench user scenarios for all public domains.

    Reads ``data/tau2/domains/<domain>/tasks.json`` from a local checkout of
    sierra-research/tau2-bench when ``local_repo`` (or the TAU2_REPO env var)
    is set — the repo carries ALL domains including banking_knowledge, which
    the HF mirror lacks — else falls back to the HF mirror (airline/retail).
    """
    import os
    local_repo = local_repo or os.environ.get("TAU2_REPO")
    prompts, source_ids = [], []
    if local_repo:
        base = os.path.join(local_repo, "data", "tau2", "domains")
        for domain in domains:
            path = os.path.join(base, domain, "tasks.json")
            if not os.path.exists(path):
                continue
            with open(path, encoding="utf-8") as f:
                tasks = json.load(f)
            for t in tasks:
                instr = t.get("user_scenario", {}).get("instructions", {})
                prompts.append(_taubench_prompt(domain, instr))
                source_ids.append(f"{domain}/{t.get('id', '')}")
    else:
        from huggingface_hub import hf_hub_download
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


def _pick_columns(df: pd.DataFrame, wanted: Dict[str, List[str]], where: str) -> Dict[str, str]:
    """Resolve each wanted role ('id', 'prompt') to the first matching column.

    Kept schema-defensive because several 2026 sources ship without stable,
    documented column names; failing loudly with the observed columns beats a
    silently wrong ingest.
    """
    picked = {}
    for role, candidates in wanted.items():
        col = next((c for c in candidates if c in df.columns), None)
        if col is None:
            raise ValueError(
                f"{where}: no {role} column among candidates {candidates}; "
                f"dataset has columns {list(df.columns)} — update the loader."
            )
        picked[role] = col
    return picked


def _load_terminal_bench() -> pd.DataFrame:
    """Terminal-Bench 2.0 task instructions (harborframework/terminal-bench-2.0).

    The tasks (not run logs) — one instruction per task; task ids join against
    Terminal-Bench leaderboard results.
    """
    from datasets import load_dataset
    ds = load_dataset("harborframework/terminal-bench-2.0", split="train").to_pandas()
    cols = _pick_columns(ds, {
        "id": ["task_id", "id", "name", "task_name"],
        "prompt": ["instruction", "task", "prompt", "description", "task_description"],
    }, "terminal-bench-2.0")
    return _frame(ds[cols["prompt"]].astype(str).tolist(),
                  ds[cols["id"]].astype(str).tolist(), "terminalbench", "tb")


def _load_aime() -> pd.DataFrame:
    """AIME 2025+2026 problem statements (MathArena problem sets).

    Problem indices join against MathArena/aime_*_outputs per-instance results.
    """
    from datasets import load_dataset
    frames = []
    for year, repo in (("2025", "MathArena/aime_2025"), ("2026", "MathArena/aime_2026")):
        ds = load_dataset(repo, split="train").to_pandas()
        cols = _pick_columns(ds, {
            "id": ["problem_idx", "id", "problem_id"],
            "prompt": ["problem", "question", "problem_statement"],
        }, repo)
        frames.append(pd.DataFrame({
            "prompt": ds[cols["prompt"]].astype(str),
            "source_id": year + "/" + ds[cols["id"]].astype(str),
        }))
    both = pd.concat(frames, ignore_index=True)
    return _frame(both["prompt"].tolist(), both["source_id"].tolist(), "aime", "aime")


BENCH_LOADERS: Dict[str, Callable[[], pd.DataFrame]] = {
    "swebench": _load_swebench,
    "assistantbench": _load_assistantbench,
    "usaco": _load_usaco,
    "taubench": _load_taubench,
    "terminalbench": _load_terminal_bench,
    "aime": _load_aime,
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
