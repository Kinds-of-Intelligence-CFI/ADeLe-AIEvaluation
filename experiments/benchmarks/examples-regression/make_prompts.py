"""Prompts of the examples regression (see PREREGISTRATION.md): do the reviewed examples (d4ec2ec) change how the
judge labels anything other than the examples themselves?

Two texts per rubric (PLp, PLe, PLs, MSm, MSc): `old` is the file at d4ec2ec~1 and `new` the file at d4ec2ec, both as
the catalog shows them. Sets:
  B  battery-v1: the lab's 36 standing items (lab record 7159671), both texts, one label each
  R  60 real tasks, 10 each from SWE-bench Verified, DeepSWE, Terminal-Bench 4.0, tau2 (retail), EQ-Bench 4 and
     CooperBench (coop prompts), seeded: `new` once; the reference is the task's current Opus label (old text)
  N  20 of the R tasks (the first 3 or 4 drawn per set) again under `old`, to measure judge noise
Every B item is checked for shared word 4-grams against every example bullet of the new text; a shared 4-gram voids
it for that rubric. One prompt file per call (opaque ids), all shuffled into run exreg-1. Pass 2 (--pass2 ITEM:DIM
...) judges the named cells again under both texts, three repeats each, as run exreg-2.

    python experiments/benchmarks/examples-regression/make_prompts.py
    python experiments/benchmarks/examples-regression/make_prompts.py --pass2 B-D02:PLs R-...:MSc
"""

import argparse
import hashlib
import importlib.util
import io
import json
import random
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from adele.agentic import load_active_catalog
from adele.annotation.prompts import build_annotation_prompt_v2
from adele.mass.pin import load_instances
from adele.mass.spec import load_spec

HERE = Path(__file__).resolve().parent
BENCH = HERE.parent
ROOT = BENCH.parents[1]
JUDGE_IO = ROOT.parents[1] / "judge-io"
DIMS = ["PLp", "PLe", "PLs", "MSm", "MSc"]
NEW, LAB, SEED = "d4ec2ec", "7159671", 20261006
SETS = {"swe-bench-verified": ("pls-relabel", 4), "deepswe-v1.1": ("pls-relabel", 3),
        "terminal-bench-4.0.0": ("pls-relabel", 3), "tau2-retail": ("pls-relabel", 4),
        "eqbench4": ("eqbench4-plms", 3), "cooperbench": ("cooperbench-plms", 3)}
N_PER_SET = 10
ID_CHARS = "abcdefghjkmnpqrstuvwxyz23456789"


def git(*args: str) -> str:
    return subprocess.run(["git", "-C", str(ROOT), *args], capture_output=True, text=True, check=True).stdout


def shown(text: str) -> str:
    lines = text.splitlines()
    assert lines[0].startswith("# ") and lines[1] == ""
    return "\n".join(lines[2:]).rstrip("\n")


def bullets(text: str) -> list[str]:
    return [l[2:] for l in text.splitlines() if l.startswith("* ")]


def fourgrams(t: str) -> set:
    w = re.findall(r"[a-z0-9]+", t.lower())
    return {tuple(w[i:i + 4]) for i in range(len(w) - 3)}


def texts() -> dict:
    out = {}
    for d in DIMS:
        path = f"src/adele/rubrics/data_v2/Paolo_Pablo/{d}.txt"
        out[d] = {"old": shown(git("show", f"{NEW}~1:{path}")), "new": shown(git("show", f"{NEW}:{path}"))}
    cat = load_active_catalog()
    for d in DIMS:
        assert cat[d].content == out[d]["new"], f"{d}: the active text is not the reviewed text"
    return out


