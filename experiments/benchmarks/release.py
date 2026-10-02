"""Shared builder for the shareable releases of a study: <study>/release/ (a Hugging Face dataset layout).

  release/README.md        the data card: <study>/DATACARD.md with {placeholders} filled
  release/tasks.csv        the study's tasks.csv (every task, with outcomes, flags and the clean-set decision)
  release/labels.csv       one row per (task, rubric): level and full provenance
  release/labels_wide.csv  tasks.csv plus one column per rubric
  release/rubrics.csv      every rubric used: code, generation, name, file, and the sha256 pinned by the runs
  release/MANIFEST.tsv     sha256 of every file above

Inputs are committed files only: the study's tasks.csv and the labels.csv and manifest.json of `adele mass` runs. Only
valid answers written by claude-opus-5-5 are exported. A rubric must be pinned to the same text by every run that used
it. No task text. Used by deepswe-clean, frontierswe-pl and programbench-pl export.py.
"""

import hashlib
import json
import subprocess
from pathlib import Path

import pandas as pd

BENCH = Path(__file__).resolve().parent
ROOT = BENCH.parents[1]
MODEL = "claude-opus-5-5"
FILES = ["README.md", "tasks.csv", "labels.csv", "labels_wide.csv", "rubrics.csv"]


def sha256(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def commit() -> str:
    return subprocess.run(["git", "-C", str(ROOT), "rev-parse", "--short", "HEAD"], capture_output=True, text=True,
                          check=True).stdout.strip()


def labels(benchmark: str, runs: dict[str, str], dims: list[str]) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Labels of `benchmark` from runs {run: study}, and the rubric pins. Each (task, rubric) must come from one run."""
    rows, pins = [], {}
    for run, study in runs.items():
        d = BENCH / "mass-annotation/runs" / run
        frozen = json.loads((d / "manifest.json").read_text())["frozen"]
        for ref, r in frozen["rubrics"].items():
            if ref.removeprefix("v2/") in dims:
                assert pins.setdefault(ref, r)["sha256"] == r["sha256"], f"{ref}: runs pin different texts"
        lab = pd.read_csv(d / "labels.csv", dtype={"instance_id": str})
        lab = lab[(lab["benchmark"] == benchmark) & lab["valid"].astype(bool)
                  & lab["writer_model"].astype(str).str.startswith(MODEL)
                  & lab["rubric_ref"].isin([f"v2/{x}" for x in dims])]
        rows.append(pd.DataFrame({
            "instance_id": lab["instance_id"], "rubric": lab["rubric_ref"], "level": lab["level"].astype(int),
            "judge_model": lab["writer_model"], "judge_effort": lab["effort"],
            "judge_harness": lab["backend"].replace({"subagent": "claude-code-subagent"}),
            "prompt_builder": frozen["prompt"]["function"], "prompt_sha256": lab["prompt_sha256"],
            "response_sha256": lab["response_sha256"], "study": study, "run": run}))
    out = pd.concat(rows, ignore_index=True).sort_values(["instance_id", "rubric"])
    assert not out.duplicated(["instance_id", "rubric"]).any()
    order = [f"v2/{x}" for x in dims]
    rubrics = pd.DataFrame([{"rubric": ref, "code": ref.removeprefix("v2/"), "generation": "v2",
                             "name": pins[ref]["full_name"], "file": pins[ref]["file"], "sha256": pins[ref]["sha256"]}
                            for ref in order if ref in pins])
    return out, rubrics


def build(here: Path, benchmark: str, runs: dict[str, str], dims: list[str], fill: dict[str, str]) -> None:
    out = here / "release"
    out.mkdir(exist_ok=True)
    tasks = pd.read_csv(here / "tasks.csv", dtype={"instance_id": str}).set_index("instance_id")
    lab, rubrics = labels(benchmark, runs, dims)
    assert set(lab["instance_id"]) <= set(tasks.index)
    lab.to_csv(out / "labels.csv", index=False)
    wide = lab.pivot(index="instance_id", columns="rubric", values="level").reindex(columns=list(rubrics["rubric"]))
    tasks.join(wide).reset_index().to_csv(out / "labels_wide.csv", index=False)
    tasks.reset_index().to_csv(out / "tasks.csv", index=False)
    rubrics.to_csv(out / "rubrics.csv", index=False)

    counts = lab.groupby("rubric").size()
    fill = {"{n_tasks}": str(len(tasks)), "{n_labels}": str(len(lab)), "{commit}": commit(),
            "{label_counts}": ", ".join(f"{r.removeprefix('v2/')} {counts.get(r, 0)}" for r in rubrics["rubric"]),
            **fill}
    card = (here / "DATACARD.md").read_text(encoding="utf-8")
    for k, v in fill.items():
        card = card.replace(k, v)
    assert "{" not in card.split("---", 2)[2].replace("{{", ""), "unfilled placeholder in DATACARD.md"
    (out / "README.md").write_text(card, encoding="utf-8")
    (out / "MANIFEST.tsv").write_text("file\tsha256\n" + "".join(
        f"{f}\t{sha256((out / f).read_bytes())}\n" for f in FILES))
    print(f"{here.name}/release/: {len(tasks)} tasks, {len(lab)} labels ({fill['{label_counts}']})")
