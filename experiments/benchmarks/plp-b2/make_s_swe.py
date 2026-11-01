"""Pin run s-swe-gate (PREREGISTRATION.md, amendment 2): candidate S on the 44 SWE-bench Verified gate tasks.

For each task the current-text PLp prompt is rebuilt with the v2 builder and must match the stored hash of
natural-prompt's run npb-gate-opuslow (Opus low, v2 prompt, current text), so the only difference between that
run and this one is the rubric text. One Opus-low call per task, as in npb-gate-opuslow.

    python experiments/benchmarks/plp-b2/make_s_swe.py
"""

import hashlib
import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from adele.agentic import load_active_catalog
from adele.annotation.prompts import build_annotation_prompt_v2

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
JUDGE_IO = ROOT.parents[1] / "judge-io"
RUN = "s-swe-gate"
GATE = ROOT / "experiments/benchmarks/natural-prompt/labels/npb-gate-opuslow"


def sha256(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def git(*args: str) -> str:
    return subprocess.run(["git", "-C", str(ROOT), *args], capture_output=True, text=True, check=True).stdout.strip()


def main() -> None:
    cur = load_active_catalog()["PLp"]
    s_text = (HERE / "PLp_S.txt").read_text(encoding="utf-8").split("\n", 2)[2].rstrip("\n")
    inst = pd.read_parquet(ROOT / "data/instances/instances_swe-bench-verified.parquet").set_index("instance_id")
    gate = pd.read_csv(GATE / "prompts_index.csv")
    gate = gate[gate["demand"] == "PLp"]
    io, labels = JUDGE_IO / RUN, HERE / "labels" / RUN
    for d in (io / "prompts", io / "responses" / "opus-low", labels):
        d.mkdir(parents=True, exist_ok=True)
    rows = []
    for r in gate.itertuples(index=False):
        text = inst.loc[r.instance_id, "prompt"]
        old = build_annotation_prompt_v2(cur.full_name, cur.content, text)
        assert sha256(old.encode("utf-8")) == r.prompt_sha256, r.instance_id
        new = build_annotation_prompt_v2(cur.full_name, s_text, text)
        (io / "prompts" / f"{r.instance_id}@PLp.txt").write_text(new, encoding="utf-8")
        rows.append({"benchmark": "swe-bench-verified", "instance_id": r.instance_id, "file_id": r.instance_id,
                     "demand": "PLp", "family": "v2", "baseline_prompt_sha256": r.prompt_sha256,
                     "prompt_sha256": sha256(new.encode("utf-8"))})
    pd.DataFrame(rows).to_csv(labels / "prompts_index.csv", index=False)
    run = {"run_id": RUN, "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
           "repo_commit": git("rev-parse", "HEAD"),
           "repo_dirty_tracked_files": git("status", "--porcelain", "--untracked-files=no").splitlines(),
           "benchmark": ["swe-bench-verified"],
           "baseline": "natural-prompt/labels/npb-gate-opuslow (current text, same builder and judge)",
           "rubric": {"candidate": "experiments/benchmarks/plp-b2/PLp_S.txt", "candidate_sha256": sha256(s_text.encode())},
           "design": {"n_prompts": len(rows), "judges": {"opus-low": "adele-judge-v2-low, model alias 'opus'"}},
           "prompt": {"builder": "adele.annotation.prompts.build_annotation_prompt_v2"},
           "judge_instruction": "Prompt file: {prompt_file}\nResponse file: {response_file}",
           "judge_io": os.path.relpath(io, ROOT),
           "sampling": "harness defaults; snapshot cannot be pinned for subagents; effort is set in the agent file"}
    (labels / "run.json").write_text(json.dumps(run, indent=2) + "\n")
    print(f"{RUN}: {len(rows)} prompts; every baseline prompt matched its stored hash")


if __name__ == "__main__":
    main()
