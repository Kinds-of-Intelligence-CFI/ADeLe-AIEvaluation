"""Shared builder for the shareable releases of a study: <study>/release/ (a Hugging Face dataset layout).

  release/README.md        the data card: <study>/DATACARD.md with {placeholders} filled
  release/tasks.csv        the study's tasks.csv (every task, with outcomes, flags and the clean-set decision)
  release/labels.csv       one row per (task, rubric): level and full provenance
  release/labels_wide.csv  tasks.csv plus one column per rubric
  release/rubrics.csv      one row per rubric text used: code, generation, name, file, sha256, and the runs that used it
  release/MANIFEST.tsv     sha256 of every file above

Labels are the current ("merged") ones, the same for every release (`current_labels`): every rubric from relabel-v2
(runs relabel-v2 and relabel-v2-long; the examples review of 2026-10-04, d4ec2ec), and where relabel-v3 re-judged a
cell (PLp at 3-5 after the synthesis example moved to Level 4, d6cc9ca; MSm at 4-5 on the social sets), its label
replaces the relabel-v2 one. The merge is one-sided: only cells at 3-5 were re-judged (relabel-v3/RESULTS.md). So
PLp comes from two texts; each label row names its run, and rubrics.csv names the runs of each text.

Inputs are committed files only: the study's tasks.csv and the labels.csv and manifest.json of `adele mass` runs. Only
valid answers written by claude-opus-5-5 are exported. No task text. `build` is used by deepswe-clean, frontierswe-pl
and programbench-pl export.py; `current_labels` and `rubrics` by all seven.
"""

import hashlib
import json
import subprocess
from pathlib import Path

import pandas as pd

BENCH = Path(__file__).resolve().parent
ROOT = BENCH.parents[1]
RUNS = BENCH / "mass-annotation/runs"
MODEL = "claude-opus-5-5"
FILES = ["README.md", "tasks.csv", "labels.csv", "labels_wide.csv", "rubrics.csv"]
BASE = {"relabel-v2": ["relabel-v2", "relabel-v2-long"]}
OVERRIDE = {"relabel-v3": ["relabel-v3-plp", "relabel-v3-plp-long", "relabel-v3-plp-eqbench4",
                           "relabel-v3-plp-cooperbench", "relabel-v3-plp-gamearena", "relabel-v3-msm-eqbench4",
                           "relabel-v3-msm-gamearena"]}
KEY = ["benchmark", "instance_id", "rubric"]


