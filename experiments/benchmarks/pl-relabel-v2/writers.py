"""Which model wrote each answer of a pl-relabel-v2 run (as plp-candidate/writers.py).

A safety classifier can stop the registered judge mid-answer, and Claude Code may then finish the
call with another model. This script matches every answer file in <judge_io>/responses/<judge>/ to
the Write call that produced it (same SHA-256) in the judge transcripts Claude Code keeps for the
judging session, and writes labels/<run>/writers.csv: file_id, demand, writer_model, calls (judge
calls made for the cell) and classifier_stops (calls in which a safety classifier stopped a
response). The transcripts stay on the judging machine; writers.csv is committed.

    python experiments/benchmarks/pl-relabel-v2/writers.py --run v2-swe \
        --transcripts ~/.claude/projects/<project>/<session>/subagents
"""

import argparse
import hashlib
import json
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
# Opus stops mid-answer and may recover; Sonnet 5.5 ends the call with an API error and no answer.
STOPS = ("stopped by a safety classifier", "safeguards flagged this message")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--transcripts", required=True, type=Path)
    args = ap.parse_args()
    run = json.loads((HERE / f"labels/{args.run}/run.json").read_text())
    index = pd.read_csv(HERE / f"labels/{args.run}/prompts_index.csv", dtype={"instance_id": str})
    io = (ROOT / run["judge_io"]).resolve()

    writes, calls, stops = {}, {}, {}
    for f in args.transcripts.glob("agent-*.jsonl"):
        with open(f, encoding="utf-8") as fh:
            lines = fh.readlines()
        if f"{io}/prompts/" not in lines[0]:
            continue
        cell = lines[0].split(f"{io}/prompts/")[1].split(".txt")[0]
        calls[cell] = calls.get(cell, 0) + 1
        stops[cell] = stops.get(cell, 0) + any(s in line for line in lines for s in STOPS)
        for line in lines:
            r = json.loads(line)
            if r.get("type") != "assistant":
                continue
            for b in r["message"].get("content", []):
                if isinstance(b, dict) and b.get("type") == "tool_use" and b.get("name") == "Write" \
                        and "content" in b["input"]:
                    h = hashlib.sha256(b["input"]["content"].encode("utf-8")).hexdigest()
                    writes.setdefault(h, []).append((r.get("timestamp"), r["message"].get("model"), cell))

    rows = []
    for judge in run["design"]["judges"]:
        for rec in index.itertuples(index=False):
            cell = f"{rec.file_id}@{rec.demand}"
            path = io / "responses" / judge / f"{cell}.txt"
            if not path.exists():
                continue
            match = [w for w in writes.get(hashlib.sha256(path.read_bytes()).hexdigest(), []) if w[2] == cell]
            assert match, f"{cell}: no Write call produced this file"
            rows.append({"file_id": rec.file_id, "demand": rec.demand, "judge": judge,
                         "writer_model": max(match)[1], "calls": calls[cell], "classifier_stops": stops[cell]})
    out = pd.DataFrame(rows)
    out.to_csv(HERE / f"labels/{args.run}/writers.csv", index=False)
    # Every cell, answered or not: calls made and calls stopped by a safeguard.
    cells = [f"{r.file_id}@{r.demand}" for r in index.itertuples(index=False)]
    pd.DataFrame({"cell": cells, "calls": [calls.get(c, 0) for c in cells],
                  "safeguard_stops": [stops.get(c, 0) for c in cells]}).to_csv(HERE / f"labels/{args.run}/calls.csv", index=False)
    print(out["writer_model"].value_counts().to_dict(), "| cells with a classifier stop:",
          int((out["classifier_stops"] > 0).sum()), "| cells called more than once:", int((out["calls"] > 1).sum()))


if __name__ == "__main__":
    main()
