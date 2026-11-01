"""Interactive river-crossing referee for agent solving.

The agent proposes one crossing at a time; the referee enforces the rules:
illegal moves are REJECTED with feedback (not recorded), legal moves advance the
state and are appended to the trajectory (suboptimal moves allowed). It never
reveals the optimal length / distance-to-go, so it leaks no difficulty ground
truth. Per-session state lives in rivercross_pilot/interactive/<cid>.json.

Usage:
  referee.py init <cid>
  referee.py move <cid> "passenger1, passenger2"
"""

import json
import re
import sys
from pathlib import Path

from adele.testbeds.rivercross import PuzzleSpec, apply_move, goal_state, initial_state

ROOT = Path(__file__).resolve().parent
SPECS = json.load(open(ROOT / "specs.json"))
SESS = ROOT / "interactive"
MOVE_BUDGET = 40
ILLEGAL_BUDGET = 8


def _ser(state):
    return {"left": sorted(state[0]), "boat": state[1]}


def _deser(d):
    return (frozenset(d["left"]), d["boat"])


def _describe(spec, state):
    left, side = state
    right = sorted(set(spec.items) - left)
    return (f"Left bank: {', '.join(sorted(left)) or 'nothing'}. "
            f"Right bank: {', '.join(right) or 'nothing'}. "
            f"Boat is on the {'left' if side == 'L' else 'right'}.")


def main():
    cmd, cid = sys.argv[1], sys.argv[2]
    spec = PuzzleSpec.from_dict(SPECS[cid])
    path = SESS / f"{cid}.json"

    if cmd == "init":
        SESS.mkdir(exist_ok=True)
        state = initial_state(spec)
        json.dump({"trajectory": [_ser(state)], "attempts": [],
                   "consec_illegal": 0, "status": "ongoing"}, open(path, "w"), indent=2)
        print(_describe(spec, state))
        print("Goal: move everything to the right bank. Make your first crossing.")
        return

    data = json.load(open(path))
    if data["status"] != "ongoing":
        print(f"Session already {data['status']}. STOP.")
        return

    state = _deser(data["trajectory"][-1])
    passengers = set(re.findall(r"[A-Za-z0-9]+", sys.argv[3]))
    names = frozenset(it for it in spec.items if it in passengers)
    load = names | ({spec.ferryman} if spec.ferryman else frozenset())
    nxt = apply_move(spec, state, load)
    reason = " ".join(sys.argv[4:]).strip() if len(sys.argv) > 4 else ""
    data["attempts"].append({"load": sorted(load), "legal": nxt is not None, "reason": reason})

    if nxt is None:
        data["consec_illegal"] += 1
        if data["consec_illegal"] >= ILLEGAL_BUDGET:
            data["status"] = "aborted"
        json.dump(data, open(path, "w"), indent=2)
        print(f"ILLEGAL move (rejected, not recorded): carrying {sorted(load)} is not "
              "allowed here — it either exceeds the boat, isn't on the boat's bank, or "
              "leaves a forbidden combination unattended. State unchanged.")
        print("Current " + _describe(spec, state))
        print("STOP." if data["status"] == "aborted" else "Try a different crossing.")
        return

    data["consec_illegal"] = 0
    step = _ser(nxt)
    step["reason"] = reason
    data["trajectory"].append(step)
    if nxt == goal_state(spec):
        data["status"] = "solved"
    elif len(data["trajectory"]) - 1 >= MOVE_BUDGET:
        data["status"] = "budget"
    json.dump(data, open(path, "w"), indent=2)
    print("LEGAL. " + _describe(spec, nxt))
    if data["status"] == "solved":
        print("SOLVED! STOP.")
    elif data["status"] == "budget":
        print("Move budget reached. STOP.")
    else:
        print("Continue.")


if __name__ == "__main__":
    main()
