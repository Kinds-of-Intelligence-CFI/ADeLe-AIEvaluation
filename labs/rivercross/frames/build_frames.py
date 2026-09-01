"""Build standardized rivercross annotation frames for method 1b.

The state-visible frame preserves the existing PLp frame exactly. The
history-only frame is a paired MMs pilot view: each row uses the same underlying
state as a state-visible row, but exposes only the initial state, a legal move
history, and the goal.
"""

from __future__ import annotations

import csv
import re
from collections import deque
from pathlib import Path
from sys import path as sys_path


sys_path.insert(0, str(Path(__file__).resolve().parents[1]))

from rivercross.annotate_methods import _subproblem_text
from rivercross.play import moves_from_trace
from rivercross.puzzle import (
    PuzzleSpec,
    conflict_topology_spec,
    describe_rules,
    missionaries_cannibals,
)
from rivercross.solver import State, initial_state, neighbors, solve


HERE = Path(__file__).resolve().parent
RIVERCROSS = HERE.parent
LEGACY_1B = RIVERCROSS / "method1b"
OUT_STATE_VISIBLE = HERE / "1b_state_visible.csv"
OUT_HISTORY_ONLY = HERE / "1b_history_only.csv"
OUT_COST_TO_GO = HERE / "ground_truth" / "1b_state_visible_cost_to_go.csv"
OUT_MEMORY_PAIRS = HERE / "ground_truth" / "1b_memory_pairs.csv"

FAMILY_RE = re.compile(r"^(chain|star|cycle|complete)-(\d+)-boat-(\d+)$")
MISSIONARIES_RE = re.compile(r"^missionaries-cannibals-(\d+)$")


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_rows(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)


def spec_from_instance(instance: str) -> PuzzleSpec:
    family = FAMILY_RE.match(instance)
    if family:
        topology, n_cargo, boat_capacity = family.groups()
        return conflict_topology_spec(
            int(n_cargo),
            topology=topology,
            boat_capacity=int(boat_capacity),
            name=instance,
        )

    missionaries = MISSIONARIES_RE.match(instance)
    if missionaries:
        n = int(missionaries.group(1))
        # The historical calibration set uses the standard n-1 capacity.
        return missionaries_cannibals(n=n, boat_capacity=n - 1)

    raise ValueError(f"cannot infer PuzzleSpec for {instance!r}")


def infer_state_from_prompt(spec: PuzzleSpec, prompt: str) -> State:
    matches = [
        state
        for state in solve(spec).dist
        if _subproblem_text(spec, state) == prompt
    ]
    if len(matches) != 1:
        raise ValueError(
            f"expected exactly one solver state for {spec.name}; found {len(matches)}"
        )
    return matches[0]


def shortest_trace_to_state(spec: PuzzleSpec, target: State) -> list[State]:
    start = initial_state(spec)
    queue: deque[State] = deque([start])
    parent: dict[State, State | None] = {start: None}
    while queue:
        state = queue.popleft()
        if state == target:
            break
        for nxt in neighbors(spec, state):
            if nxt not in parent:
                parent[nxt] = state
                queue.append(nxt)
    if target not in parent:
        raise ValueError(f"target state is not reachable from initial state: {target}")

    trace = []
    state: State | None = target
    while state is not None:
        trace.append(state)
        state = parent[state]
    return list(reversed(trace))


def side_name(side: str) -> str:
    return "left" if side == "L" else "right"


def format_load(items: list[str]) -> str:
    if not items:
        return "nothing"
    if len(items) == 1:
        return items[0]
    return ", ".join(items[:-1]) + f", and {items[-1]}"


def render_move_history(spec: PuzzleSpec, trace: list[State]) -> str:
    if len(trace) == 1:
        return "No crossings have been made yet."

    lines = []
    for i, ((_, _src_side), (_, dst_side), load) in enumerate(
        zip(trace, trace[1:], moves_from_trace(trace)),
        start=1,
    ):
        direction = side_name(dst_side)
        if spec.ferryman is not None:
            cargo = sorted(load - {spec.ferryman})
            if cargo:
                passengers = f"{spec.ferryman} with {format_load(cargo)}"
            else:
                passengers = f"{spec.ferryman} alone"
        else:
            passengers = format_load(sorted(load))
        lines.append(f"{i}. {passengers} crossed to the {direction} bank.")
    return "\n".join(lines)


def format_history_only_item(spec: PuzzleSpec, trace: list[State]) -> str:
    initial_items = format_load(list(spec.items))
    return (
        f"You are partway through a river-crossing puzzle. {describe_rules(spec)} "
        "Goal: get everything to the right bank. "
        f"Initial state: {initial_items} start on the left bank with the boat; "
        "the right bank starts empty. "
        "Move history so far:\n"
        f"{render_move_history(spec, trace)}\n"
        "Based only on the initial state and move history, infer the present "
        "configuration and find a sequence of crossings that gets everything to the "
        "right bank from here."
    )


