"""Pin the two runs of natural-prompt (PREREGISTRATION.md).

  np-gate-opuslow  Opus low (adele-judge-v2-low) on the 132 cells of swebench-pl's gate: 44 SWE-bench
                   Verified tasks x PLp, PLe, PLs. The same judge's labels under the old prompt are
                   swebench-pl/labels/swepl-gate-low.
  np-plp-s55h      Sonnet 5.5 high (adele-judge-v2-high) on the 44 PLp cells of the gate: the 23 that
                   Sonnet 5.5's safeguards blocked twice under the old prompt, and the 21 it answered.

For every cell, the old prompt is rebuilt from the rubric (as the catalog loads it) and the task text, and
must match swepl-gate's prompt hash. The natural prompt is then built from the same inputs, so only the
prompt's own wording differs.

    python experiments/benchmarks/natural-prompt/make_runs.py
"""

import hashlib
import importlib.util
import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from adele.agentic import load_active_catalog
from adele.annotation.prompts import build_annotation_prompt

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BENCH = HERE.parent
JUDGE_IO = ROOT.parents[1] / "judge-io"
INSTRUCTION = "Prompt file: {prompt_file}\nResponse file: {response_file}"
RUNS = {
    "np-gate-opuslow": {
        "dims": ["PLp", "PLe", "PLs"], "agent": "adele-judge-v2-low.md",
        "judges": {"opus-low": "Claude Code subagent 'adele-judge-v2-low' (tools: Read, Write; omitClaudeMd; "
                               "effort low), model alias 'opus'"}},
    "np-plp-s55h": {
        "dims": ["PLp"], "agent": "adele-judge-v2-high.md",
        "judges": {"sonnet55-high": "Claude Code subagent 'adele-judge-v2-high' (tools: Read, Write; omitClaudeMd; "
                                    "effort high), model alias 'sonnet' (claude-sonnet-5-5 on 2026-09-29)"}},
}


def sha256(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def git(*args: str) -> str:
    return subprocess.run(["git", "-C", str(ROOT), *args], capture_output=True, text=True, check=True).stdout.strip()


def load_prompt_module():
    spec = importlib.util.spec_from_file_location("natural_prompt", HERE / "prompt.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main() -> None:
    natural = load_prompt_module().build_natural_prompt
    gate = pd.read_csv(BENCH / "swebench-pl/labels/swepl-gate/prompts_index.csv", dtype={"instance_id": str})
    inst = pd.read_parquet(ROOT / "data/instances/instances_swe-bench-verified.parquet").set_index("instance_id")
    catalog = load_active_catalog()
    for run_id, spec in RUNS.items():
        io, labels = JUDGE_IO / run_id, HERE / "labels" / run_id
        for d in [io / "prompts", labels] + [io / "responses" / j for j in spec["judges"]]:
            d.mkdir(parents=True, exist_ok=True)
        rows = []
        for r in gate[gate["demand"].isin(spec["dims"])].itertuples(index=False):
            rubric, text = catalog[r.demand], inst.loc[r.instance_id, "prompt"]
            assert sha256(Path(rubric.file_path).read_bytes()) == r.rubric_sha256, f"{r.demand}: rubric changed"
            old = build_annotation_prompt(demand_name=rubric.full_name, rubric_content=rubric.content, task_instance=text)
            assert sha256(old.encode("utf-8")) == r.prompt_sha256, f"{r.instance_id}@{r.demand}: inputs differ"
            new = natural(rubric.full_name, rubric.content, text)
            (io / "prompts" / f"{r.instance_id}@{r.demand}.txt").write_text(new, encoding="utf-8")
            rows.append({"benchmark": "swe-bench-verified", "instance_id": r.instance_id, "file_id": r.instance_id,
                         "demand": r.demand, "family": r.family, "old_prompt_sha256": r.prompt_sha256,
                         "prompt_sha256": sha256(new.encode("utf-8"))})
        pd.DataFrame(rows).to_csv(labels / "prompts_index.csv", index=False)
        agent = HERE / spec["agent"]
        run = {
            "run_id": run_id,
            "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "repo_commit": git("rev-parse", "HEAD"),
            "repo_dirty_tracked_files": git("status", "--porcelain", "--untracked-files=no").splitlines(),
            "benchmark": ["swe-bench-verified"],
            "design": {"n_tasks": len({r["instance_id"] for r in rows}), "dims": spec["dims"], "n_prompts": len(rows),
                       "judges": spec["judges"]},
            "prompt": {"builder": "natural-prompt/prompt.py:build_natural_prompt",
                       "builder_file_sha256": sha256((HERE / "prompt.py").read_bytes()),
                       "inputs_checked_against": "swebench-pl/labels/swepl-gate (old prompt rebuilt, hashes equal)"},
            "judge_agent": {"file": str(agent.relative_to(ROOT)), "sha256": sha256(agent.read_bytes())},
            "judge_instruction": INSTRUCTION,
            "judge_instruction_sha256": sha256(INSTRUCTION.encode("utf-8")),
            "judge_io": os.path.relpath(io, ROOT),
            "sampling": "harness defaults; snapshot cannot be pinned for subagents; effort is set in the agent file",
        }
        (labels / "run.json").write_text(json.dumps(run, indent=2) + "\n")
        print(f"{run_id}: {len(rows)} prompts")


if __name__ == "__main__":
    main()