def sha256(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def commit() -> str:
    return subprocess.run(["git", "-C", str(ROOT), "rev-parse", "--short", "HEAD"], capture_output=True, text=True,
                          check=True).stdout.strip()


def frozen(run: str) -> dict:
    return json.loads((RUNS / run / "manifest.json").read_text())["frozen"]


def _read(studies: dict[str, list[str]], benchmarks: list[str], dims: list[str]) -> pd.DataFrame:
    rows = []
    for study, runs in studies.items():
        for run in runs:
            lab = pd.read_csv(RUNS / run / "labels.csv", dtype={"instance_id": str})
            lab = lab[lab["benchmark"].isin(benchmarks) & lab["valid"].astype(bool)
                      & lab["writer_model"].astype(str).str.startswith(MODEL)
                      & lab["rubric_ref"].isin([f"v2/{x}" for x in dims])]
            rows.append(pd.DataFrame({
                "benchmark": lab["benchmark"], "instance_id": lab["instance_id"], "rubric": lab["rubric_ref"],
                "level": lab["level"].astype(int), "judge_model": lab["writer_model"], "judge_effort": lab["effort"],
                "judge_harness": lab["backend"].replace({"subagent": "claude-code-subagent"}),
                "prompt_builder": frozen(run)["prompt"]["function"], "prompt_sha256": lab["prompt_sha256"],
                "response_sha256": lab["response_sha256"], "study": study, "run": run}))
    out = pd.concat(rows, ignore_index=True)
    assert not out.duplicated(KEY).any(), f"{list(studies)}: a cell has two labels"
    return out


def current_labels(benchmarks: list[str], dims: list[str]) -> pd.DataFrame:
    """The current label of every (benchmark, instance_id, rubric) cell: relabel-v3 where it re-judged the cell,
    relabel-v2 elsewhere. One row per cell, with provenance."""
    out = pd.concat([_read(OVERRIDE, benchmarks, dims), _read(BASE, benchmarks, dims)], ignore_index=True)
    return out.drop_duplicates(KEY, keep="first").sort_values(KEY).reset_index(drop=True)


def rubrics(lab: pd.DataFrame, dims: list[str]) -> pd.DataFrame:
    """rubrics.csv: one row per (rubric, text) behind the labels in `lab`, with the runs that used that text."""
    rows = {}
    for run in sorted(lab["run"].unique()):
        pins = frozen(run)["rubrics"]
        for ref in lab.loc[lab["run"] == run, "rubric"].unique():
            p = pins[ref]
            r = rows.setdefault((ref, p["sha256"]), {
                "rubric": ref, "code": ref.removeprefix("v2/"), "generation": "v2", "name": p["full_name"],
                "file": p["file"], "sha256": p["sha256"], "runs": []})
            r["runs"].append(run)
    rows = sorted(({**r, "runs": ";".join(r["runs"])} for r in rows.values()),
                  key=lambda r: (dims.index(r["code"]), r["runs"]))
    return pd.DataFrame(rows)


def release_labels(here: Path, benchmark: str, dims: list[str]) -> pd.DataFrame:
    """Current labels of one study's kept tasks (tasks.csv `keep`), without the benchmark column."""
    tasks = pd.read_csv(here / "tasks.csv", dtype={"instance_id": str})
    keep = tasks.loc[tasks["keep"].astype(bool), "instance_id"] if "keep" in tasks else tasks["instance_id"]
    lab = current_labels([benchmark], dims)
    return lab[lab["instance_id"].isin(set(keep))].drop(columns="benchmark").reset_index(drop=True)


def wide(lab: pd.DataFrame, dims: list[str], index: str | list[str] = "instance_id") -> pd.DataFrame:
    """One column per rubric (`v2/<code>`), in the order of `dims`."""
    return lab.pivot(index=index, columns="rubric", values="level").reindex(columns=[f"v2/{x}" for x in dims])


def build(here: Path, lab: pd.DataFrame, dims: list[str], fill: dict[str, str]) -> None:
    """Write release/ from the study's tasks.csv and the labels `lab` (from `release_labels`)."""
    out = here / "release"
    out.mkdir(exist_ok=True)
    tasks = pd.read_csv(here / "tasks.csv", dtype={"instance_id": str}).set_index("instance_id")
    assert set(lab["instance_id"]) <= set(tasks.index)
    rub = rubrics(lab, dims)
    lab.to_csv(out / "labels.csv", index=False)
    cols = [f"v2/{x}" for x in dims if f"v2/{x}" in set(rub["rubric"])]
    tasks.join(wide(lab, dims)[cols]).reset_index().to_csv(out / "labels_wide.csv", index=False)
    tasks.reset_index().to_csv(out / "tasks.csv", index=False)
    rub.to_csv(out / "rubrics.csv", index=False)

    counts = lab.groupby("rubric").size()
    fill = {"{n_tasks}": str(len(tasks)), "{n_labels}": str(len(lab)), "{commit}": commit(),
            "{label_counts}": ", ".join(f"{r.removeprefix('v2/')} {counts.get(r, 0)}" for r in cols), **fill}
    card = (here / "DATACARD.md").read_text(encoding="utf-8")
    for k, v in fill.items():
        card = card.replace(k, v)
    assert "{" not in card.split("---", 2)[2].replace("{{", ""), "unfilled placeholder in DATACARD.md"
    (out / "README.md").write_text(card, encoding="utf-8")
    (out / "MANIFEST.tsv").write_text("file\tsha256\n" + "".join(
        f"{f}\t{sha256((out / f).read_bytes())}\n" for f in FILES))
    print(f"{here.name}/release/: {len(tasks)} tasks, {len(lab)} labels ({fill['{label_counts}']})")
