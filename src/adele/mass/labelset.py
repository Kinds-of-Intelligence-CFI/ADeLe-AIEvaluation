"""Label sets: which runs make up a set of labels, declared in a small TOML file reviewed like code.

    name = "current"
    description = "What these labels are for."
    model = "claude-opus-5-5"     # only valid answers written by this model count
    [[layers]]                    # earlier layers win: a cell takes its label from the first layer that has it
    name = "relabel-v3"
    runs = ["relabel-v3-plp", "relabel-v3-msm-eqbench4"]
    [[layers]]
    name = "relabel-v2"
    runs = ["relabel-v2", "relabel-v2-long"]

A cell is (benchmark, instance_id, rubric ref). Within a layer a cell may have only one label. Every label keeps its
provenance, plus two version columns read from its run's manifest: ``rubric_sha256`` (the rubric text judged) and
``task_version`` (the sha256 of the frozen instance frame the task text came from). ``export`` writes the set in the
layout of a Hugging Face dataset: long labels, a wide table, the rubric texts' hashes and a manifest.
"""

import hashlib
import json
import subprocess
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional, Tuple

import pandas as pd

from adele.mass.collect import is_requested
from adele.mass.pin import RUNS_ROOT
from adele.mass.spec import REPO_ROOT

LABELSETS_ROOT = REPO_ROOT / "experiments" / "benchmarks" / "mass-annotation" / "labelsets"
KEY = ["benchmark", "instance_id", "rubric"]
COLUMNS = KEY + ["level", "judge_model", "judge_effort", "judge_harness", "prompt_builder", "prompt_sha256",
                 "response_sha256", "rubric_sha256", "task_version", "study", "run"]


class LabelSetError(ValueError):
    pass


@dataclass
class LabelSet:
    name: str
    description: str
    model: str
    layers: List[Tuple[str, List[str]]]
    path: Path
    sha256: str

    @property
    def runs(self) -> List[str]:
        return [r for _, runs in self.layers for r in runs]


def load_labelset(ref: str | Path, runs_root: Optional[Path] = None) -> LabelSet:
    """Load a label set by path, or by name under ``labelsets/``; every run it names must exist."""
    p = Path(ref)
    if not p.is_file():
        p = LABELSETS_ROOT / f"{ref}.toml"
    if not p.is_file():
        raise LabelSetError(f"no label set at {ref} (nor {p})")
    data = p.read_bytes()
    d = tomllib.loads(data.decode("utf-8"))
    unknown = set(d) - {"name", "description", "model", "layers"}
    if unknown:
        raise LabelSetError(f"{p}: unknown keys {sorted(unknown)}")
    if not d.get("name") or not d.get("model") or not d.get("layers"):
        raise LabelSetError(f"{p}: name, model and at least one [[layers]] are required")
    layers = []
    for layer in d["layers"]:
        if set(layer) != {"name", "runs"} or not layer["runs"]:
            raise LabelSetError(f"{p}: each layer needs exactly a name and a non-empty runs list")
        layers.append((layer["name"], list(layer["runs"])))
    runs = [r for _, rs in layers for r in rs]
    if len(set(runs)) != len(runs):
        raise LabelSetError(f"{p}: a run is listed twice")
    root = Path(runs_root or RUNS_ROOT)
    missing = [r for r in runs if not (root / r / "labels.csv").is_file()]
    if missing:
        raise LabelSetError(f"{p}: runs without labels.csv: {missing}")
    return LabelSet(name=d["name"], description=d.get("description", ""), model=d["model"], layers=layers, path=p,
                    sha256=hashlib.sha256(data).hexdigest())


def _run_labels(run: str, root: Path, model: str, study: str) -> pd.DataFrame:
    frozen = json.loads((root / run / "manifest.json").read_text())["frozen"]
    lab = pd.read_csv(root / run / "labels.csv", dtype={"instance_id": str})
    lab = lab[lab["valid"].astype(bool) & lab["writer_model"].astype(str).map(lambda w: is_requested(w, model))]
    benches = frozen["tasks"]["benchmarks"]
    return pd.DataFrame({
        "benchmark": lab["benchmark"], "instance_id": lab["instance_id"], "rubric": lab["rubric_ref"],
        "level": lab["level"].astype(int), "judge_model": lab["writer_model"], "judge_effort": lab["effort"],
        "judge_harness": lab["backend"].replace({"subagent": "claude-code-subagent"}),
        "prompt_builder": frozen["prompt"]["function"], "prompt_sha256": lab["prompt_sha256"],
        "response_sha256": lab["response_sha256"],
        "rubric_sha256": lab["rubric_ref"].map(lambda r: frozen["rubrics"][r]["sha256"]),
        "task_version": lab["benchmark"].map(lambda b: benches[b]["frame_sha256"]),
        "study": study, "run": run}, columns=COLUMNS)


