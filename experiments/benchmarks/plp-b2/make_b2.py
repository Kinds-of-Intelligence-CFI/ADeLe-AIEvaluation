"""Build PLp candidate B2 (approved by Pablo on 2026-09-30) and pin its first test, run b2-search
(PREREGISTRATION.md).

B2 is the current PLp text (src/adele/rubrics/data_v2/Paolo_Pablo/PLp.txt, unchanged) with
  - two sentences after the length sentence of "What this dimension does not cover";
  - one Level 1 example (a long plan fixed by a routine) and one Level 3 example (a short plan with a trap),
both outside river-crossing puzzles, so the test below measures generalisation rather than copying.
The script checks that B2 is exactly the current text plus these insertions, runs the word 4-gram check of the
new examples against the 54 test frames, and builds the b2-search prompts: the amendment 2 grid of
rivercross-v2 (frames/search_frame.csv), judged three times (opus-low-r1..r3) with the v2 prompt.

    python experiments/benchmarks/plp-b2/make_b2.py
"""

import hashlib
import json
import os
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from adele.agentic import load_active_catalog
from adele.annotation.prompts import build_annotation_prompt_v2

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
JUDGE_IO = ROOT.parents[1] / "judge-io"
FRAME = ROOT / "experiments/benchmarks/rivercross-v2/frames/search_frame.csv"
AGENT = ROOT / "experiments/benchmarks/natural-prompt/adele-judge-v2-low.md"
RUN, REPEATS = "b2-search", ["opus-low-r1", "opus-low-r2", "opus-low-r3"]

ANCHOR_SCOPE = "nor by how many agents are involved or how their beliefs and intentions must be worked out."
SCOPE_ADD = (" Only choices that could go wrong add to this demand. A step with one sensible option, or a choice "
             "where every option works, adds nothing, however many such steps there are.")
ANCHOR_L1 = "* Write a covering letter for a job application, given the advertisement and the CV it responds to."
L1_ADD = ("\n* Move a tower of eight disks from one peg to another under the usual rules. The standard recursive "
          "procedure fixes all 255 moves, so nothing has to be searched for.")
ANCHOR_L3 = ("The data structure settled on early decides whether the later queries can be answered in time, so the "
             "options must be compared before committing.")
L3_ADD = ("\n* Solve a sliding-block puzzle that is four moves from solved, where the move that looks most natural "
          "blocks the only way out.")


def sha256(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def git(*args: str) -> str:
    return subprocess.run(["git", "-C", str(ROOT), *args], capture_output=True, text=True, check=True).stdout.strip()


def fourgrams(text: str) -> set:
    w = re.findall(r"[a-z0-9]+", text.lower())
    return {tuple(w[i:i + 4]) for i in range(len(w) - 3)}


def main() -> None:
    cur = load_active_catalog()["PLp"]
    text = cur.content
    for anchor in (ANCHOR_SCOPE, ANCHOR_L1, ANCHOR_L3):
        assert text.count(anchor) == 1, anchor
    b2 = (text.replace(ANCHOR_SCOPE, ANCHOR_SCOPE + SCOPE_ADD)
              .replace(ANCHOR_L1, ANCHOR_L1 + L1_ADD)
              .replace(ANCHOR_L3, ANCHOR_L3 + L3_ADD))
    assert len(b2) == len(text) + len(SCOPE_ADD) + len(L1_ADD) + len(L3_ADD)
    # same layout as the source file (heading, blank line, text, final newline); the prompt uses the text only
    (HERE / "PLp_B2.txt").write_text(f"# {cur.full_name}\n\n{b2}\n", encoding="utf-8")

    frames = pd.read_csv(FRAME)
    new = fourgrams(L1_ADD) | fourgrams(L3_ADD) | fourgrams(SCOPE_ADD)
    shared = sorted({g for t in frames["prompt"] for g in fourgrams(t) & new})
    print("4-grams shared between the new text and the 54 frames:", shared or "none")

    io, labels = JUDGE_IO / RUN, HERE / "labels" / RUN
    for d in [io / "prompts", labels] + [io / "responses" / r for r in REPEATS]:
        d.mkdir(parents=True, exist_ok=True)
    rows = []
    for s in frames.itertuples(index=False):
        prompt = build_annotation_prompt_v2(cur.full_name, b2, s.prompt)
        (io / "prompts" / f"{s.custom_id}@PLp.txt").write_text(prompt, encoding="utf-8")
        rows.append({"benchmark": "rivercross", "instance_id": s.custom_id, "file_id": s.custom_id, "demand": "PLp",
                     "family": "v2", "prompt_sha256": sha256(prompt.encode("utf-8"))})
    pd.DataFrame(rows).to_csv(labels / "prompts_index.csv", index=False)
    run = {"run_id": RUN, "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
           "repo_commit": git("rev-parse", "HEAD"),
           "repo_dirty_tracked_files": git("status", "--porcelain", "--untracked-files=no").splitlines(),
           "benchmark": ["rivercross"],
           "frame": {"file": str(FRAME.relative_to(ROOT)), "sha256": sha256(FRAME.read_bytes())},
           "rubric": {"current": str(Path(cur.file_path).relative_to(ROOT)), "current_sha256": sha256(text.encode()),
                      "candidate": "experiments/benchmarks/plp-b2/PLp_B2.txt", "candidate_sha256": sha256(b2.encode()),
                      "fourgrams_shared_with_frames": [" ".join(g) for g in shared]},
           "design": {"n_prompts": len(rows),
                      "judges": {r: "adele-judge-v2-low, model alias 'opus'; repeat " + r[-1] for r in REPEATS}},
           "prompt": {"builder": "adele.annotation.prompts.build_annotation_prompt_v2",
                      "builder_file_sha256": sha256((ROOT / "src/adele/annotation/prompts.py").read_bytes())},
           "judge_agent": {"file": str(AGENT.relative_to(ROOT)), "sha256": sha256(AGENT.read_bytes())},
           "judge_instruction": "Prompt file: {prompt_file}\nResponse file: {response_file}",
           "judge_io": os.path.relpath(io, ROOT),
           "sampling": "harness defaults; snapshot cannot be pinned for subagents; effort is set in the agent file"}
    (labels / "run.json").write_text(json.dumps(run, indent=2) + "\n")
    print(f"{RUN}: {len(rows)} prompts x {len(REPEATS)}")


if __name__ == "__main__":
    main()
