"""Build the items, the 4-gram check, the prompts and the relay files of the MSm/MSc lab regression.

See PREREGISTRATION.md. No rubric text changes: MSm and MSc are judged as the catalog loads them, with
the v2 prompt (build_annotation_prompt_v2), by Opus at effort low (adele-judge-v2-low), three repeats
per item (judge folders opus-low-r1 to -r3), relayed by judge-dispatcher-v2-low.
Item sets (items.csv), each item judged on one rubric, MSm or MSc:
  P  placement: every example bullet of MSm and MSc, on its own rubric, with every Examples block stripped
  F  foreign examples: PLp, PLe and PLs bullets at Levels 3 to 5, each on MSm and on MSc
  S  sibling split: MSm's bullets at Levels 3 to 5 on MSc, and MSc's on MSm (descriptive, no target)
  L  lab items: r30, r36, r60, r69 and r75 items (lab_items.csv); r70's human labels ride on r75's texts
  B  battery-v1: the items that bear on MSc, and the anchors, pure PL and pure MSc items on MSm (battery_targets.csv)
Every item outside P is checked for shared word 4-grams against every example bullet of the rubric it is
judged on. An item with any shared 4-gram is void and is not judged (JUDGING.md rule 4).
Prompts go to $ADELE_JUDGE_IO/<run>/prompts/<id>@<rubric>.txt (default ~/Developer/ADELE/judge-io). Ids are
opaque and shuffled. Relay messages for judge-dispatcher-v2-low go to <run>/relays/, at most 50 cells each.

    python experiments/benchmarks/ms-lab-regression/make_prompts.py                         # pass 1, ms-labreg1
    python experiments/benchmarks/ms-lab-regression/make_prompts.py --replicate ITEM [...]  # pass 2, ms-labreg2
"""

import argparse
import hashlib
import io
import json
import os
import random
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from adele.agentic import load_active_catalog
from adele.annotation.prompts import build_annotation_prompt_v2

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
JUDGE_IO = Path(os.environ.get("ADELE_JUDGE_IO", "~/Developer/ADELE/judge-io")).expanduser()
LAB = "7159671"  # rubrics/v2-lab-record (on origin): battery-v1, r36, r60, r69, r70, r75
PL_REBUILT = ROOT / "experiments/benchmarks/plp-candidate/lab-regression/reconstructed_items.csv"
AGENT = ROOT / "experiments/benchmarks/natural-prompt/adele-judge-v2-low.md"
DISPATCHER = ROOT / "experiments/benchmarks/natural-prompt/judge-dispatcher-v2-low.md"
JUDGES = {f"opus-low-r{k}": f"adele-judge-v2-low, model alias 'opus'; repeat {k}" for k in (1, 2, 3)}
INSTRUCTION = "Prompt file: {prompt_file}\nResponse file: {response_file}"
RUBRICS = ("MSm", "MSc")
FOREIGN = ("PLp", "PLe", "PLs")
RELAY_MAX = 50
ID_CHARS = "abcdefghjkmnpqrstuvwxyz23456789"
SEED = 20261002
COLS = ["item_id", "set", "rubric", "own_dim", "own_level", "target", "check", "registered", "stored",
        "label_kind", "judged_as", "rebuilt", "round", "status", "fourgram_hits", "fourgram_shared", "source", "text"]


