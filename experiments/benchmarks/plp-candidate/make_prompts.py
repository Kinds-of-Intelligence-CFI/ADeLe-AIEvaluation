"""Write the prompts and pin the runs of the plp-candidate comparison (PREREGISTRATION.md).

The candidate is PLp with one sentence of Level 3 replaced (see OLD and NEW below). Everything else
is as in tau2-tb4-pl and swebench-pl: builder, instruction, task text, and the judge (Opus at low
effort). Runs:
  cand-tb    candidate text, the 34 Terminal-Bench analysis-set tasks
  ctrl-tb    current text, the same 34 tasks: tb4pl-r1's prompts, byte for byte (noise control)
  cand-swe   candidate text, 60 solvable SWE-bench Verified tasks (all at PLp 3 under Opus low, rest drawn)
  cand-tau2  candidate text, the 232 tau2 tasks of tau2pl-r1
Prompts built with the current text must reproduce the original runs' prompt hashes, which checks
that nothing but the sentence differs.

    python experiments/benchmarks/plp-candidate/make_prompts.py
"""

import hashlib
import importlib.util
import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

from adele.agentic import load_active_catalog
from adele.annotation.prompts import build_annotation_prompt

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BENCH = HERE.parent
JUDGE_IO = ROOT.parents[1] / "judge-io"
AGENT = BENCH / "swebench-pl/adele-judge-low.md"
JUDGES = {"opus-low": "Claude Code subagent 'adele-judge-low' (tools: Read, Write; omitClaudeMd; "
                      "effort low), model alias 'opus'"}
INSTRUCTION = "Prompt file: {prompt_file}\nResponse file: {response_file}"
OLD = ("An option that looks good locally can be wrong because of its consequences several steps "
       "later, so alternatives must be compared by looking ahead before committing.")
NEW = "The best choice at one step depends on choices at other steps, so options must be compared before committing."
SEED = 20260928


