"""Write the judge prompts and the run manifest for the swebench-30 run.

One prompt per (task, dimension), built by adele's build_annotation_prompt exactly
as `adele agentic judge` would, for
  - the 30 new tasks x 25 rubrics: the 18 v1 rubrics with v1's MSm replaced by the
    v2 MSm (v1's text plus one carve-out), plus the 7 other active v2 rubrics; and
  - the 14 pilot anchors x PLp, PLe, PLs (test-retest against the 2026-09-14 pilot).

Prompts contain task text, so they go to the gitignored data/annotations/<run>/prompts/,
with a copy for the judges in JUDGE_IO, outside the repo.
The index (hashes, no text) and run.json go to labels/<run>/ here, and are committed.
Judges are the `adele-judge` subagent (adele-judge.md, installed under .claude/agents/),
one prompt per call; see JUDGE_INSTRUCTION and PREREGISTRATION.md (deviations 1 to 3).

    python experiments/benchmarks/swebench-30/make_prompts.py
"""

import hashlib
import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from adele.agentic import load_active_catalog
from adele.annotation.prompts import build_annotation_prompt
from adele.rubrics.catalog import RubricsCatalog

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
RUN_ID = "swev30-r4"
ANCHOR_DIMS = ["PLp", "PLe", "PLs"]
JUDGE_AGENT = HERE / "adele-judge.md"
JUDGES = {
    "sonnet": "Claude Code subagent 'adele-judge' (tools: Read, Write; omitClaudeMd; effort max), model alias 'sonnet'",
    "opus": "Claude Code subagent 'adele-judge' (tools: Read, Write; omitClaudeMd; effort max), model alias 'opus'",
}
# Sent verbatim to each judge subagent, one (task, dimension) per call; the judging
# protocol itself is the agent's system prompt in adele-judge.md.
JUDGE_INSTRUCTION = """Prompt file: {prompt_file}
Response file: {response_file}"""
# The judges read and write here, two levels above the repo: Claude Code attaches a folder's
# CLAUDE.md to a subagent that reads a file below it, and omitClaudeMd does not stop that
# (deviation 3). Judging sessions run in ROOT.parents[1], the folder that holds judge-io/.
JUDGE_IO = ROOT.parents[1] / "judge-io" / RUN_ID


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def git(*args: str) -> str:
    return subprocess.run(["git", "-C", str(ROOT), *args], capture_output=True,
                          text=True, check=True).stdout.strip()


def main() -> None:
    sample = pd.read_csv(HERE / "sample.csv", dtype={"instance_id": str})
    inst = pd.read_parquet(ROOT / "data/instances/instances_swe-bench-verified.parquet")
    text = inst.set_index("instance_id")["prompt"]

    v1, v2 = RubricsCatalog(), load_active_catalog()
    rubrics = {**{c: v1[c] for c in v1.acronyms if c not in v2}, **{c: v2[c] for c in v2.acronyms}}
    assert len(rubrics) == 25, sorted(rubrics)

    design = [(i, d) for i in sample.loc[sample["role"] == "new", "instance_id"] for d in sorted(rubrics)]
    design += [(i, d) for i in sample.loc[sample["role"] == "anchor", "instance_id"] for d in ANCHOR_DIMS]

    data_dir = ROOT / "data/annotations" / RUN_ID
    for d in (data_dir, JUDGE_IO):
        (d / "prompts").mkdir(parents=True, exist_ok=True)
    for judge in JUDGES:
        (JUDGE_IO / "responses" / judge).mkdir(parents=True, exist_ok=True)
    labels_dir = HERE / "labels" / RUN_ID
    labels_dir.mkdir(parents=True, exist_ok=True)

    index = []
    for iid, dim in design:
        r = rubrics[dim]
        prompt = build_annotation_prompt(demand_name=r.full_name, rubric_content=r.content,
                                         task_instance=text[iid])
        for d in (data_dir, JUDGE_IO):
            (d / "prompts" / f"{iid}@{dim}.txt").write_text(prompt, encoding="utf-8")
        index.append({
            "instance_id": iid, "demand": dim, "family": "v2" if dim in v2 else "v1",
            "rubric_sha256": sha256_bytes(Path(r.file_path).read_bytes()),
            "prompt_sha256": sha256_bytes(prompt.encode("utf-8")),
        })
    pd.DataFrame(index).to_csv(labels_dir / "prompts_index.csv", index=False)

    manifest_rows = pd.read_csv(ROOT / "data/instances/INSTANCES.tsv", sep="\t").set_index("benchmark")
    run = {
        "run_id": RUN_ID,
        "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "repo_commit": git("rev-parse", "HEAD"),
        "repo_dirty_tracked_files": git("status", "--porcelain", "--untracked-files=no").splitlines(),
        "benchmark": "swe-bench-verified",
        "instances": {
            "source": "princeton-nlp/SWE-bench_Verified (HF), split test",
            "hf_revision": "c104f840cc67f8b6eec6f759ebc8b2693d585d4a",
            "task_text": "problem_statement only (adele.agentic.benchmarks loader), as in the pilots",
            "frozen_file_sha256": manifest_rows.loc["swe-bench-verified", "sha256"],
        },
        "outcomes": {
            "source": "github.com/SWE-bench/experiments evaluation/verified/*/results/results.json",
            "commit": "40f164d5b8f1d249bf95a6df8b74b577fd8e519d",
            "entries": 135,
            "universe": "official 500 ids (adele results fetch-swebench --instance-ids)",
        },
        "sample": {"file": "sample.csv", "seed": 20260926, "design": "10 per solve-rate tercile + 14 pilot anchors",
                   "suspect_rule": "leaderboard solve rate < 0.05"},
        "design": {"n_new": int((sample["role"] == "new").sum()),
                   "n_anchor": int((sample["role"] == "anchor").sum()),
                   "anchor_dims": ANCHOR_DIMS, "n_prompts": len(design),
                   "calls_per_judge": len(design), "judges": JUDGES},
        "rubrics": {d: {"name": r.full_name, "family": "v2" if d in v2 else "v1",
                        "file": str(Path(r.file_path).relative_to(ROOT)),
                        "sha256": sha256_bytes(Path(r.file_path).read_bytes())}
                    for d, r in sorted(rubrics.items())},
        "prompt": {
            "builder": "adele.annotation.prompts.build_annotation_prompt",
            "builder_file_sha256": sha256_bytes((ROOT / "src/adele/annotation/prompts.py").read_bytes()),
            "note": "shared agentic-v2 prompt for all 25 rubrics, incl. the 'demand is a property "
                    "of the task; when in doubt assign the lower' sentence (not on main)",
        },
        "judge_agent": {"file": str(JUDGE_AGENT.relative_to(ROOT)),
                        "sha256": sha256_bytes(JUDGE_AGENT.read_bytes())},
        "judge_instruction": JUDGE_INSTRUCTION,
        "judge_instruction_sha256": sha256_bytes(JUDGE_INSTRUCTION.encode("utf-8")),
        "judge_io": os.path.relpath(JUDGE_IO, ROOT),
        "sampling": "harness defaults; temperature and snapshot cannot be pinned for subagents",
        "unguessability": "UG = 100 for every task (open-ended); computed, not judged",
    }
    (labels_dir / "run.json").write_text(json.dumps(run, indent=2) + "\n")
    (data_dir / "run.json").write_text(json.dumps(run, indent=2) + "\n")
    print(f"{len(design)} prompts → {data_dir / 'prompts'} and {JUDGE_IO / 'prompts'}; "
          f"index + run.json → {labels_dir}")


if __name__ == "__main__":
    main()
