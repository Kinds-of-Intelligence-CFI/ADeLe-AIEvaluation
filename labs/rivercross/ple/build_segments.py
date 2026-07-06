"""Build flexible multi-step *segment* frames for PLe (method 2, generalised).

Reads the 6 captured interactive sessions and, for a chosen window-selection
strategy, emits one row per segment:

  frame_PLe_seg_<strategy>.csv   custom_id, prompt          (judge input; no LLM here)
  oracle_PLe_seg_<strategy>.csv  custom_id, length, d_phi, cost_to_go_{start,end},
                                 min_phi_dip, n_{optimal,lateral,backward,recovering,
                                 fatal}, n_illegal, reaches_goal

``d_phi`` (= Phi(s_j) - Phi(s_i), exact optimal net progress) is the credit-assignment
target the demand is meant to explain. This script makes NO model/LLM/judge calls --
it only builds frames and the solver oracle, so it is free to run.

Usage:
    python labs/rivercross/ple/build_segments.py [strategy ...] [--radius R] [--summary]
    # strategies: multilen (default), sliding, event, subgoal, all
"""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent  # ple/
PILOT = HERE.parent
sys.path.insert(0, str(PILOT))

from rivercross import (  # noqa: E402
    PuzzleSpec,
    build_spans,
    replay_session,
    segment_oracle,
    segment_prompt,
    solve,
)

SPECS = json.load(open(PILOT / "specs.json"))
SESS = PILOT / "interactive"
CIDS = [
    "chain-3-boat-1",
    "chain-5-boat-2",
    "complete-4-boat-3",
    "cycle-4-boat-2",
    "star-4-boat-2",
    "missionaries-cannibals-3",
]

ORACLE_COLS = [
    "custom_id", "instance", "length", "d_phi", "cost_to_go_start",
    "cost_to_go_end", "min_phi_dip", "n_optimal", "n_lateral", "n_backward",
    "n_recovering", "n_fatal", "n_illegal", "reaches_goal",
]


def build(strategy: str, *, radius: int = 1):
    frame_rows, oracle_rows = [], []
    for cid in CIDS:
        spec = PuzzleSpec.from_dict(SPECS[cid])
        data = json.load(open(SESS / f"{cid}.json"))
        sol = solve(spec)
        states, entries = replay_session(spec, data)
        spans = build_spans(sol, states, strategy, radius=radius)
        for (i, j) in spans:
            uid = f"{cid}#seg{i}-{j}"
            frame_rows.append(
                {"custom_id": uid, "prompt": segment_prompt(spec, states, entries, i, j)}
            )
            orc = segment_oracle(sol, states, entries, i, j)
            orc.pop("i"); orc.pop("j")
            oracle_rows.append({"custom_id": uid, "instance": cid, **orc})
    return frame_rows, oracle_rows


def write(strategy: str, frame_rows, oracle_rows):
    fp = HERE / f"frame_PLe_seg_{strategy}.csv"
    with fp.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["custom_id", "prompt"])
        w.writeheader()
        w.writerows(frame_rows)
    op = HERE / f"oracle_PLe_seg_{strategy}.csv"
    with op.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=ORACLE_COLS)
        w.writeheader()
        w.writerows(oracle_rows)
    return fp, op


def summarize(strategy: str, oracle_rows):
    lengths = [r["length"] for r in oracle_rows]
    dphis = [r["d_phi"] for r in oracle_rows]
    n = len(oracle_rows)
    def dist(xs):
        out = {}
        for x in xs:
            out[x] = out.get(x, 0) + 1
        return {k: out[k] for k in sorted(out)}
    print(f"\n=== strategy '{strategy}': {n} segments ===")
    print(f"  segment length   dist={dist(lengths)}  (method 2 was all length 1)")
    print(f"  net progress dPhi dist={dist(dphis)}  (varies -> rubric + value both have signal)")
    print(f"  segments with a backtrack/lateral (dPhi<length): "
          f"{sum(1 for r in oracle_rows if r['d_phi'] < r['length'])}/{n}")
    print(f"  segments containing >=1 rejected attempt: "
          f"{sum(1 for r in oracle_rows if r['n_illegal'] > 0)}/{n}")


def main(argv: list[str]) -> None:
    radius = 1
    if "--radius" in argv:
        k = argv.index("--radius")
        radius = int(argv[k + 1])
        del argv[k : k + 2]
    show = "--summary" in argv
    argv = [a for a in argv if a != "--summary"]
    strategies = [a for a in argv if not a.startswith("--")] or ["multilen"]
    if strategies == ["all"]:
        strategies = ["sliding", "multilen", "event", "subgoal"]

    for strategy in strategies:
        frame_rows, oracle_rows = build(strategy, radius=radius)
        fp, op = write(strategy, frame_rows, oracle_rows)
        print(f"{fp.name}: {len(frame_rows)} segments   ->   {op.name}")
        if show:
            summarize(strategy, oracle_rows)

    # Show one representative segment (a stretch that contains a correction).
    frame_rows, oracle_rows = build(strategies[0], radius=radius)
    ex = next((r for r in frame_rows if "ILLEGAL" in r["prompt"]), frame_rows[0])
    exo = next(r for r in oracle_rows if r["custom_id"] == ex["custom_id"])
    print(f"\n--- sample segment ({strategies[0]}) ---")
    print(ex["custom_id"], "|||", ex["prompt"])
    print("oracle:", {k: exo[k] for k in ("length", "d_phi", "min_phi_dip", "n_illegal",
                                          "n_backward", "n_lateral", "reaches_goal")})


if __name__ == "__main__":
    main(sys.argv[1:])