def sha256(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def git(*args: str) -> str:
    return subprocess.run(["git", "-C", str(ROOT), *args], capture_output=True, text=True, check=True).stdout.strip()


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def index_of(study: str, runs: list[str]) -> pd.DataFrame:
    idx = pd.concat(pd.read_csv(BENCH / f"{study}/labels/{r}/prompts_index.csv", dtype={"instance_id": str}) for r in runs)
    idx = idx[idx["demand"] == "PLp"]
    return idx.set_index("file_id" if "file_id" in idx else "instance_id")["prompt_sha256"]


def write_run(run_id: str, rows: pd.DataFrame, rubric: str, rubric_note: dict, name: str) -> None:
    io, labels = JUDGE_IO / run_id, HERE / "labels" / run_id
    for d in (io / "prompts", io / "responses" / "opus-low", labels):
        d.mkdir(parents=True, exist_ok=True)
    index = []
    for r in rows.itertuples(index=False):
        prompt = build_annotation_prompt(demand_name=name, rubric_content=rubric, task_instance=r.text)
        (io / "prompts" / f"{r.file_id}@PLp.txt").write_text(prompt, encoding="utf-8")
        index.append({"benchmark": r.benchmark, "instance_id": r.instance_id, "file_id": r.file_id, "demand": "PLp",
                      "family": "v2", "prompt_sha256": sha256(prompt.encode("utf-8"))})
    index = pd.DataFrame(index)
    index.to_csv(labels / "prompts_index.csv", index=False)
    run = {
        "run_id": run_id,
        "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "repo_commit": git("rev-parse", "HEAD"),
        "repo_dirty_tracked_files": git("status", "--porcelain", "--untracked-files=no").splitlines(),
        "benchmark": sorted(rows["benchmark"].unique()),
        "sample": {"file": "sample.csv", "rows": f"run == {run_id!r}"},
        "design": {"n_tasks": len(rows), "dims": ["PLp"], "n_prompts": len(index), "judges": JUDGES},
        "rubric": rubric_note,
        "prompt": {"builder": "adele.annotation.prompts.build_annotation_prompt",
                   "builder_file_sha256": sha256((ROOT / "src/adele/annotation/prompts.py").read_bytes())},
        "judge_agent": {"file": str(AGENT.relative_to(ROOT)), "sha256": sha256(AGENT.read_bytes())},
        "judge_instruction": INSTRUCTION,
        "judge_instruction_sha256": sha256(INSTRUCTION.encode("utf-8")),
        "judge_io": os.path.relpath(io, ROOT),
        "sampling": "harness defaults; snapshot cannot be pinned for subagents; effort is set in the agent file",
    }
    (labels / "run.json").write_text(json.dumps(run, indent=2) + "\n")
    print(f"{run_id}: {len(index)} prompts")


def main() -> None:
    plp = load_active_catalog()["PLp"]
    assert plp.content.count(OLD) == 1
    candidate = plp.content.replace(OLD, NEW)
    (HERE / "PLp_candidate.txt").write_text(candidate, encoding="utf-8")
    base_note = {"file": str(Path(plp.file_path).relative_to(ROOT)), "sha256": sha256(Path(plp.file_path).read_bytes())}
    cand_note = {**base_note, "candidate": "plp-candidate/PLp_candidate.txt",
                 "candidate_sha256": sha256(candidate.encode("utf-8")), "old_sentence": OLD, "new_sentence": NEW}

    # Terminal-Bench and tau2: task text and outcomes exactly as in tau2-tb4-pl.
    t2 = load("t2_make_prompts", BENCH / "tau2-tb4-pl/make_prompts.py")
    s2, text2 = t2.build_sample()
    s2["text"] = s2["file_id"].map(text2)
    tb = s2[(s2["benchmark"] == t2.TB4) & s2["analysis_set"]].copy()
    tau2 = s2[s2["benchmark"].str.startswith("tau2-")].copy()
    assert len(tb) == 34 and len(tau2) == 232

    # SWE-bench: the swebench-pl sample and task text; all tasks at PLp 3 under Opus low, then drawn.
    sw = pd.read_csv(BENCH / "swebench-pl/sample.csv").set_index("instance_id")
    sw = sw[sw["solvable"]]
    low = pd.concat(pd.read_csv(BENCH / f"swebench-pl/labels/{r}/labels_long.csv") for r in ("swepl-gate-low", "swepl-r1-low"))
    low = low[low["demand"] == "PLp"].set_index("instance_id")["level"].loc[sw.index]
    threes = sorted(low.index[low == 3])
    rng = np.random.default_rng(SEED)
    rest = sorted(set(sw.index) - set(threes))
    picked = threes + list(rng.choice(rest, 60 - len(threes), replace=False))
    inst = pd.read_parquet(ROOT / "data/instances/instances_swe-bench-verified.parquet").set_index("instance_id")
    swe = pd.DataFrame({"benchmark": "swe-bench-verified", "instance_id": picked, "file_id": picked,
                        "solve_rate": sw.loc[picked, "solve_rate"].values, "text": inst.loc[picked, "prompt"].values})

    # Check: the current text reproduces the original prompts, so only the sentence differs.
    for rows, ref in ((tb, index_of("tau2-tb4-pl", ["tb4pl-r1"])), (tau2, index_of("tau2-tb4-pl", ["tau2pl-r1"])),
                      (swe, index_of("swebench-pl", ["swepl-gate-low", "swepl-r1-low"]))):
        for r in rows.itertuples(index=False):
            p = build_annotation_prompt(demand_name=plp.full_name, rubric_content=plp.content, task_instance=r.text)
            assert sha256(p.encode("utf-8")) == ref[r.file_id], f"{r.file_id}: current-text prompt differs"

    runs = {"cand-tb": (tb, candidate, cand_note), "ctrl-tb": (tb, plp.content, base_note),
            "cand-swe": (swe, candidate, cand_note), "cand-tau2": (tau2, candidate, cand_note)}
    frames = []
    for run_id, (rows, rubric, note) in runs.items():
        write_run(run_id, rows, rubric, note, plp.full_name)
        frames.append(rows.drop(columns="text").assign(run=run_id))
    cols = ["run", "benchmark", "instance_id", "file_id", "solve_rate", "expert_hours", "analysis_set"]
    pd.concat(frames)[cols].to_csv(HERE / "sample.csv", index=False)


if __name__ == "__main__":
    main()
