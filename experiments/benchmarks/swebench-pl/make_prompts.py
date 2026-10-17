"""Write the judge prompts, sample and run manifests for the swebench-pl study.

Two runs, both judged by Opus at medium effort (adele-judge-medium.md), on PLp, PLe and PLs:
  swepl-gate  the 44 swebench-30 tasks (30 new, 14 anchors): the effort gate, 132 prompts
  swepl-r1    every other SWE-bench Verified task with leaderboard solve rate >= 0.05
Prompts are built exactly as in swebench-30 (same builder, rubric files and task text); the
gate's prompts are checked against swebench-30's run swev30-r4, hash by hash.
Task text goes to the gitignored data/annotations/<run>/prompts/ and, for the judges, to
JUDGE_IO/<run>/prompts/. sample.csv, the indexes (hashes) and run.json are committed.

    python experiments/benchmarks/swebench-pl/make_prompts.py
    python experiments/benchmarks/swebench-pl/make_prompts.py --low-gate   # step 1b only
    python experiments/benchmarks/swebench-pl/make_prompts.py --low-r1     # step 1c only
"""

import argparse
import hashlib
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
S30 = HERE.parent / "swebench-30"
DIMS = ["PLp", "PLe", "PLs"]
SOLVABLE_FROM = 0.05
JUDGE_AGENT = HERE / "adele-judge-medium.md"
JUDGES = {
    "opus-medium": "Claude Code subagent 'adele-judge-medium' (tools: Read, Write; omitClaudeMd; "
                   "effort medium), model alias 'opus'",
}
# Step 1b (exploratory): the same gate cells at effort low.
LOW_AGENT = HERE / "adele-judge-low.md"
LOW_JUDGES = {
    "opus-low": "Claude Code subagent 'adele-judge-low' (tools: Read, Write; omitClaudeMd; "
                "effort low), model alias 'opus'",
}
# Sent verbatim to each judge subagent, one (task, dimension) per call.
JUDGE_INSTRUCTION = """Prompt file: {prompt_file}
Response file: {response_file}"""
# As in swebench-30 (its deviation 3): judge files two levels above the repo, where no folder
# between the judging session's folder and the files has a CLAUDE.md.
JUDGE_IO = ROOT.parents[1] / "judge-io"