def labels(ls: LabelSet, benchmarks: Optional[Iterable[str]] = None, rubrics: Optional[Iterable[str]] = None,
           runs_root: Optional[Path] = None) -> pd.DataFrame:
    """One row per cell: the label of the first layer that has the cell, with provenance and version columns."""
    root = Path(runs_root or RUNS_ROOT)
    frames = []
    for study, runs in ls.layers:
        layer = pd.concat([_run_labels(r, root, ls.model, study) for r in runs], ignore_index=True)
        if benchmarks is not None:
            layer = layer[layer["benchmark"].isin(list(benchmarks))]
        if rubrics is not None:
            layer = layer[layer["rubric"].isin(list(rubrics))]
        dup = layer[layer.duplicated(KEY, keep=False)]
        if len(dup):
            raise LabelSetError(f"layer {study!r}: {len(dup)} rows share a cell, e.g. {dup[KEY].iloc[0].tolist()}")
        frames.append(layer)
    out = pd.concat(frames, ignore_index=True)
    return out.drop_duplicates(KEY, keep="first").sort_values(KEY).reset_index(drop=True)


def wide(lab: pd.DataFrame) -> pd.DataFrame:
    """One row per task, one column per rubric ref (sorted)."""
    return lab.pivot(index=["benchmark", "instance_id"], columns="rubric", values="level") \
        .reindex(columns=sorted(lab["rubric"].unique())).astype("Int64").reset_index()


def rubric_texts(lab: pd.DataFrame, runs_root: Optional[Path] = None) -> pd.DataFrame:
    """One row per (rubric ref, text) behind the labels, with the runs that used that text."""
    root = Path(runs_root or RUNS_ROOT)
    rows = {}
    for run in sorted(lab["run"].unique()):
        pins = json.loads((root / run / "manifest.json").read_text())["frozen"]["rubrics"]
        for ref in sorted(lab.loc[lab["run"] == run, "rubric"].unique()):
            p = pins[ref]
            r = rows.setdefault((ref, p["sha256"]), {"rubric": ref, "name": p["full_name"], "file": p["file"],
                                                      "sha256": p["sha256"], "runs": []})
            r["runs"].append(run)
    return pd.DataFrame([{**r, "runs": ";".join(r["runs"])} for _, r in sorted(rows.items())])


def export(ls: LabelSet, out: Path, fmt: str = "csv", benchmarks: Optional[Iterable[str]] = None,
           rubrics: Optional[Iterable[str]] = None, runs_root: Optional[Path] = None) -> pd.DataFrame:
    """Write labels, labels_wide, rubrics (``.csv`` or ``.parquet``) and MANIFEST.tsv into ``out``."""
    if fmt not in ("csv", "parquet"):
        raise LabelSetError("fmt must be 'csv' or 'parquet'")
    lab = labels(ls, benchmarks, rubrics, runs_root)
    out.mkdir(parents=True, exist_ok=True)
    tables = {"labels": lab, "labels_wide": wide(lab), "rubrics": rubric_texts(lab, runs_root)}
    files = []
    for name, df in tables.items():
        f = out / f"{name}.{fmt}"
        df.to_csv(f, index=False) if fmt == "csv" else df.to_parquet(f, index=False)
        files.append(f)
    commit = subprocess.run(["git", "-C", str(REPO_ROOT), "rev-parse", "--short", "HEAD"], capture_output=True,
                            text=True).stdout.strip()
    meta = [("labelset", ls.name), ("labelset_sha256", ls.sha256), ("commit", commit),
            ("n_labels", str(len(lab))), ("n_tasks", str(len(tables["labels_wide"])))]
    (out / "MANIFEST.tsv").write_text(
        "".join(f"# {k}\t{v}\n" for k, v in meta) + "file\tsha256\n"
        + "".join(f"{f.name}\t{hashlib.sha256(f.read_bytes()).hexdigest()}\n" for f in files))
    return lab