def serialize_items(items: frozenset[str]) -> str:
    return ";".join(sorted(items)) or "nothing"


def memory_features(spec: PuzzleSpec, trace: list[State]) -> dict[str, str]:
    loads = moves_from_trace(trace)
    object_moves: list[str] = []
    object_move_counts: dict[str, int] = {}
    all_move_counts: dict[str, int] = {}
    for load in loads:
        cargo = set(load) if spec.ferryman is None else set(load - {spec.ferryman})
        object_moves.extend(cargo)
        for item in cargo:
            object_move_counts[item] = object_move_counts.get(item, 0) + 1
        for item in load:
            all_move_counts[item] = all_move_counts.get(item, 0) + 1

    object_repeated_updates = sum(max(0, n - 1) for n in object_move_counts.values())
    object_reversal_items = sum(1 for n in object_move_counts.values() if n > 1)

    return {
        "history_length": str(len(loads)),
        "boat_side_updates": str(len(loads)),
        "object_location_updates": str(len(object_moves)),
        "num_unique_objects_moved": str(len(object_move_counts)),
        "num_reversals": str(object_repeated_updates),
        "interference_count": str(object_reversal_items),
        # Backward-compatible legacy feature names from the first pilot draft.
        "num_object_moves": str(len(object_moves)),
        "num_location_updates": str(sum(len(load) + 1 for load in loads)),
        "num_repeated_moves": str(sum(max(0, n - 1) for n in all_move_counts.values())),
    }


def main() -> None:
    frame_rows = read_rows(LEGACY_1B / "judge_frame_v2.csv")
    frame_ids = {row["custom_id"] for row in frame_rows}
    gt_rows = [
        row
        for row in read_rows(LEGACY_1B / "ground_truth.csv")
        if row["custom_id"] in frame_ids
    ]

    missing_gt = frame_ids - {row["custom_id"] for row in gt_rows}
    if missing_gt:
        raise SystemExit(f"missing ground truth for {len(missing_gt)} frame ids")

    gt_by_id = {row["custom_id"]: row for row in gt_rows}
    history_rows: list[dict[str, str]] = []
    pair_rows: list[dict[str, str]] = []
    for row in frame_rows:
        state_visible_id = row["custom_id"]
        instance = state_visible_id.split("#", 1)[0]
        spec = spec_from_instance(instance)
        state = infer_state_from_prompt(spec, row["prompt"])
        trace = shortest_trace_to_state(spec, state)
        history_id = f"{state_visible_id}__history_only"
        left, boat_side = state
        right = frozenset(spec.items) - left

        history_rows.append(
            {
                "custom_id": history_id,
                "prompt": format_history_only_item(spec, trace),
            }
        )
        pair_rows.append(
            {
                "pair_id": state_visible_id,
                "underlying_state_id": state_visible_id,
                "custom_id_state_visible": state_visible_id,
                "custom_id_history_only": history_id,
                "puzzle_id": instance,
                "step_idx": state_visible_id.rsplit("#s", 1)[-1],
                "true_left": serialize_items(left),
                "true_right": serialize_items(right),
                "true_boat": side_name(boat_side),
                "cost_to_go": gt_by_id[state_visible_id]["dist_to_goal"],
                **memory_features(spec, trace),
            }
        )

    write_rows(OUT_STATE_VISIBLE, frame_rows, ["custom_id", "prompt"])
    write_rows(OUT_COST_TO_GO, gt_rows, ["custom_id", "instance", "dist_to_goal"])
    write_rows(OUT_HISTORY_ONLY, history_rows, ["custom_id", "prompt"])
    write_rows(
        OUT_MEMORY_PAIRS,
        pair_rows,
        [
            "pair_id",
            "underlying_state_id",
            "custom_id_state_visible",
            "custom_id_history_only",
            "puzzle_id",
            "step_idx",
            "true_left",
            "true_right",
            "true_boat",
            "cost_to_go",
            "history_length",
            "boat_side_updates",
            "object_location_updates",
            "num_unique_objects_moved",
            "num_reversals",
            "interference_count",
            "num_object_moves",
            "num_location_updates",
            "num_repeated_moves",
        ],
    )
    print(f"wrote {OUT_STATE_VISIBLE.relative_to(RIVERCROSS)} ({len(frame_rows)} rows)")
    print(f"wrote {OUT_COST_TO_GO.relative_to(RIVERCROSS)} ({len(gt_rows)} rows)")
    print(f"wrote {OUT_HISTORY_ONLY.relative_to(RIVERCROSS)} ({len(history_rows)} rows)")
    print(f"wrote {OUT_MEMORY_PAIRS.relative_to(RIVERCROSS)} ({len(pair_rows)} rows)")


if __name__ == "__main__":
    main()