def sha256(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def git(*args: str) -> str:
    return subprocess.run(["git", "-C", str(ROOT), *args], capture_output=True, text=True, check=True).stdout


def lab_csv(path: str) -> pd.DataFrame:
    return pd.read_csv(io.StringIO(git("show", f"{LAB}:labs/rubric-qa/{path}")))


def bullets(content: str) -> list[tuple[int, str]]:
    """(level, text) for every example bullet, in file order."""
    out, level = [], None
    for line in content.splitlines():
        m = re.match(r"Level (\d):", line)
        if m:
            level = int(m.group(1))
        elif line.startswith("* "):
            out.append((level, line[2:].strip()))
    return out


def strip_examples(content: str) -> str:
    """The rubric with every Examples block removed (the r25 placement design)."""
    kept = [l for l in content.splitlines() if l.strip() != "Examples:" and not l.startswith("* ")]
    return "\n".join(kept)


def fourgrams(text: str) -> set[tuple[str, ...]]:
    w = re.findall(r"[a-z0-9]+", text.lower())
    return {tuple(w[i:i + 4]) for i in range(len(w) - 3)}


def numbered(content: str, dim: str) -> list[tuple[str, int, str]]:
    """(id stem, level, text) for every bullet, e.g. ('MSm-L3-1', 3, ...)."""
    out, counts = [], {}
    for level, text in bullets(content):
        counts[level] = counts.get(level, 0) + 1
        out.append((f"{dim}-L{level}-{counts[level]}", level, text))
    return out


def build_items(catalog) -> pd.DataFrame:
    rows = []
    row = dict.fromkeys(COLS, "")
    for dim in RUBRICS:  # P
        for stem, level, text in numbered(catalog[dim].content, dim):
            rows.append({**row, "item_id": f"P-{stem}", "set": "P", "rubric": dim, "own_dim": dim,
                         "own_level": level, "target": level, "check": "within1", "label_kind": "lab",
                         "rebuilt": False, "source": f"{dim}.txt example bullet", "text": text})
    for dim in FOREIGN:  # F
        for stem, level, text in numbered(catalog[dim].content, dim):
            if level >= 3:
                for rub in RUBRICS:
                    rows.append({**row, "item_id": f"F-{stem}-on-{rub}", "set": "F", "rubric": rub, "own_dim": dim,
                                 "own_level": level, "target": 2, "check": "<=2", "label_kind": "lab",
                                 "rebuilt": False, "round": "r34" if rub == "MSc" else "",
                                 "source": f"{dim}.txt example bullet" + (
                                     "; r34 found no PL example at 3+ on MSc (older texts)" if rub == "MSc"
                                     else "; no lab record on MSm"), "text": text})
    for dim, other in (("MSm", "MSc"), ("MSc", "MSm")):  # S
        for stem, level, text in numbered(catalog[dim].content, dim):
            if level >= 3:
                rows.append({**row, "item_id": f"S-{stem}-on-{other}", "set": "S", "rubric": other, "own_dim": dim,
                             "own_level": level, "check": "none", "label_kind": "lab", "rebuilt": False,
                             "source": f"{dim}.txt example bullet (descriptive: co-loading is allowed)", "text": text})
    lab = pd.read_csv(HERE / "lab_items.csv", dtype=str, keep_default_na=False)  # L
    check_lab_provenance(lab)
    for r in lab.itertuples(index=False):
        rows.append({**row, "item_id": r.item_id, "set": "L", "rubric": r.rubric, "own_dim": r.rubric,
                     "target": int(r.target), "check": r.check, "registered": r.registered, "stored": r.stored,
                     "label_kind": r.label_kind, "judged_as": r.judged_as, "rebuilt": r.rebuilt == "True",
                     "round": r.round, "source": r.source, "text": r.text})
    battery = lab_csv("battery-v1/items.csv").set_index("item_id")["task"]  # B
    prereg = lab_csv("battery-v1/prereg.csv").set_index("item_id")
    r36 = lab_csv("r36/labels.csv")
    r36_msc = r36[r36["dim"] == "MSc"].groupby("item_id")["assigned"].median()
    for r in pd.read_csv(HERE / "battery_targets.csv", dtype=str, keep_default_na=False).itertuples(index=False):
        if r.rubric == "MSc":  # registered and stored levels must match the lab record
            assert int(r.registered) == int(prereg.loc[r.battery_id, "MSc"]), r.battery_id
            assert int(r.stored) == int(r36_msc[r.battery_id]), r.battery_id
        rows.append({**row, "item_id": f"B-{r.battery_id}-on-{r.rubric}", "set": "B", "rubric": r.rubric,
                     "own_dim": prereg.loc[r.battery_id, "family"], "target": int(r.target), "check": r.check,
                     "registered": r.registered, "stored": r.stored, "label_kind": "lab", "rebuilt": False,
                     "round": "battery-v1",
                     "source": f"battery-v1 items.csv ({LAB}); stored = r36 median; {r.note}",
                     "text": battery[r.battery_id]})
    items = pd.DataFrame(rows, columns=COLS)
    assert items["item_id"].is_unique
    # 4-gram independence against every example bullet of the rubric the item is judged on.
    hits, shared, status = [], [], []
    for r in items.itertuples(index=False):
        if r.set == "P":
            hits.append("")
            shared.append("n/a: the item is a bullet of this file, and the rubric shown has no examples")
            status.append("judged")
            continue
        found = [(lvl, i, sorted(fourgrams(r.text) & fourgrams(t)))
                 for i, (lvl, t) in enumerate(bullets(catalog[r.rubric].content), 1)]
        found = [f for f in found if f[2]]
        hits.append(sum(len(s) for _, _, s in found))
        shared.append("; ".join(f"bullet {i} (Level {lvl}): " + " | ".join(" ".join(g) for g in s)
                                for lvl, i, s in found))
        status.append("void" if found else ("alias" if r.judged_as else "judged"))
    items["fourgram_hits"], items["fourgram_shared"], items["status"] = hits, shared, status
    for r in items[items["status"] == "alias"].itertuples(index=False):
        src = items.set_index("item_id").loc[r.judged_as]
        assert src["text"] == r.text and src["rubric"] == r.rubric, r.item_id
    return items


def check_lab_provenance(lab: pd.DataFrame) -> None:
    """Persisted texts must be found verbatim where the source says; rebuilt r36 texts equal the PL rebuild."""
    seal = " ".join(git("show", f"{LAB}:labs/rubric-qa/r75/sealed_predictions_r75.md").split())
    for r in lab[lab["round"] == "r75"].itertuples(index=False):
        assert f"{r.item_id[-2:]}: {r.text}" in seal, f"{r.item_id}: text not in the r75 seal"
    pl = pd.read_csv(PL_REBUILT).set_index("item_id")["text"]
    for r in lab[lab["round"] == "r36"].itertuples(index=False):
        assert pl[f"M-{r.item_id[-2:]}"] == r.text, f"{r.item_id}: differs from the PL regression's rebuild"
    r36 = lab_csv("r36/labels.csv")
    for r in lab[lab["round"] == "r36"].itertuples(index=False):
        got = r36[(r36["dim"] == "MSc") & (r36["item_id"] == r.item_id[-2:])]["assigned"].median()
        assert int(got) == int(r.stored), r.item_id
    cset = lab_csv("r30/cset.csv").set_index("item_id")["task"]  # r30's pairs, judged in r33 (arm MSc_new)
    h2h = lab_csv("r33/headtohead_labels.csv")
    h2h = h2h[(h2h["set"] == "C") & (h2h["arm"] == "MSc_new")].groupby("item_id")["assigned"].median()
    r30 = lab[lab["round"] == "r30"]
    assert len(r30) == len(cset) == 8
    for r in r30.itertuples(index=False):
        assert cset[r.item_id[-2:]] == r.text, f"{r.item_id}: text differs from r30/cset.csv"
        assert int(h2h[r.item_id[-2:]]) == int(r.stored), r.item_id


def prompt_for(catalog, item) -> str:
    content = catalog[item.rubric].content
    rubric = strip_examples(content) if item.set == "P" else content
    p = build_annotation_prompt_v2(catalog[item.rubric].full_name, rubric, item.text)
    if item.set == "P":
        assert "Examples:" not in p and not any(t in p for _, t in bullets(content) if t != item.text)
    else:
        assert content in p
    return p


def opaque_ids(n: int, rng: random.Random, taken: set[str]) -> list[str]:
    out = []
    while len(out) < n:
        i = "".join(rng.choice(ID_CHARS) for _ in range(5))
        if i not in taken:
            taken.add(i)
            out.append(i)
    return out


def write_run(run_id: str, cells: list[dict], note: dict) -> None:
    io_dir, labels = JUDGE_IO / run_id, HERE / "labels" / run_id
    answered = [p for j in JUDGES for p in (io_dir / "responses" / j).glob("*.txt")]
    assert not answered, f"{run_id} already has {len(answered)} answers; refusing to overwrite a judged run"
    for d in [io_dir / "prompts", io_dir / "relays", labels] + [io_dir / "responses" / j for j in JUDGES]:
        d.mkdir(parents=True, exist_ok=True)
    for old in list((io_dir / "prompts").glob("*.txt")) + list((io_dir / "relays").glob("*.txt")):
        old.unlink()  # an unjudged earlier build of this run
    for c in cells:
        (io_dir / "prompts" / f"{c['file_id']}@{c['rubric']}.txt").write_text(c.pop("prompt"), encoding="utf-8")
    pd.DataFrame(cells).to_csv(labels / "prompts_index.csv", index=False)
    relays = []
    for judge in JUDGES:
        cell_ids = [f"{c['file_id']}@{c['rubric']}" for c in cells]
        for k in range(0, len(cell_ids), RELAY_MAX):
            batch = cell_ids[k:k + RELAY_MAX]
            name = f"{judge}-{k // RELAY_MAX + 1:02d}"
            msg = "\n".join([f"Model: opus", f"I/O folder: {io_dir}", f"Judge folder name: {judge}",
                             f"Cells ({len(batch)}):", *batch])
            (io_dir / "relays" / f"{name}.txt").write_text(msg, encoding="utf-8")
            relays.append({"relay": name, "judge": judge, "cells": len(batch)})
    pd.DataFrame(relays).to_csv(labels / "relays.csv", index=False)
    run = {
        "run_id": run_id,
        "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "repo_commit": git("rev-parse", "HEAD").strip(),
        "repo_dirty_tracked_files": git("status", "--porcelain", "--untracked-files=no").splitlines(),
        "design": {"n_cells": len(cells), "dims": list(RUBRICS), "judges": JUDGES,
                   "n_calls": len(cells) * len(JUDGES), "relays": len(relays), "relay_max_cells": RELAY_MAX},
        **note,
        "prompt": {"builder": "adele.annotation.prompts.build_annotation_prompt_v2",
                   "builder_file_sha256": sha256((ROOT / "src/adele/annotation/prompts.py").read_bytes())},
        "judge_agent": {"file": str(AGENT.relative_to(ROOT)), "sha256": sha256(AGENT.read_bytes())},
        "dispatcher_agent": {"file": str(DISPATCHER.relative_to(ROOT)), "sha256": sha256(DISPATCHER.read_bytes())},
        "judge_instruction": INSTRUCTION,
        "judge_instruction_sha256": sha256(INSTRUCTION.encode("utf-8")),
        "judge_io": os.path.relpath(io_dir, ROOT),
        "sampling": "harness defaults; snapshot cannot be pinned for subagents; effort is set in the agent file",
    }
    (labels / "run.json").write_text(json.dumps(run, indent=2) + "\n")
    print(f"{run_id}: {len(cells)} prompts x {len(JUDGES)} repeats = {len(cells) * len(JUDGES)} calls, "
          f"in {len(relays)} relays of at most {RELAY_MAX} cells ({io_dir / 'relays'})")


def taken_ids(exclude: str) -> set[str]:
    idx = [p for p in HERE.glob("labels/*/prompts_index.csv") if p.parent.name != exclude]
    return set(pd.concat(pd.read_csv(p) for p in idx)["file_id"]) if idx else set()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--replicate", nargs="+", metavar="ITEM", help="write pass 2 (ms-labreg2)")
    args = ap.parse_args()
    catalog = load_active_catalog()
    note = {"rubrics": {d: {"file": str(Path(catalog[d].file_path).relative_to(ROOT)),
                            "sha256": sha256(Path(catalog[d].file_path).read_bytes())} for d in RUBRICS + FOREIGN},
            "set_P": "every Examples block stripped from the rubric shown (r25 design)",
            "items": "ms-lab-regression/items.csv", "lab_record_commit": LAB}

    if args.replicate:  # pass 2: the pass-1 prompts of the listed items, under new ids
        r1 = pd.read_csv(HERE / "labels/ms-labreg1/prompts_index.csv")
        todo = r1[r1["item_id"].isin(args.replicate)]
        assert set(todo["item_id"]) == set(args.replicate), "unknown or unjudged item"
        rng = random.Random(SEED + 2)
        cells = []
        for r, new in zip(todo.sample(frac=1, random_state=SEED + 2).itertuples(index=False),
                          opaque_ids(len(todo), rng, taken_ids("ms-labreg2"))):
            p = (JUDGE_IO / "ms-labreg1/prompts" / f"{r.file_id}@{r.rubric}.txt").read_text(encoding="utf-8")
            assert sha256(p.encode("utf-8")) == r.prompt_sha256
            cells.append({"file_id": new, "item_id": r.item_id, "set": r.set, "rubric": r.rubric,
                          "prompt_sha256": r.prompt_sha256, "pass1_file_id": r.file_id, "prompt": p})
        write_run("ms-labreg2", cells, {**note, "pass": 2, "replicates": "ms-labreg1"})
        return

    items = build_items(catalog)
    items.to_csv(HERE / "items.csv", index=False)
    judged = items[items["status"] == "judged"]
    cells = []
    for r in judged.itertuples(index=False):
        p = prompt_for(catalog, r)
        cells.append({"item_id": r.item_id, "set": r.set, "rubric": r.rubric,
                      "prompt_sha256": sha256(p.encode("utf-8")), "prompt": p})
    rng = random.Random(SEED)
    rng.shuffle(cells)
    for c, i in zip(cells, opaque_ids(len(cells), rng, taken_ids("ms-labreg1"))):
        c["file_id"] = i
    cells = [{"file_id": c["file_id"], **{k: v for k, v in c.items() if k != "file_id"}} for c in cells]
    write_run("ms-labreg1", cells, {**note, "pass": 1})
    print(items.groupby(["set", "rubric", "status"]).size().to_string())
    void = items[items["status"] == "void"]
    print("void (4-gram):", "none" if void.empty else "")
    for r in void.itertuples(index=False):
        print(f"  {r.item_id}: {r.fourgram_shared}")


if __name__ == "__main__":
    main()
