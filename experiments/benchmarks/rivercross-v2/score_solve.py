"""Score the solver attempts of an rc-solve run (PREREGISTRATION.md, amendment 2). Writes labels/<run>/solve_long.csv.

Each answer is parsed after its last line reading ANSWER with the rivercross library's parse_moves (a numbered
list of boat loads; the farmer is added where there is one) and replayed from the puzzle state with the
library's rules. An attempt succeeds when every crossing is legal and everything ends on the right bank; it is
optimal when it also uses exactly the solver's number of crossings. The model that wrote each answer comes
from labels/<run>/writers.csv (writers.py).

    python experiments/benchmarks/rivercross-v2/score_solve.py --run rc-solve
"""

import argparse
import json
import re
from pathlib import Path

import pandas as pd

from adele.testbeds.rivercross.play import apply_move, parse_moves
from adele.testbeds.rivercross.puzzle import PuzzleSpec
from adele.testbeds.rivercross.solver import goal_state, solve

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def score(spec: PuzzleSpec, state, text: str) -> dict:
    parts = re.split(r"(?m)^\s*\**ANSWER\**:?\s*$", text)
    if len(parts) < 2:
        return {"answer_found": False, "n_moves": 0, "legal": False, "success": False}
    loads = parse_moves(spec, parts[-1])
    goal, legal = goal_state(spec), True
    for load in loads:
        nxt = apply_move(spec, state, load)
        if nxt is None:
            legal = False
            break
        state = nxt
        if state == goal:
            break
    return {"answer_found": True, "n_moves": len(loads), "legal": legal, "success": legal and state == goal}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    run_id = ap.parse_args().run
    labels = HERE / "labels" / run_id
    run = json.loads((labels / "run.json").read_text())
    specs = json.loads((HERE / "frames/search_specs.json").read_text())
    writers = pd.read_csv(labels / "writers.csv").set_index(["judge", "file_id"])["writer_model"]
    answers = ROOT / run["judge_io"] / "responses"
    rows = []
    for fid in pd.read_csv(labels / "prompts_index.csv")["file_id"]:
        d = specs[fid]
        spec = PuzzleSpec.from_dict(d["spec"])
        state = (frozenset(d["left"]), d["side"])
        ctg = solve(spec).dist[state]
        for attempt in run["design"]["judges"]:
            path = answers / attempt / f"{fid}@SOLVE.txt"
            if not path.exists():
                continue
            r = score(spec, state, path.read_text(encoding="utf-8"))
            rows.append({"custom_id": fid, "attempt": attempt, "writer_model": writers.get((attempt, fid)), **r,
                         "optimal": r["success"] and r["n_moves"] == ctg})
    out = pd.DataFrame(rows)
    out.to_csv(labels / "solve_long.csv", index=False)
    print(out.groupby("writer_model")[["answer_found", "legal", "success", "optimal"]].mean().round(3).to_string(),
          f"\n{len(out)} attempts on {out['custom_id'].nunique()} states")


if __name__ == "__main__":
    main()
