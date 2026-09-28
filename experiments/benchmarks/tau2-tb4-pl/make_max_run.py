"""Pin the follow-up run tb4pl-max (exploratory; PREREGISTRATION.md, section Follow-up).

Opus at max effort judges PLp on the 34 Terminal-Bench analysis-set tasks. The prompts are
copied byte for byte from run tb4pl-r1, each checked against its prompt_sha256. The judge is
swebench-30's adele-judge.md (effort max). This writes labels/tb4pl-max/ (run.json,
prompts_index.csv) and copies the prompts to JUDGE_IO/tb4pl-max/prompts/.

    python experiments/benchmarks/tau2-tb4-pl/make_max_run.py
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
SRC, RUN = "tb4pl-r1", "tb4pl-max"
AGENT = HERE.parent / "swebench-30/adele-judge.md"
JUDGES = {
    "opus-max": "Claude Code subagent 'adele-judge' (tools: Read, Write; omitClaudeMd; "
                "effort max), model alias 'opus'",
}


def sha256(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def git(*args: str) -> str:
    return subprocess.run(["git", "-C", str(ROOT), *args], capture_output=True,
                          text=True, check=True).stdout.strip()


def main() -> None:
    src = json.loads((HERE / f"labels/{SRC}/run.json").read_text())
    index = pd.read_csv(HERE / f"labels/{SRC}/prompts_index.csv", dtype={"instance_id": str})
    sample = pd.read_csv(HERE / "sample.csv", dtype={"instance_id": str})
    keep = set(sample.loc[(sample["run"] == SRC) & sample["analysis_set"], "instance_id"])
    index = index[(index["demand"] == "PLp") & index["instance_id"].isin(keep)].reset_index(drop=True)
    assert len(index) == 34

    src_io, io, labels = ROOT / src["judge_io"], ROOT.parents[1] / "judge-io" / RUN, HERE / "labels" / RUN
    for d in (io / "prompts", io / "responses" / "opus-max", labels):
        d.mkdir(parents=True, exist_ok=True)
    for r in index.itertuples(index=False):
        name = f"{r.file_id}@{r.demand}.txt"
        data = (src_io / "prompts" / name).read_bytes()
        assert sha256(data) == r.prompt_sha256, f"{name}: prompt differs from {SRC}"
        (io / "prompts" / name).write_bytes(data)
    index.to_csv(labels / "prompts_index.csv", index=False)

    run = {
        "run_id": RUN,
        "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "repo_commit": git("rev-parse", "HEAD"),
        "repo_dirty_tracked_files": git("status", "--porcelain", "--untracked-files=no").splitlines(),
        "follows": SRC,
        **{k: src[k] for k in ("benchmark", "instances", "outcomes", "rubrics", "prompt",
                               "judge_instruction", "judge_instruction_sha256", "sampling")},
        "sample": {"file": "sample.csv", "rows": f"run == {SRC!r} and analysis_set; PLp only"},
        "design": {"n_tasks": len(index), "dims": ["PLp"], "n_prompts": len(index), "judges": JUDGES},
        "judge_agent": {"file": str(AGENT.relative_to(ROOT)), "sha256": sha256(AGENT.read_bytes())},
        "judge_io": os.path.relpath(io, ROOT),
    }
    (labels / "run.json").write_text(json.dumps(run, indent=2) + "\n")
    print(f"{RUN}: {len(index)} prompts, identical to {SRC} → {io / 'prompts'}")


if __name__ == "__main__":
    main()
