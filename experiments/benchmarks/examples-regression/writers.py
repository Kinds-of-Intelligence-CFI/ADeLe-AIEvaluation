"""Which model wrote each answer of an examples-regression run (as plp-candidate/lab-regression/writers.py).

A safety classifier can stop the registered judge mid-answer, and Claude Code may then finish the
call with another model. This script matches every answer file in <judge_io>/responses/<judge>/ to
the Write call that produced it (same SHA-256) in the judge transcripts of the judging session, and
writes labels/<run>/writers.csv: judge, file_id, writer_model, calls (judge calls made for the cell
and judge) and classifier_stops. It also lists answers written by a model other than the judge's
registered one; those are moved to responses_fallback/ and the cell is judged once more.

    python experiments/benchmarks/examples-regression/writers.py --run exreg-1 \
        --transcripts ~/.claude/projects/<project>/<session>/subagents
"""

import argparse
import hashlib
import json
import re
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
STOP = "stopped by a safety classifier"
MODELS = {"opus-low": "claude-opus-5-5"}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--transcripts", required=True, type=Path)
    args = ap.parse_args()
    run = json.loads((HERE / f"labels/{args.run}/run.json").read_text())
    index = pd.read_csv(HERE / f"labels/{args.run}/prompts_index.csv")
    io = (ROOT / run["judge_io"]).resolve()

    writes, calls, stops = {}, {}, {}
    for f in args.transcripts.glob("agent-*.jsonl"):
        with open(f, encoding="utf-8") as fh:
            lines = fh.readlines()
        m = re.search(rf"{re.escape(str(io))}/responses/([\w-]+)/(\w+)@ER\.txt", lines[0]) if lines else None
        if not m:
            continue
        key = (m.group(1), m.group(2))
        calls[key] = calls.get(key, 0) + 1
        stops[key] = stops.get(key, 0) + any(STOP in line for line in lines)
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
            path = io / "responses" / judge / f"{rec.file_id}@ER.txt"
            if not path.exists():
                continue
            key = (judge, rec.file_id)
            match = [w for w in writes.get(hashlib.sha256(path.read_bytes()).hexdigest(), []) if w[2] == key]
            assert match, f"{key}: no Write call produced this file"
            rows.append({"judge": judge, "file_id": rec.file_id, "writer_model": max(match)[1],
                         "calls": calls[key], "classifier_stops": stops[key]})
    out = pd.DataFrame(rows)
    out.to_csv(HERE / f"labels/{args.run}/writers.csv", index=False)
    other = out[[not str(m).startswith(MODELS[re.sub(r"-r\d+$", "", j)]) for j, m in zip(out["judge"], out["writer_model"])]]
    print(out.groupby("judge")["writer_model"].value_counts().to_dict())
    print("cells with a classifier stop:", int((out["classifier_stops"] > 0).sum()),
          "| cells called more than once:", int((out["calls"] > 1).sum()))
    print("written by another model:", [f"{j}/{f}@ER" for j, f in zip(other["judge"], other["file_id"])] or "none")


if __name__ == "__main__":
    main()
