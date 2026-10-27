"""Pin run clean-swe (PREREGISTRATION.md): PLp, PLe and PLs for the clean-set tasks that have no PL labels yet.

Same judge, prompt and task text as the existing labels: v2 prompt, the catalog's rubrics (PLp = text O), Opus low.
Before writing, it rebuilds every existing PL prompt of the clean set from the same inputs and checks it against the
stored hash, so the new cells differ from the old ones only in which task they are.

    python experiments/benchmarks/swebench-clean/make_prompts.py
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
BENCH = HERE.parent
JUDGE_IO = ROOT.parents[1] / "judge-io"
RUN = "clean-swe"
DIMS = ["PLp", "PLe", "PLs"]
AGENT = BENCH / "natural-prompt/adele-judge-v2-low.md"
# Where the existing PL labels of SWE-bench Verified come from (dimension -> runs).
SOURCES = {"PLp": ["plp-o-relabel/labels/o-swe", "plp-b2/labels/o-swe-gate"],
           "PLe": ["pl-relabel-v2/labels/v2-swe", "natural-prompt/labels/npb-gate-opuslow"],
           "PLs": ["pl-relabel-v2/labels/v2-swe", "natural-prompt/labels/npb-gate-opuslow"]}


def sha256(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def git(*args: str) -> str:
    return subprocess.run(["git", "-C", str(ROOT), *args], capture_output=True, text=True, check=True).stdout.strip()


def existing(dim: str) -> pd.DataFrame:
    idx = pd.concat(pd.read_csv(BENCH / s / "prompts_index.csv", dtype={"instance_id": str}) for s in SOURCES[dim])
    return idx[idx["demand"] == dim].drop_duplicates("instance_id")


def main() -> None:
    cat = load_active_catalog()
    tasks = pd.read_csv(HERE / "tasks.csv")
    keep = set(tasks.loc[tasks["keep"], "instance_id"])
    inst = pd.read_parquet(ROOT / "data/instances/instances_swe-bench-verified.parquet").set_index("instance_id")
    build = lambda dim, iid: build_annotation_prompt_v2(cat[dim].full_name, cat[dim].content, inst.loc[iid, "prompt"])

    missing = set()
    for dim in DIMS:
        old = existing(dim)
        old = old[old["instance_id"].isin(keep)]
        for r in old.itertuples(index=False):
            assert sha256(build(dim, r.instance_id).encode("utf-8")) == r.prompt_sha256, f"{r.instance_id}@{dim} changed"
        missing |= keep - set(old["instance_id"])
        print(f"{dim}: {len(old)} existing prompts reproduce their hashes")

    io, labels = JUDGE_IO / RUN, HERE / "labels" / RUN
    for d in (io / "prompts", io / "responses" / "opus-low", labels):
        d.mkdir(parents=True, exist_ok=True)
    rows = []
    for iid in sorted(missing):
        for dim in DIMS:
            p = build(dim, iid)
            (io / "prompts" / f"{iid}@{dim}.txt").write_text(p, encoding="utf-8")
            rows.append({"benchmark": "swe-bench-verified", "instance_id": iid, "file_id": iid, "demand": dim,
                         "family": "v2", "prompt_sha256": sha256(p.encode("utf-8"))})
    pd.DataFrame(rows).to_csv(labels / "prompts_index.csv", index=False)
    run = {"run_id": RUN, "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
           "repo_commit": git("rev-parse", "HEAD"),
           "repo_dirty_tracked_files": git("status", "--porcelain", "--untracked-files=no").splitlines(),
           "benchmark": ["swe-bench-verified"],
           "design": {"n_tasks": len(missing), "dims": DIMS, "n_prompts": len(rows),
                      "judges": {"opus-low": "Claude Code subagent 'adele-judge-v2-low' (tools: Read, Write; "
                                             "omitClaudeMd; effort low), model alias 'opus'"}},
           "rubrics": {d: {"file": str(Path(cat[d].file_path).relative_to(ROOT)),
                           "sha256": sha256(Path(cat[d].file_path).read_bytes())} for d in DIMS},
           "prompt": {"builder": "adele.annotation.prompts.build_annotation_prompt_v2",
                      "builder_file_sha256": sha256((ROOT / "src/adele/annotation/prompts.py").read_bytes()),
                      "existing_prompts_checked_against": SOURCES},
           "judge_agent": {"file": str(AGENT.relative_to(ROOT)), "sha256": sha256(AGENT.read_bytes())},
           "judge_instruction": "Prompt file: {prompt_file}\nResponse file: {response_file}",
           "judge_io": os.path.relpath(io, ROOT),
           "sampling": "harness defaults; snapshot cannot be pinned for subagents; effort is set in the agent file"}
    (labels / "run.json").write_text(json.dumps(run, indent=2) + "\n")
    print(f"{RUN}: {len(missing)} tasks, {len(rows)} prompts")


if __name__ == "__main__":
    main()
