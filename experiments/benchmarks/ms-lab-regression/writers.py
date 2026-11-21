"""Which model wrote each answer of an MS lab-regression run (as plp-candidate/lab-regression/writers.py).

A safety classifier can stop the registered judge mid-answer, and Claude Code may then finish the call
with another model. This script matches every answer file in <judge_io>/responses/<judge>/ to the Write
call that produced it (same SHA-256) in the judge transcripts of the judging session, and writes
labels/<run>/writers.csv: judge, file_id, writer_model, calls (judge calls made for the cell and judge)
and classifier_stops. Only answers written by claude-opus-5-5 count.

With --set-aside, every answer written by another model is moved to <judge_io>/responses_fallback/<judge>/
and a retry relay (relays/retry-<judge>.txt) is written, so the cell is judged once more. A cell already
set aside once is not set aside again: if its second answer is also a fallback, it has no label.

    python experiments/benchmarks/ms-lab-regression/writers.py --run ms-labreg1 \
        --transcripts ~/.claude/projects/<project>/<session>/subagents [--set-aside]
"""

import argparse
import hashlib
import json
import re
import shutil
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
STOPS = ("stopped by a safety classifier", "safeguards flagged this message")
MODEL = "claude-opus-5-5"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--transcripts", required=True, type=Path)
    ap.add_argument("--set-aside", action="store_true", help="move fallback answers aside and write retry relays")
    args = ap.parse_args()
    run = json.loads((HERE / f"labels/{args.run}/run.json").read_text())
    index = pd.read_csv(HERE / f"labels/{args.run}/prompts_index.csv")
    io = (ROOT / run["judge_io"]).resolve()

    writes, calls, stops = {}, {}, {}
    for f in args.transcripts.expanduser().glob("agent-*.jsonl"):
        with open(f, encoding="utf-8") as fh:
            lines = fh.readlines()
        m = re.search(rf"{re.escape(str(io))}/responses/([\w-]+)/(\w+)@(?:MSm|MSc)\.txt", lines[0]) if lines else None
        if not m:
            continue
        key = (m.group(1), m.group(2))
        calls[key] = calls.get(key, 0) + 1
        stops[key] = stops.get(key, 0) + any(s in line for line in lines for s in STOPS)
        for line in lines:
            r = json.loads(line)
            if r.get("type") != "assistant":
                continue
            for b in r["message"].get("content", []):
                if isinstance(b, dict) and b.get("type") == "tool_use" and b.get("name") == "Write" \
                        and "content" in b["input"]:
                    h = hashlib.sha256(b["input"]["content"].encode("utf-8")).hexdigest()
                    writes.setdefault(h, []).append((r.get("timestamp"), r["message"].get("model"), key))

    rows = []
    for judge in run["design"]["judges"]:
        for rec in index.itertuples(index=False):
            path = io / "responses" / judge / f"{rec.file_id}@{rec.rubric}.txt"
            if not path.exists():
                continue
            key = (judge, rec.file_id)
            match = [w for w in writes.get(hashlib.sha256(path.read_bytes()).hexdigest(), []) if w[2] == key]
            assert match, f"{key}: no Write call produced this file"
            rows.append({"judge": judge, "file_id": rec.file_id, "rubric": rec.rubric,
                         "writer_model": max(match)[1], "calls": calls[key], "classifier_stops": stops[key]})
    out = pd.DataFrame(rows, columns=["judge", "file_id", "rubric", "writer_model", "calls", "classifier_stops"])
    out.drop(columns=["rubric"]).to_csv(HERE / f"labels/{args.run}/writers.csv", index=False)
    other = out[~out["writer_model"].astype(str).str.startswith(MODEL)]
    print(out.groupby("judge")["writer_model"].value_counts().to_dict())
    print("cells with a classifier stop:", int((out["classifier_stops"] > 0).sum()),
          "| cells called more than once:", int((out["calls"] > 1).sum()))
    print("written by another model:", [f"{j}/{f}@{d}" for j, f, d in
                                        zip(other["judge"], other["file_id"], other["rubric"])] or "none")
    if args.set_aside and not other.empty:
        retry = {}
        for r in other.itertuples(index=False):
            cell = f"{r.file_id}@{r.rubric}"
            dest = io / "responses_fallback" / r.judge / f"{cell}.txt"
            if dest.exists():
                print(f"{r.judge}/{cell}: already set aside once; no label")
                continue
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(io / "responses" / r.judge / f"{cell}.txt", dest)
            retry.setdefault(r.judge, []).append(cell)
        for judge, cells in retry.items():
            msg = "\n".join(["Model: opus", f"I/O folder: {io}", f"Judge folder name: {judge}",
                             f"Cells ({len(cells)}):", *cells])
            (io / "relays" / f"retry-{judge}.txt").write_text(msg, encoding="utf-8")
            print(f"set aside {len(cells)} answers of {judge}; retry relay: {io / 'relays' / f'retry-{judge}.txt'}")


if __name__ == "__main__":
    main()