def sha256(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def git(*args: str) -> str:
    return subprocess.run(["git", "-C", str(ROOT), *args], capture_output=True,
                          text=True, check=True).stdout.strip()


def write_run(run_id: str, ids: list[str], rubrics, text: pd.Series, sample_note: str,
              judges: dict = JUDGES, agent: Path = JUDGE_AGENT) -> pd.DataFrame:
    data_dir, io, labels = ROOT / "data/annotations" / run_id, JUDGE_IO / run_id, HERE / "labels" / run_id
    for d in (data_dir / "prompts", io / "prompts", labels):
        d.mkdir(parents=True, exist_ok=True)
    for judge in judges:
        (io / "responses" / judge).mkdir(parents=True, exist_ok=True)

    index = []
    for iid in ids:
        for dim in DIMS:
            r = rubrics[dim]
            prompt = build_annotation_prompt(demand_name=r.full_name, rubric_content=r.content,
                                             task_instance=text[iid])
            for d in (data_dir, io):
                (d / "prompts" / f"{iid}@{dim}.txt").write_text(prompt, encoding="utf-8")
            index.append({"instance_id": iid, "demand": dim, "family": "v2",
                          "rubric_sha256": sha256(Path(r.file_path).read_bytes()),
                          "prompt_sha256": sha256(prompt.encode("utf-8"))})
    index = pd.DataFrame(index)
    index.to_csv(labels / "prompts_index.csv", index=False)

    manifest_rows = pd.read_csv(ROOT / "data/instances/INSTANCES.tsv", sep="\t").set_index("benchmark")
    run = {
        "run_id": run_id,
        "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "repo_commit": git("rev-parse", "HEAD"),
        "repo_dirty_tracked_files": git("status", "--porcelain", "--untracked-files=no").splitlines(),
        "benchmark": "swe-bench-verified",
        "instances": {
            "source": "princeton-nlp/SWE-bench_Verified (HF), split test",
            "hf_revision": "c104f840cc67f8b6eec6f759ebc8b2693d585d4a",
            "task_text": "problem_statement only (adele.agentic.benchmarks loader), as in swebench-30",
            "frozen_file_sha256": manifest_rows.loc["swe-bench-verified", "sha256"],
        },
        "outcomes": {
            "source": "github.com/SWE-bench/experiments evaluation/verified/*/results/results.json",
            "commit": "40f164d5b8f1d249bf95a6df8b74b577fd8e519d",
            "entries": 135,
        },
        "sample": {"file": "sample.csv", "rule": sample_note},
        "design": {"n_tasks": len(ids), "dims": DIMS, "n_prompts": len(index), "judges": judges},
        "rubrics": {d: {"name": rubrics[d].full_name,
                        "file": str(Path(rubrics[d].file_path).relative_to(ROOT)),
                        "sha256": sha256(Path(rubrics[d].file_path).read_bytes())} for d in DIMS},
        "prompt": {
            "builder": "adele.annotation.prompts.build_annotation_prompt",
            "builder_file_sha256": sha256((ROOT / "src/adele/annotation/prompts.py").read_bytes()),
        },
        "judge_agent": {"file": str(agent.relative_to(ROOT)), "sha256": sha256(agent.read_bytes())},
        "judge_instruction": JUDGE_INSTRUCTION,
        "judge_instruction_sha256": sha256(JUDGE_INSTRUCTION.encode("utf-8")),
        "judge_io": os.path.relpath(io, ROOT),
        "sampling": "harness defaults; snapshot cannot be pinned for subagents; effort is set in the agent file",
    }
    for d in (labels, data_dir):
        (d / "run.json").write_text(json.dumps(run, indent=2) + "\n")
    print(f"{run_id}: {len(ids)} tasks, {len(index)} prompts → {io / 'prompts'}")
    return index


def check_same_prompts(index: pd.DataFrame, run_id: str) -> None:
    ref = pd.read_csv(HERE / f"labels/{run_id}/prompts_index.csv", dtype={"instance_id": str})
    key = ["instance_id", "demand"]
    assert index.set_index(key)["prompt_sha256"].sort_index().equals(
        ref.set_index(key)["prompt_sha256"].sort_index()), f"prompts differ from {run_id}"


def check_gate(index: pd.DataFrame) -> None:
    r4 = pd.read_csv(S30 / "labels/swev30-r4/prompts_index.csv", dtype={"instance_id": str})
    ref = r4[r4["demand"].isin(DIMS)].set_index(["instance_id", "demand"])["prompt_sha256"].sort_index()
    assert index.set_index(["instance_id", "demand"])["prompt_sha256"].sort_index().equals(ref), \
        "gate prompts differ from swev30-r4"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--low-gate", action="store_true", help="write only run swepl-gate-low (step 1b)")
    ap.add_argument("--low-r1", action="store_true", help="write only run swepl-r1-low (step 1c)")
    args = ap.parse_args()
    low_only = args.low_gate
    inst = pd.read_parquet(ROOT / "data/instances/instances_swe-bench-verified.parquet")
    text = inst.set_index("instance_id")["prompt"]
    flags = pd.read_parquet(ROOT / "data/results/swebench.parquet")
    solve = flags.groupby("instance_id")["success"].mean()
    assert len(solve) == 500 and (flags.groupby("instance_id").size() == 135).all()
    rubrics = load_active_catalog()

    s30 = pd.read_csv(S30 / "sample.csv", dtype={"instance_id": str})
    gate_ids = list(s30["instance_id"])
    scale_ids = sorted(set(solve[solve >= SOLVABLE_FROM].index) - set(gate_ids))
    if low_only:
        check_gate(write_run("swepl-gate-low", gate_ids, rubrics, text,
                             "the 44 swebench-30 tasks, as swepl-gate", LOW_JUDGES, LOW_AGENT))
        return
    if args.low_r1:
        check_same_prompts(write_run("swepl-r1-low", scale_ids, rubrics, text,
                                     "the 398 swepl-r1 tasks, as swepl-r1", LOW_JUDGES, LOW_AGENT), "swepl-r1")
        return

    sample = pd.DataFrame({"instance_id": gate_ids + scale_ids})
    sample["solve_rate"] = sample["instance_id"].map(solve).round(4)
    sample["solvable"] = sample["solve_rate"] >= SOLVABLE_FROM
    sample["swebench30_role"] = sample["instance_id"].map(s30.set_index("instance_id")["role"]).fillna("")
    sample["run"] = ["swepl-gate"] * len(gate_ids) + ["swepl-r1"] * len(scale_ids)
    sample.to_csv(HERE / "sample.csv", index=False)

    gate = write_run("swepl-gate", gate_ids, rubrics, text,
                     "the 44 swebench-30 tasks (30 new, 14 anchors), all solve rates")
    check_gate(gate)
    write_run("swepl-r1", scale_ids, rubrics, text,
              f"solve rate >= {SOLVABLE_FROM} over the 135 entries, not in swebench-30")
    print(f"sample.csv: {len(sample)} tasks, {int(sample['solvable'].sum())} solvable")


if __name__ == "__main__":
    main()
