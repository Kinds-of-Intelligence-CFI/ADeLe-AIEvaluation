"""Pin the runs of pl-relabel-v2 (PREREGISTRATION.md): PLp, PLe and PLs relabelled with the v2 prompt
(adele.annotation.prompts.build_annotation_prompt_v2) and the same judge as before, Opus low.

  v2-swe     SWE-bench Verified: the 398 tasks of swebench-pl's run swepl-r1-low (1,194 cells). The 44 gate
             tasks were already judged with this prompt in natural-prompt (run npb-gate-opuslow); their prompts
             are checked to be identical, and their labels are reused.
  v2-tau2    tau2: the 232 tasks of tau2-tb4-pl's run tau2pl-r1 (696 cells).
  v2-tb4     Terminal-Bench 4.0.0: the 66 tasks of tb4pl-r1 (198 cells).

For every cell the old prompt is rebuilt from the same rubric and task text and must match the old run's
hash; the v2 prompt is then built from the same inputs, so only the prompt differs.

    python experiments/benchmarks/pl-relabel-v2/make_prompts.py
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
from adele.annotation.prompts import build_annotation_prompt, build_annotation_prompt_v2

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BENCH = HERE.parent
JUDGE_IO = ROOT.parents[1] / "judge-io"
AGENT = BENCH / "natural-prompt/adele-judge-v2-low.md"
JUDGES = {"opus-low": "Claude Code subagent 'adele-judge-v2-low' (tools: Read, Write; omitClaudeMd; effort low), "
                      "model alias 'opus'"}
INSTRUCTION = "Prompt file: {prompt_file}\nResponse file: {response_file}"


def sha256(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def git(*args: str) -> str:
    return subprocess.run(["git", "-C", str(ROOT), *args], capture_output=True, text=True, check=True).stdout.strip()


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def write_run(run_id: str, cells: list[tuple], catalog, source: str) -> None:
    """cells: (benchmark, instance_id, file_id, demand, family, old_prompt_sha256, task_text)."""
    io, labels = JUDGE_IO / run_id, HERE / "labels" / run_id
    for d in (io / "prompts", io / "responses" / "opus-low", labels):
        d.mkdir(parents=True, exist_ok=True)
    rows = []
    for bench, iid, fid, dim, fam, old_sha, text in cells:
        r = catalog[dim]
        old = build_annotation_prompt(demand_name=r.full_name, rubric_content=r.content, task_instance=text)
        assert sha256(old.encode("utf-8")) == old_sha, f"{fid}@{dim}: inputs differ from {source}"
        new = build_annotation_prompt_v2(r.full_name, r.content, text)
        (io / "prompts" / f"{fid}@{dim}.txt").write_text(new, encoding="utf-8")
        rows.append({"benchmark": bench, "instance_id": iid, "file_id": fid, "demand": dim, "family": fam,
                     "old_prompt_sha256": old_sha, "prompt_sha256": sha256(new.encode("utf-8"))})
    pd.DataFrame(rows).to_csv(labels / "prompts_index.csv", index=False)
    run = {
        "run_id": run_id,
        "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "repo_commit": git("rev-parse", "HEAD"),
        "repo_dirty_tracked_files": git("status", "--porcelain", "--untracked-files=no").splitlines(),
        "benchmark": sorted({r["benchmark"] for r in rows}),
        "design": {"n_tasks": len({r["file_id"] for r in rows}), "dims": ["PLp", "PLe", "PLs"],
                   "n_prompts": len(rows), "judges": JUDGES},
        "prompt": {"builder": "adele.annotation.prompts.build_annotation_prompt_v2",
                   "builder_file_sha256": sha256((ROOT / "src/adele/annotation/prompts.py").read_bytes()),
                   "inputs_checked_against": source},
        "judge_agent": {"file": str(AGENT.relative_to(ROOT)), "sha256": sha256(AGENT.read_bytes())},
        "judge_instruction": INSTRUCTION,
        "judge_instruction_sha256": sha256(INSTRUCTION.encode("utf-8")),
        "judge_io": os.path.relpath(io, ROOT),
        "sampling": "harness defaults; snapshot cannot be pinned for subagents; effort is set in the agent file",
    }
    (labels / "run.json").write_text(json.dumps(run, indent=2) + "\n")
    print(f"{run_id}: {len(rows)} prompts")


def main() -> None:
    catalog = load_active_catalog()

    # SWE-bench: task text as in swebench-pl; the gate's v2 prompts must equal natural-prompt's variant B.
    inst = pd.read_parquet(ROOT / "data/instances/instances_swe-bench-verified.parquet").set_index("instance_id")
    gate = pd.read_csv(BENCH / "natural-prompt/labels/npb-gate-opuslow/prompts_index.csv", dtype={"instance_id": str})
    for r in gate.itertuples(index=False):
        text = inst.loc[r.instance_id, "prompt"]
        rub = catalog[r.demand]
        assert sha256(build_annotation_prompt_v2(rub.full_name, rub.content, text).encode("utf-8")) == r.prompt_sha256
    r1 = pd.read_csv(BENCH / "swebench-pl/labels/swepl-r1-low/prompts_index.csv", dtype={"instance_id": str})
    write_run("v2-swe", [("swe-bench-verified", r.instance_id, r.instance_id, r.demand, r.family, r.prompt_sha256,
                          inst.loc[r.instance_id, "prompt"]) for r in r1.itertuples(index=False)],
              catalog, "swebench-pl/labels/swepl-r1-low")

    # tau2 and Terminal-Bench: task text exactly as in tau2-tb4-pl.
    t2 = load("t2_make_prompts", BENCH / "tau2-tb4-pl/make_prompts.py")
    _, text = t2.build_sample()
    for run_id, src in (("v2-tau2", "tau2pl-r1"), ("v2-tb4", "tb4pl-r1")):
        idx = pd.read_csv(BENCH / f"tau2-tb4-pl/labels/{src}/prompts_index.csv", dtype={"instance_id": str})
        write_run(run_id, [(r.benchmark, r.instance_id, r.file_id, r.demand, r.family, r.prompt_sha256, text[r.file_id])
                           for r in idx.itertuples(index=False)], catalog, f"tau2-tb4-pl/labels/{src}")


if __name__ == "__main__":
    main()
