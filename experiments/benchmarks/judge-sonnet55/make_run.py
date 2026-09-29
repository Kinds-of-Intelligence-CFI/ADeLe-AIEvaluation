"""Pin run s55h-gate of judge-sonnet55 (PREREGISTRATION.md).

Sonnet 5.5 at high effort judges the PLp and PLe cells of swebench-pl's gate (44 SWE-bench Verified
tasks). The prompts are copied byte for byte from the gate run swepl-gate (Opus 5.5 at medium effort),
and each copy is checked against that run's prompt hash, so only the judge differs.

    python experiments/benchmarks/judge-sonnet55/make_run.py
"""

import hashlib
import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
JUDGE_IO = ROOT.parents[1] / "judge-io"
SRC = "swepl-gate"
RUN = "s55h-gate"
DIMS = ["PLp", "PLe"]
AGENT = HERE / "adele-judge-high.md"
JUDGES = {"sonnet55-high": "Claude Code subagent 'adele-judge-high' (tools: Read, Write; omitClaudeMd; effort high), "
                           "model alias 'sonnet', which gave claude-sonnet-5-5 in a probe on 2026-09-29"}
INSTRUCTION = "Prompt file: {prompt_file}\nResponse file: {response_file}"


def sha256(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def git(*args: str) -> str:
    return subprocess.run(["git", "-C", str(ROOT), *args], capture_output=True, text=True, check=True).stdout.strip()


def main() -> None:
    src = pd.read_csv(ROOT / f"experiments/benchmarks/swebench-pl/labels/{SRC}/prompts_index.csv", dtype={"instance_id": str})
    src = src[src["demand"].isin(DIMS)]
    io, labels = JUDGE_IO / RUN, HERE / "labels" / RUN
    for d in (io / "prompts", io / "responses" / "sonnet55-high", labels):
        d.mkdir(parents=True, exist_ok=True)
    rows = []
    for r in src.itertuples(index=False):
        name = f"{r.instance_id}@{r.demand}.txt"
        prompt = (JUDGE_IO / SRC / "prompts" / name).read_bytes()
        assert sha256(prompt) == r.prompt_sha256, f"{name}: differs from {SRC}"
        (io / "prompts" / name).write_bytes(prompt)
        rows.append({"benchmark": "swe-bench-verified", "instance_id": r.instance_id, "file_id": r.instance_id,
                     "demand": r.demand, "family": r.family, "prompt_sha256": r.prompt_sha256})
    pd.DataFrame(rows).to_csv(labels / "prompts_index.csv", index=False)
    run = {
        "run_id": RUN,
        "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "repo_commit": git("rev-parse", "HEAD"),
        "repo_dirty_tracked_files": git("status", "--porcelain", "--untracked-files=no").splitlines(),
        "benchmark": ["swe-bench-verified"],
        "design": {"n_tasks": len(src["instance_id"].unique()), "dims": DIMS, "n_prompts": len(rows), "judges": JUDGES},
        "prompts_from": f"swebench-pl/labels/{SRC} (byte-identical, hash-checked)",
        "judge_agent": {"file": str(AGENT.relative_to(ROOT)), "sha256": sha256(AGENT.read_bytes())},
        "judge_instruction": INSTRUCTION,
        "judge_instruction_sha256": sha256(INSTRUCTION.encode("utf-8")),
        "judge_io": os.path.relpath(io, ROOT),
        "sampling": "harness defaults; snapshot cannot be pinned for subagents; effort is set in the agent file",
    }
    (labels / "run.json").write_text(json.dumps(run, indent=2) + "\n")
    print(f"{RUN}: {len(rows)} prompts from {SRC}")


if __name__ == "__main__":
    main()
