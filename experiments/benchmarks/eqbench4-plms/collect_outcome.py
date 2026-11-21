"""Collect the outcome-judge answers of eqbench4-plms (make_outcome_prompts.py) into labels/eq4-outcome/outcomes.csv.

For every cell in judge-io/eq4-outcome/cells.csv with an answer in responses/opus-low/: the parsed CORE (yes / partly
/ no) and A<k> (yes / no) lines, and the model that wrote the answer. Writer: the answer file is matched (SHA-256) to
the Write call that produced it in the judge transcripts Claude Code keeps for the judging session, as
rivercross-v2/writers.py does; a safety classifier can hand a call to another model. Only answers written by
claude-opus-5-5 that parse completely are valid.

Columns: cell, scenario, model, repeat, core, n_items, n_voiced, items (e.g. "yny"), writer_model, calls,
classifier_stops, valid.

    python experiments/benchmarks/eqbench4-plms/collect_outcome.py \
        --transcripts ~/.claude/projects/<project>/<session>/subagents
"""

import argparse
import hashlib
import json
import re
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
IO = Path.home() / "Developer/ADELE/judge-io/eq4-outcome"
JUDGE = "opus-low"
MODEL = "claude-opus-5-5"
STOPS = ("stopped by a safety classifier", "safeguards flagged this message")
LINE = re.compile(r"^(CORE|A\d+):\s*(yes|partly|no)\b", re.I | re.M)


def parse(text: str, n_items: int) -> dict | None:
    got = {k.upper(): v.lower() for k, v in LINE.findall(text)}
    keys = ["CORE"] + [f"A{k}" for k in range(1, n_items + 1)]
    if set(got) != set(keys) or got["CORE"] not in ("yes", "partly", "no") \
            or any(got[k] not in ("yes", "no") for k in keys[1:]):
        return None
    items = "".join(got[k][0] for k in keys[1:])
    return {"core": got["CORE"], "n_items": n_items, "n_voiced": items.count("y"), "items": items}


def transcripts(folder: Path) -> tuple[dict, dict, dict]:
    writes, calls, stops = {}, {}, {}
    for f in folder.glob("agent-*.jsonl"):
        lines = f.read_text(encoding="utf-8").splitlines()
        if not lines or f"{IO}/prompts/" not in lines[0]:
            continue
        cell = lines[0].split(f"{IO}/prompts/")[1].split(".txt")[0]
        calls[cell] = calls.get(cell, 0) + 1
        stops[cell] = stops.get(cell, 0) + any(s in x for x in lines for s in STOPS)
        for x in lines:
            r = json.loads(x)
            if r.get("type") != "assistant":
                continue
            for b in r["message"].get("content", []):
                if isinstance(b, dict) and b.get("type") == "tool_use" and b.get("name") == "Write" \
                        and "content" in b["input"]:
                    h = hashlib.sha256(b["input"]["content"].encode("utf-8")).hexdigest()
                    writes.setdefault(h, []).append((r.get("timestamp"), r["message"].get("model"), cell))
    return writes, calls, stops


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--transcripts", required=True, type=Path)
    args = ap.parse_args()
    cells = pd.read_csv(IO / "cells.csv")
    writes, calls, stops = transcripts(args.transcripts)
    rows = []
    for c in cells.itertuples(index=False):
        path = IO / "responses" / JUDGE / f"{c.cell}.txt"
        row = {"cell": c.cell, "scenario": c.scenario, "model": c.model, "repeat": c.repeat,
               "calls": calls.get(c.cell, 0), "classifier_stops": stops.get(c.cell, 0)}
        if path.exists():
            prompt = (IO / "prompts" / f"{c.cell}.txt").read_text(encoding="utf-8")
            n_items = len(re.findall(r"^A\d+: yes \| no", prompt, re.M))
            match = [w for w in writes.get(hashlib.sha256(path.read_bytes()).hexdigest(), []) if w[2] == c.cell]
            row["writer_model"] = max(match)[1] if match else "unmatched"
            row.update(parse(path.read_text(encoding="utf-8"), n_items) or {})
        rows.append(row)
    out = pd.DataFrame(rows).reindex(columns=["cell", "scenario", "model", "repeat", "core", "n_items", "n_voiced",
                                              "items", "writer_model", "calls", "classifier_stops"])
    out["valid"] = out["core"].notna() & out["writer_model"].astype(str).str.startswith(MODEL)
    (HERE / "labels/eq4-outcome").mkdir(parents=True, exist_ok=True)
    out.to_csv(HERE / "labels/eq4-outcome/outcomes.csv", index=False)
    print(f"{len(out)} cells; answered {int(out['writer_model'].notna().sum())}; valid {int(out['valid'].sum())}; "
          f"writers {out['writer_model'].value_counts().to_dict()}; classifier stops "
          f"{int((out['classifier_stops'] > 0).sum())}; unparsed {int((out['writer_model'].notna() & out['core'].isna()).sum())}")


if __name__ == "__main__":
    main()
