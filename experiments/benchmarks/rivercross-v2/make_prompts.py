"""Pin the runs of rivercross-v2 (PREREGISTRATION.md): the rivercross frames judged one state per call
with the v2 prompt (adele.annotation.prompts.build_annotation_prompt_v2), the current rubrics and Opus low.

  rc-state  the 43 state-visible puzzle states of experiments/rivercross/frames/1b_state_visible.csv,
            for PLp, PLe and PLs (129 cells). The solver's cost-to-go for each state is in
            frames/ground_truth/1b_state_visible_cost_to_go.csv and is never shown to the judge.
  rc-play   the 49 states of captured agent play in experiments/rivercross/ple/frame_PLe_1b.csv, for
            PLe (49 cells).

The frames are read from experiments/rivercross/ and not changed. Their SHA-256 is recorded in run.json.

    python experiments/benchmarks/rivercross-v2/make_prompts.py
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
RC = ROOT / "experiments/rivercross"
JUDGE_IO = ROOT.parents[1] / "judge-io"
AGENT = ROOT / "experiments/benchmarks/natural-prompt/adele-judge-v2-low.md"
JUDGES = {"opus-low": "Claude Code subagent 'adele-judge-v2-low' (tools: Read, Write; omitClaudeMd; effort low), "
                      "model alias 'opus'"}
INSTRUCTION = "Prompt file: {prompt_file}\nResponse file: {response_file}"
RUNS = {"rc-state": (RC / "frames/1b_state_visible.csv", ["PLp", "PLe", "PLs"]),
        "rc-play": (RC / "ple/frame_PLe_1b.csv", ["PLe"])}


def sha256(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def git(*args: str) -> str:
    return subprocess.run(["git", "-C", str(ROOT), *args], capture_output=True, text=True, check=True).stdout.strip()


def main() -> None:
    catalog = load_active_catalog()
    for run_id, (frame, dims) in RUNS.items():
        io, labels = JUDGE_IO / run_id, HERE / "labels" / run_id
        for d in (io / "prompts", io / "responses" / "opus-low", labels):
            d.mkdir(parents=True, exist_ok=True)
        states = pd.read_csv(frame)
        rows = []
        for s in states.itertuples(index=False):
            fid = s.custom_id.replace("#", "--")  # '#' is awkward in file names
            for dim in dims:
                r = catalog[dim]
                prompt = build_annotation_prompt_v2(r.full_name, r.content, s.prompt)
                (io / "prompts" / f"{fid}@{dim}.txt").write_text(prompt, encoding="utf-8")
                rows.append({"benchmark": "rivercross", "instance_id": s.custom_id, "file_id": fid, "demand": dim,
                             "family": "v2", "prompt_sha256": sha256(prompt.encode("utf-8"))})
        pd.DataFrame(rows).to_csv(labels / "prompts_index.csv", index=False)
        run = {
            "run_id": run_id,
            "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "repo_commit": git("rev-parse", "HEAD"),
            "repo_dirty_tracked_files": git("status", "--porcelain", "--untracked-files=no").splitlines(),
            "benchmark": ["rivercross"],
            "frame": {"file": str(frame.relative_to(ROOT)), "sha256": sha256(frame.read_bytes())},
            "design": {"n_states": len(states), "dims": dims, "n_prompts": len(rows), "judges": JUDGES},
            "rubrics_sha256": {d: sha256(catalog[d].content.encode("utf-8")) for d in dims},
            "prompt": {"builder": "adele.annotation.prompts.build_annotation_prompt_v2",
                       "builder_file_sha256": sha256((ROOT / "src/adele/annotation/prompts.py").read_bytes())},
            "judge_agent": {"file": str(AGENT.relative_to(ROOT)), "sha256": sha256(AGENT.read_bytes())},
            "judge_instruction": INSTRUCTION,
            "judge_instruction_sha256": sha256(INSTRUCTION.encode("utf-8")),
            "judge_io": os.path.relpath(io, ROOT),
            "sampling": "harness defaults; snapshot cannot be pinned for subagents; effort is set in the agent file",
        }
        (labels / "run.json").write_text(json.dumps(run, indent=2) + "\n")
        print(f"{run_id}: {len(rows)} prompts")


if __name__ == "__main__":
    main()
