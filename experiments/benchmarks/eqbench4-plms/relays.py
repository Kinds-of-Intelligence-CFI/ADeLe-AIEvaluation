"""Print the next relay messages for the eq4-outcome judging (eq-outcome-dispatcher), and record them as sent.

A cell is due when it has no answer file and was never sent; `--resend CELL ...` marks cells to send once more (a
relay that died, or an answer written by another model; one recorded retry each). Sent cells are appended to
judge-io/eq4-outcome/sent.csv (cell, relay, time), so a cell is never printed twice by accident.

    python experiments/benchmarks/eqbench4-plms/relays.py --max 4 [--size 50] [--resend CELL ...]
"""

import argparse
import time
from pathlib import Path

import pandas as pd

IO = Path.home() / "Developer/ADELE/judge-io/eq4-outcome"
JUDGE = "opus-low"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--max", type=int, default=4)
    ap.add_argument("--size", type=int, default=50)
    ap.add_argument("--resend", nargs="*", default=[])
    args = ap.parse_args()
    cells = pd.read_csv(IO / "cells.csv")["cell"].tolist()
    log = IO / "sent.csv"
    sent = pd.read_csv(log) if log.exists() else pd.DataFrame(columns=["cell", "relay", "time"])
    answered = {p.stem for p in (IO / "responses" / JUDGE).glob("*.txt")}
    for c in args.resend:
        assert c in cells and (sent["cell"] == c).sum() == 1, f"{c}: unknown, unsent or already retried"
    due = list(args.resend) + [c for c in cells if c not in answered and c not in set(sent["cell"])]
    stamp = time.strftime("%Y%m%dT%H%M%S")
    rows = []
    for k in range(args.max):
        batch = due[k * args.size:(k + 1) * args.size]
        if not batch:
            break
        relay = f"eq4o-{stamp}-{k + 1:02d}"
        print(f"=== {relay} ({len(batch)} cells) ===")
        print(f"Model: opus\nI/O folder: {IO}\nJudge folder name: {JUDGE}\nCells ({len(batch)}):")
        print("\n".join(batch))
        print("=== end ===")
        rows += [{"cell": c, "relay": relay, "time": stamp} for c in batch]
    if not rows:
        print("nothing to send")
        return
    pd.concat([sent, pd.DataFrame(rows)]).to_csv(log, index=False)


if __name__ == "__main__":
    main()
