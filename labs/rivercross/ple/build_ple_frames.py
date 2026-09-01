"""Build PLe (action control & execution) judge frames from captured trajectories.

Each of the 6 interactive sessions holds states + the agent's per-step reasoning +
illegal attempts. We render the play-through and emit three method frames so PLe can
be compared across methods:
  frame_PLe_1b.csv - demand-to-go at each non-terminal state (with the history+reasoning that led there)
                     (1a/whole-task is just the #s0 entries, so it is not built separately)
  frame_PLe_2.csv  - one DECISION EPISODE per committed action: what the agent tried, detected
                     as wrong, and corrected at that point, then the move it committed.
Each row: custom_id, prompt  (prompt is single-line; steps separated by ' | ').
"""
import csv
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent      # ple/
PILOT = HERE.parent
sys.path.insert(0, str(PILOT))
from rivercross import PuzzleSpec, describe_rules, goal_state  # noqa: E402

SPECS = json.load(open(PILOT / "specs.json"))
SESS = PILOT / "interactive"
CIDS = ["chain-3-boat-1", "chain-5-boat-2", "complete-4-boat-3",
        "cycle-4-boat-2", "star-4-boat-2", "missionaries-cannibals-3"]


def banks(spec, st):
    left = sorted(st["left"])
    right = sorted(set(spec.items) - set(st["left"]))
    side = "left" if st["boat"] == "L" else "right"
    return (f"Left: {', '.join(left) or 'nothing'}; Right: {', '.join(right) or 'nothing'}; "
            f"boat on {side}")


def load_str(spec, load):
    load = list(load)
    if spec.ferryman and spec.ferryman in load:
        others = [x for x in load if x != spec.ferryman]
        return spec.ferryman + (" with " + ", ".join(others) if others else " alone")
    return ", ".join(load) or "(nobody)"


def replay(spec, data):
    traj = data["trajectory"]
    entries, cur, ti = [], traj[0], 1
    for att in data["attempts"]:
        dest = "right" if cur["boat"] == "L" else "left"
        if att["legal"]:
            after = traj[ti]; ti += 1
            entries.append(dict(before=cur, load=att["load"], legal=True,
                                reason=att.get("reason", ""), after=after, dest=dest))
            cur = after
        else:
            entries.append(dict(before=cur, load=att["load"], legal=False,
                                reason=att.get("reason", ""), after=cur, dest=dest))
    return entries


def step_text(spec, e, n):
    r = e["reason"] or "(no reason given)"
    if e["legal"]:
        return f'move {n}: took {load_str(spec, e["load"])} to {e["dest"]} (agent: "{r}") -> {banks(spec, e["after"])}'
    return f'rejected: tried {load_str(spec, e["load"])} to {e["dest"]} (agent: "{r}") -> ILLEGAL, unchanged'


def history_str(spec, entries):
    """Single-line history; number legal moves cumulatively."""
    out, n = [], 0
    for e in entries:
        if e["legal"]:
            n += 1
        out.append(step_text(spec, e, n))
    return " | ".join(out)


def main():
    rows_1b, rows_2 = [], []
    for cid in CIDS:
        spec = PuzzleSpec.from_dict(SPECS[cid])
        data = json.load(open(SESS / f"{cid}.json"))
        rules = describe_rules(spec).strip()
        goal = goal_state(spec)
        start = data["trajectory"][0]
        entries = replay(spec, data)
        legal_pos = [i for i, e in enumerate(entries) if e["legal"]]
        states = [start] + [e["after"] for e in entries if e["legal"]]

        # --- 1b: demand-to-go at each non-terminal state (s0 doubles as whole-task) ---
        for k, st in enumerate(states):
            if (frozenset(st["left"]), st["boat"]) == goal:
                continue  # terminal: nothing left to do
            if k == 0:
                hist = "the task has just begun, no actions yet"
            else:
                hist = history_str(spec, entries[:legal_pos[k - 1] + 1])
            rows_1b.append({"custom_id": f"{cid}#s{k}",
                            "prompt": f"{rules} Goal: get everything to the right bank. "
                                      f"History so far: {hist}. Current situation: {banks(spec, st)}."})

        # --- 2: one DECISION EPISODE per committed action (corrections foregrounded) ---
        n = 0
        pending = []  # illegal attempts at the current state, before a legal move commits
        for e in entries:
            if not e["legal"]:
                pending.append(e)
                continue
            n += 1
            prior_legal = [x for x in entries[:legal_pos[n - 1]] if x["legal"]]
            prior = history_str(spec, prior_legal) if prior_legal else "none yet"
            if pending:
                tried = "; ".join(
                    f'tried {load_str(spec, x["load"])} to {x["dest"]} (agent: "{x["reason"] or "(no reason)"}") -> ILLEGAL, recognised and changed'
                    for x in pending)
                episode = f"At this point the agent {tried}; then committed "
            else:
                episode = "At this point the agent committed (no failed attempt) "
            committed = f'{load_str(spec, e["load"])} to the {e["dest"]} bank (agent: "{e["reason"] or "(no reason)"}")'
            rows_2.append({"custom_id": f"{cid}#t{n}",
                           "prompt": f"{rules} Goal: get everything to the right bank. "
                                     f"Execution so far (committed moves): {prior}. Situation now: {banks(spec, e['before'])}. "
                                     f"{episode}{committed}."})
            pending = []

    for name, rows in [("1b", rows_1b), ("2", rows_2)]:
        p = HERE / f"frame_PLe_{name}.csv"
        with p.open("w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=["custom_id", "prompt"])
            w.writeheader()
            w.writerows(rows)
        print(f"frame_PLe_{name}.csv: {len(rows)} items")

    print("\n--- sample 1b item ---")
    print(rows_1b[8]["custom_id"], "|||", rows_1b[8]["prompt"])
    print("\n--- sample 2 item (decision episode with a correction) ---")
    ep = next((r for r in rows_2 if "ILLEGAL" in r["prompt"]), rows_2[0])
    print(ep["custom_id"], "|||", ep["prompt"])


if __name__ == "__main__":
    main()