def opus_reference():
    spec = importlib.util.spec_from_file_location("jp", BENCH / "jev-pilot/analysis/analyse.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.opus_labels()


def opaque(n: int, rng: random.Random, taken: set) -> list[str]:
    out = []
    while len(out) < n:
        i = "".join(rng.choice(ID_CHARS) for _ in range(5))
        if i not in taken:
            taken.add(i)
            out.append(i)
    return out


def write_run(run_id: str, cells: list[dict], note: dict) -> None:
    io_dir, lab = JUDGE_IO / run_id, HERE / "labels" / run_id
    for d in (io_dir / "prompts", io_dir / "responses/opus-low", lab):
        d.mkdir(parents=True, exist_ok=True)
    for c in cells:
        (io_dir / "prompts" / f"{c['file_id']}@ER.txt").write_bytes(c.pop("prompt").encode("utf-8"))
    pd.DataFrame(cells).to_csv(lab / "prompts_index.csv", index=False)
    (lab / "run.json").write_text(json.dumps({
        "run_id": run_id, "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "repo_commit": git("rev-parse", "HEAD").strip(), "judge_io": f"../../judge-io/{run_id}",
        "design": {"n_cells": len(cells), "dims": DIMS,
                   "judges": {"opus-low": "adele-judge-v2-low via judge-dispatcher-v2-low, model opus"}},
        "texts": {"old": f"{NEW}~1", "new": NEW}, **note}, indent=2) + "\n")
    print(f"{run_id}: {len(cells)} prompts")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pass2", nargs="+", metavar="ITEM:DIM")
    args = ap.parse_args()
    tx = texts()
    cat = load_active_catalog()

    def prompt(d: str, arm: str, task: str) -> str:
        return build_annotation_prompt_v2(cat[d].full_name, tx[d][arm], task)

    if args.pass2:
        items = pd.read_csv(HERE / "items.csv", dtype={"instance_id": str}).set_index("item_id")
        inst = tasks_text()
        cells = []
        for spec in args.pass2:
            item, d = spec.split(":")
            r = items.loc[item]
            task = r["text"] if r["set"] == "B" else inst[(r["benchmark"], r["instance_id"])]
            cells += [{"item_id": item, "set": r["set"], "dim": d, "arm": a, "repeat": k, "prompt": prompt(d, a, task)}
                      for a in ("old", "new") for k in (1, 2, 3)]
        finish("exreg-2", cells, SEED + 2, {"pass": 2})
        return

    rows = []
    battery = pd.read_csv(io.StringIO(git("show", f"{LAB}:labs/rubric-qa/battery-v1/items.csv")))
    for r in battery.itertuples(index=False):
        void = [d for d in DIMS if any(fourgrams(r.task) & fourgrams(b) for b in bullets(tx[d]["new"]))]
        rows.append({"item_id": f"B-{r.item_id}", "set": "B", "text": r.task, "void_dims": ";".join(void)})
    ref = opus_reference()
    rng = random.Random(SEED)
    inst = tasks_text()
    for bench, (_, n_noise) in SETS.items():
        have = ref[ref["benchmark"] == bench]
        full = have.groupby("instance_id")["rubric"].nunique()
        ids = sorted(full[full == len(DIMS)].index)
        if bench == "cooperbench":
            ids = [i for i in ids if i.endswith("@coop")]
        pick = rng.sample(ids, N_PER_SET)
        for k, i in enumerate(pick):
            rows.append({"item_id": f"R-{bench}-{i}", "set": "R", "benchmark": bench, "instance_id": i,
                         "noise": k < n_noise, "void_dims": "",
                         **{f"ref_{d}": int(have[(have["instance_id"] == i) & (have["rubric"] == d)]["opus"].iloc[0])
                            for d in DIMS}})
    items = pd.DataFrame(rows)
    items.to_csv(HERE / "items.csv", index=False)
    cells = []
    for r in items.itertuples(index=False):
        void = set(str(r.void_dims).split(";")) if isinstance(r.void_dims, str) and r.void_dims else set()
        for d in DIMS:
            if d in void:
                continue
            if r.set == "B":
                cells += [{"item_id": r.item_id, "set": "B", "dim": d, "arm": a, "repeat": 1,
                           "prompt": prompt(d, a, r.text)} for a in ("old", "new")]
            else:
                task = inst[(r.benchmark, r.instance_id)]
                cells.append({"item_id": r.item_id, "set": "R", "dim": d, "arm": "new", "repeat": 1,
                              "prompt": prompt(d, "new", task)})
                if r.noise:
                    cells.append({"item_id": r.item_id, "set": "N", "dim": d, "arm": "old", "repeat": 1,
                                  "prompt": prompt(d, "old", task)})
    finish("exreg-1", cells, SEED + 1, {"pass": 1})
    print(items.groupby("set").size().to_string(), "\nvoid:", items["void_dims"].replace("", None).dropna().to_dict())


def tasks_text() -> dict:
    out = {}
    for spec in sorted({s for s, _ in SETS.values()}):
        inst, _ = load_instances(load_spec(BENCH / f"mass-annotation/specs/{spec}.toml", root=ROOT))
        out.update({(r.benchmark, r.instance_id): r.prompt for r in inst.itertuples(index=False)})
    return out


def finish(run_id: str, cells: list[dict], seed: int, note: dict) -> None:
    rng = random.Random(seed)
    rng.shuffle(cells)
    taken = set()
    for p in HERE.glob("labels/*/prompts_index.csv"):
        taken |= set(pd.read_csv(p)["file_id"])
    for c, i in zip(cells, opaque(len(cells), rng, taken)):
        c["file_id"] = i
        c["prompt_sha256"] = hashlib.sha256(c["prompt"].encode("utf-8")).hexdigest()
    write_run(run_id, [{"file_id": c.pop("file_id"), **c} for c in cells], note)


if __name__ == "__main__":
    main()
