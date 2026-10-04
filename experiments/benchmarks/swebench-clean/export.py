"""Build the shareable release of the SWE-bench Verified clean set: release/ (a Hugging Face dataset layout).

  release/README.md        the data card (Hugging Face front matter + documentation), written by this script
  release/tasks.csv        all 500 Verified tasks: solve counts, exclusion reasons, keep flag
  release/labels.csv       one row per (clean task, rubric): level and full provenance
  release/labels_wide.csv  one row per clean task: solve rate, time-to-fix bucket, one column per rubric
  release/rubrics.csv      every rubric used: code, generation, name, file, sha256
  release/MANIFEST.tsv     sha256 of every file above

Inputs are the committed study files only (tasks.csv, the labels_long.csv of each PLp and PLe source run, and the
labels.csv and manifest.json of mass run pls-relabel, which gives every PLs label with the PLs text of 2026-10-04), so
the release can be rebuilt at any commit. Only answers written by the requested judge (claude-opus-5-5) are exported.
No task text.

    uv run --extra annotate python experiments/benchmarks/swebench-clean/export.py
"""

import hashlib
import json
import subprocess
from pathlib import Path

import pandas as pd

from adele.agentic import load_active_catalog

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BENCH = HERE.parent
OUT = HERE / "release"
HF_REVISION = "c104f840cc67f8b6eec6f759ebc8b2693d585d4a"  # SWE-bench Verified, as in swebench-pl
MODEL = "claude-opus-5-5"
# (rubric, run folder, study that produced it). Order matters: the first source with a label wins.
SOURCES = [("PLp", "swebench-clean/labels/clean-swe", "swebench-clean"),
           ("PLp", "plp-o-relabel/labels/o-swe", "plp-o-relabel"),
           ("PLp", "plp-b2/labels/o-swe-gate", "plp-b2"),
           ("PLe", "swebench-clean/labels/clean-swe", "swebench-clean"),
           ("PLe", "pl-relabel-v2/labels/v2-swe", "pl-relabel-v2"),
           ("PLe", "natural-prompt/labels/npb-gate-opuslow", "natural-prompt")]
PLS_RUN = BENCH / "mass-annotation/runs/pls-relabel"  # every PLs label
BUCKETS = {"<15 min fix": 0, "15 min - 1 hour": 1, "1-4 hours": 2, ">4 hours": 3}


def sha256(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def git(*args: str) -> str:
    return subprocess.run(["git", "-C", str(ROOT), *args], capture_output=True, text=True, check=True).stdout.strip()


def main() -> None:
    from datasets import load_dataset

    OUT.mkdir(exist_ok=True)
    tasks = pd.read_csv(HERE / "tasks.csv")
    keep = tasks[tasks["keep"]].set_index("instance_id")
    cat = load_active_catalog()

    rows = []
    for dim, run, study in SOURCES:
        lab = pd.read_csv(BENCH / run / "labels_long.csv", dtype={"instance_id": str})
        lab = lab[(lab["demand"] == dim) & lab["valid"] & lab["writer_model"].astype(str).str.startswith(MODEL)]
        for r in lab[lab["instance_id"].isin(keep.index)].itertuples(index=False):
            rows.append({"instance_id": r.instance_id, "rubric": f"v2/{dim}", "level": int(r.level),
                         "judge_model": r.writer_model, "judge_effort": "low", "judge_harness": "claude-code-subagent",
                         "prompt_builder": "adele.annotation.prompts.build_annotation_prompt_v2",
                         "prompt_sha256": r.prompt_sha256, "response_sha256": r.response_sha256,
                         "study": study, "run": Path(run).name})
    pls = pd.read_csv(PLS_RUN / "labels.csv", dtype={"instance_id": str})
    pls = pls[(pls["benchmark"] == "swe-bench-verified") & (pls["rubric_ref"] == "v2/PLs") & pls["valid"].astype(bool)
              & pls["writer_model"].astype(str).str.startswith(MODEL)]
    frozen = json.loads((PLS_RUN / "manifest.json").read_text())["frozen"]
    for r in pls[pls["instance_id"].isin(keep.index)].itertuples(index=False):
        rows.append({"instance_id": r.instance_id, "rubric": r.rubric_ref, "level": int(r.level),
                     "judge_model": r.writer_model, "judge_effort": r.effort,
                     "judge_harness": "claude-code-subagent" if r.backend == "subagent" else r.backend,
                     "prompt_builder": frozen["prompt"]["function"], "prompt_sha256": r.prompt_sha256,
                     "response_sha256": r.response_sha256, "study": "pls-relabel", "run": r.run})
    labels = pd.DataFrame(rows).drop_duplicates(["instance_id", "rubric"], keep="first")
    missing = len(keep) * 3 - len(labels)
    assert missing == 0, f"{missing} clean-task labels missing"
    labels.sort_values(["instance_id", "rubric"]).to_csv(OUT / "labels.csv", index=False)

    meta = load_dataset("princeton-nlp/SWE-bench_Verified", split="test", revision=HF_REVISION).to_pandas()
    meta = meta.set_index("instance_id")
    wide = labels.pivot(index="instance_id", columns="rubric", values="level")
    wide = (keep[["solved_by", "of_entries", "solve_rate"]].join(meta["difficulty"].rename("time_to_fix"))
            .join(wide))
    wide["time_to_fix_bucket"] = wide["time_to_fix"].map(BUCKETS)
    wide.reset_index().to_csv(OUT / "labels_wide.csv", index=False)
    tasks.to_csv(OUT / "tasks.csv", index=False)

    rub = [{"rubric": f"v2/{d}", "code": d, "generation": "v2", "name": cat[d].full_name,
            "file": str(Path(cat[d].file_path).relative_to(ROOT)), "sha256": sha256(Path(cat[d].file_path).read_bytes())}
           for d in ("PLp", "PLe", "PLs")]
    rub[2]["sha256"] = frozen["rubrics"]["v2/PLs"]["sha256"]  # the PLs text pinned by pls-relabel
    pd.DataFrame(rub).to_csv(OUT / "rubrics.csv", index=False)

    card = (HERE / "DATACARD.md").read_text(encoding="utf-8")
    n = {"kept": len(keep), "labels": len(labels), "commit": git("rev-parse", "--short", "HEAD")}
    (OUT / "README.md").write_text(card.replace("{n_kept}", str(n["kept"])).replace("{n_labels}", str(n["labels"]))
                                   .replace("{commit}", n["commit"]), encoding="utf-8")
    files = ["README.md", "tasks.csv", "labels.csv", "labels_wide.csv", "rubrics.csv"]
    (OUT / "MANIFEST.tsv").write_text("file\tsha256\n" + "".join(
        f"{f}\t{sha256((OUT / f).read_bytes())}\n" for f in files))
    print(f"release/: {n['kept']} tasks, {n['labels']} labels")


if __name__ == "__main__":
    main()
