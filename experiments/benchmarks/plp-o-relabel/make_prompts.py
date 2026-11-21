"""Pin the runs of plp-o-relabel (PREREGISTRATION.md): PLp relabelled with the adopted text O, everything else as in
pl-relabel-v2 (v2 prompt, Opus low, same task texts).

  o-swe    SWE-bench Verified: the 398 non-gate tasks of pl-relabel-v2's run v2-swe. The 44 gate tasks were judged with
           this exact prompt in plp-b2's run o-swe-gate; their prompts are checked to be identical, and the labels reused.
  o-tau2   tau2: the 232 tasks of v2-tau2.
  o-tb4    Terminal-Bench 4.0.0: the 66 tasks of v2-tb4.

For every cell the pl-relabel-v2 PLp prompt is rebuilt from the previous PLp text (git, OLD_COMMIT) and must match its
stored hash; the new prompt is then built from the catalog's PLp (O), so only the rubric differs.

    python experiments/benchmarks/plp-o-relabel/make_prompts.py
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
from adele.annotation.prompts import build_annotation_prompt_v2

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BENCH = HERE.parent
JUDGE_IO = ROOT.parents[1] / "judge-io"
AGENT = BENCH / "natural-prompt/adele-judge-v2-low.md"
OLD_COMMIT = "062c5af"  # last commit before O was adopted (92f28fc)
RUBRIC = "src/adele/rubrics/data_v2/Paolo_Pablo/PLp.txt"
JUDGES = {"opus-low": "Claude Code subagent 'adele-judge-v2-low' (tools: Read, Write; omitClaudeMd; effort low), "
                      "model alias 'opus'"}
INSTRUCTION = "Prompt file: {prompt_file}\nResponse file: {response_file}"


def sha256(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def git(*args: str) -> str:
    return subprocess.run(["git", "-C", str(ROOT), *args], capture_output=True, text=True, check=True).stdout


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def body(text: str) -> str:
    """Rubric content as the catalog serves it: the file without its '# Name' header."""
    return text.split("\n", 2)[2].rstrip("\n")


def main() -> None:
    plp = load_active_catalog()["PLp"]
    old_text = body(git("show", f"{OLD_COMMIT}:{RUBRIC}"))
    assert sha256(git("show", f"{OLD_COMMIT}:{RUBRIC}").encode()).startswith("de98ab35"), "old text is not the pre-O PLp"
    assert plp.content.rstrip("\n") != old_text and sha256(Path(plp.file_path).read_bytes()).startswith("322674ef")
    t2 = load("t2_make_prompts", BENCH / "tau2-tb4-pl/make_prompts.py")
    _, t2_text = t2.build_sample()
    inst = pd.read_parquet(ROOT / "data/instances/instances_swe-bench-verified.parquet").set_index("instance_id")

    # The gate's O prompts (plp-b2 o-swe-gate) must equal what this script would build.
    gate = pd.read_csv(BENCH / "plp-b2/labels/o-swe-gate/prompts_index.csv", dtype={"instance_id": str})
    for r in gate.itertuples(index=False):
        p = build_annotation_prompt_v2(plp.full_name, plp.content, inst.loc[r.instance_id, "prompt"])
        assert sha256(p.encode("utf-8")) == r.prompt_sha256, r.instance_id

    for run_id, src in (("o-swe", "v2-swe"), ("o-tau2", "v2-tau2"), ("o-tb4", "v2-tb4")):
        idx = pd.read_csv(BENCH / f"pl-relabel-v2/labels/{src}/prompts_index.csv", dtype={"instance_id": str})
        idx = idx[idx["demand"] == "PLp"]
        io, labels = JUDGE_IO / run_id, HERE / "labels" / run_id
        for d in (io / "prompts", io / "responses" / "opus-low", labels):
            d.mkdir(parents=True, exist_ok=True)
        rows = []
        for r in idx.itertuples(index=False):
            text = inst.loc[r.instance_id, "prompt"] if run_id == "o-swe" else t2_text[r.file_id]
            old = build_annotation_prompt_v2(plp.full_name, old_text, text)
            assert sha256(old.encode("utf-8")) == r.prompt_sha256, f"{r.file_id}: inputs differ from {src}"
            new = build_annotation_prompt_v2(plp.full_name, plp.content, text)
            (io / "prompts" / f"{r.file_id}@PLp.txt").write_text(new, encoding="utf-8")
            rows.append({"benchmark": r.benchmark, "instance_id": r.instance_id, "file_id": r.file_id, "demand": "PLp",
                         "family": r.family, "old_prompt_sha256": r.prompt_sha256,
                         "prompt_sha256": sha256(new.encode("utf-8"))})
        pd.DataFrame(rows).to_csv(labels / "prompts_index.csv", index=False)
        run = {
            "run_id": run_id,
            "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "repo_commit": git("rev-parse", "HEAD").strip(),
            "repo_dirty_tracked_files": git("status", "--porcelain", "--untracked-files=no").splitlines(),
            "benchmark": sorted({r["benchmark"] for r in rows}),
            "design": {"n_tasks": len(rows), "dims": ["PLp"], "n_prompts": len(rows), "judges": JUDGES},
            "rubric": {"file": RUBRIC, "sha256": sha256(Path(plp.file_path).read_bytes()),
                       "previous": f"{OLD_COMMIT}:{RUBRIC}"},
            "prompt": {"builder": "adele.annotation.prompts.build_annotation_prompt_v2",
                       "builder_file_sha256": sha256((ROOT / "src/adele/annotation/prompts.py").read_bytes()),
                       "inputs_checked_against": f"pl-relabel-v2/labels/{src}"},
            "judge_agent": {"file": str(AGENT.relative_to(ROOT)), "sha256": sha256(AGENT.read_bytes())},
            "judge_instruction": INSTRUCTION,
            "judge_instruction_sha256": sha256(INSTRUCTION.encode("utf-8")),
            "judge_io": os.path.relpath(io, ROOT),
            "sampling": "harness defaults; snapshot cannot be pinned for subagents; effort is set in the agent file",
        }
        (labels / "run.json").write_text(json.dumps(run, indent=2) + "\n")
        print(f"{run_id}: {len(rows)} prompts; every previous prompt matched its stored hash")


if __name__ == "__main__":
    main()
