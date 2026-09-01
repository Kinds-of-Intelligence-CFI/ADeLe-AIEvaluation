"""Build a fixed-history-length MMs contrast set for rivercross.

This v3 pilot set tests whether MMs labels track object-memory complexity beyond
history length. It uses only legal traces and constructs paired state-visible /
history-only views for low/medium/high object-complexity histories at fixed
history lengths.
"""

from __future__ import annotations

import csv
import argparse
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from sys import path as sys_path

sys_path.insert(0, str(Path(__file__).resolve().parents[1]))
sys_path.insert(0, str(Path(__file__).resolve().parent))

from build_frames import (
    format_history_only_item,
    memory_features,
    serialize_items,
    side_name,
    write_rows,
)
from rivercross.annotate_methods import _subproblem_text
from rivercross.puzzle import PuzzleSpec, conflict_topology_spec, missionaries_cannibals
from rivercross.solver import State, goal_state, initial_state, neighbors, solve


HERE = Path(__file__).resolve().parent
RIVERCROSS = HERE.parent
OUT_STATE_VISIBLE = HERE / "1b_memory_contrast_state_visible.csv"
OUT_HISTORY_ONLY = HERE / "1b_memory_contrast_history_only.csv"
OUT_PAIRS = HERE / "ground_truth" / "1b_memory_contrast_pairs.csv"
HISTORY_LENGTHS = (3, 4, 5)
LEVELS = ("low", "medium", "high")
REPEATS = 2


@dataclass(frozen=True)
class Candidate:
    spec: PuzzleSpec
    trace: list[State]
    cost_to_go: int
    history_length: int
    object_complexity: int
    object_location_updates: int
    num_reversals: int
    interference_count: int
    num_unique_objects_moved: int

    @property
    def state(self) -> State:
        return self.trace[-1]

    @property
    def signature(self) -> tuple:
        return (self.spec.name, tuple(self.trace))


def specs() -> list[PuzzleSpec]:
    out: list[PuzzleSpec] = []
    for topology in ("chain", "star", "cycle", "complete"):
        for n_cargo in range(3, 6):
            for capacity in range(1, 5):
                spec = conflict_topology_spec(
                    n_cargo,
                    topology=topology,
                    boat_capacity=capacity,
                    name=f"{topology}-{n_cargo}-boat-{capacity}",
                )
                if solve(spec).optimal_len is not None:
                    out.append(spec)
    for n in (3, 4):
        spec = missionaries_cannibals(n=n, boat_capacity=n - 1)
        if solve(spec).optimal_len is not None:
            out.append(spec)
    return out


def enumerate_traces(spec: PuzzleSpec, max_len: int) -> list[list[State]]:
    traces = [[initial_state(spec)]]
    completed: list[list[State]] = []
    for _ in range(max_len):
        next_traces: list[list[State]] = []
        for trace in traces:
            for nxt in neighbors(spec, trace[-1]):
                new_trace = [*trace, nxt]
                completed.append(new_trace)
                next_traces.append(new_trace)
        traces = next_traces
    return completed


def candidate_from_trace(spec: PuzzleSpec, trace: list[State], sol) -> Candidate | None:
    history_length = len(trace) - 1
    if history_length not in HISTORY_LENGTHS:
        return None
    state = trace[-1]
    if state == goal_state(spec) or state not in sol.dist:
        return None
    features = {k: int(v) for k, v in memory_features(spec, trace).items()}
    object_complexity = (
        features["object_location_updates"]
        + features["num_reversals"]
        + features["interference_count"]
    )
    return Candidate(
        spec=spec,
        trace=trace,
        cost_to_go=sol.dist[state],
        history_length=history_length,
        object_complexity=object_complexity,
        object_location_updates=features["object_location_updates"],
        num_reversals=features["num_reversals"],
        interference_count=features["interference_count"],
        num_unique_objects_moved=features["num_unique_objects_moved"],
    )


def all_candidates() -> list[Candidate]:
    out: list[Candidate] = []
    seen: set[tuple] = set()
    for spec in specs():
        sol = solve(spec)
        for trace in enumerate_traces(spec, max(HISTORY_LENGTHS)):
            candidate = candidate_from_trace(spec, trace, sol)
            if candidate is None or candidate.signature in seen:
                continue
            seen.add(candidate.signature)
            out.append(candidate)
    return out


def best_cost_bucket(candidates: list[Candidate], history_length: int) -> list[Candidate]:
    by_cost: dict[int, list[Candidate]] = defaultdict(list)
    for candidate in candidates:
        if candidate.history_length == history_length:
            by_cost[candidate.cost_to_go].append(candidate)
    if not by_cost:
        raise ValueError(f"no candidates for history_length={history_length}")

    def score(bucket: list[Candidate]) -> tuple[int, int, int]:
        complexities = [c.object_complexity for c in bucket]
        return (max(complexities) - min(complexities), len(set(complexities)), len(bucket))

    _cost, bucket = max(by_cost.items(), key=lambda item: score(item[1]))
    return bucket


def pick_diverse(candidates: list[Candidate], reverse: bool) -> list[Candidate]:
    ordered = sorted(
        candidates,
        key=lambda c: (
            c.object_complexity,
            c.object_location_updates,
            c.num_reversals,
            c.interference_count,
            c.spec.name,
        ),
        reverse=reverse,
    )
    picked: list[Candidate] = []
    used_specs: set[str] = set()
    used_states: set[tuple[str, State]] = set()
    for candidate in ordered:
        key = (candidate.spec.name, candidate.state)
        if candidate.spec.name in used_specs or key in used_states:
            continue
        picked.append(candidate)
        used_specs.add(candidate.spec.name)
        used_states.add(key)
        if len(picked) == REPEATS:
            return picked
    for candidate in ordered:
        key = (candidate.spec.name, candidate.state)
        if key in used_states:
            continue
        picked.append(candidate)
        used_states.add(key)
        if len(picked) == REPEATS:
            return picked
    if len(picked) < REPEATS:
        raise ValueError("not enough diverse candidates")
    return picked



def pick_from_ordered(ordered: list[Candidate]) -> list[Candidate]:
    picked: list[Candidate] = []
    used_specs: set[str] = set()
    used_states: set[tuple[str, State]] = set()
    for candidate in ordered:
        key = (candidate.spec.name, candidate.state)
        if candidate.spec.name in used_specs or key in used_states:
            continue
        picked.append(candidate)
        used_specs.add(candidate.spec.name)
        used_states.add(key)
        if len(picked) == REPEATS:
            return picked
    for candidate in ordered:
        key = (candidate.spec.name, candidate.state)
        if key in used_states:
            continue
        picked.append(candidate)
        used_states.add(key)
        if len(picked) == REPEATS:
            return picked
    if len(picked) < REPEATS:
        raise ValueError("not enough diverse candidates")
    return picked


def pick_medium(candidates: list[Candidate], low: list[Candidate], high: list[Candidate]) -> list[Candidate]:
    low_max = max(c.object_complexity for c in low)
    high_min = min(c.object_complexity for c in high)
    no_reversal = [
        c for c in candidates
        if low_max < c.object_complexity < high_min and c.num_reversals == 0
    ]
    if len(no_reversal) >= REPEATS:
        ordered = sorted(
            no_reversal,
            key=lambda c: (c.object_location_updates, c.num_unique_objects_moved, c.spec.name),
            reverse=True,
        )
        return pick_from_ordered(ordered)

    midpoint = (low_max + high_min) / 2
    middle = sorted(candidates, key=lambda c: abs(c.object_complexity - midpoint))
    return pick_from_ordered(middle)


def select_contrast_set(candidates: list[Candidate]) -> list[tuple[str, Candidate]]:
    selected: list[tuple[str, Candidate]] = []
    for history_length in HISTORY_LENGTHS:
        bucket = best_cost_bucket(candidates, history_length)
        low = pick_diverse(bucket, reverse=False)
        high = pick_diverse(bucket, reverse=True)
        medium = pick_medium(bucket, low, high)
        for level, group in (("low", low), ("medium", medium), ("high", high)):
            for candidate in group:
                selected.append((level, candidate))
    return selected


def build_rows(selected: list[tuple[str, Candidate]]) -> tuple[list[dict[str, str]], list[dict[str, str]], list[dict[str, str]]]:
    state_rows: list[dict[str, str]] = []
    history_rows: list[dict[str, str]] = []
    pair_rows: list[dict[str, str]] = []
    counters: dict[tuple[int, str], int] = defaultdict(int)
    for level, candidate in selected:
        counters[(candidate.history_length, level)] += 1
        rank = counters[(candidate.history_length, level)]
        pair_id = f"memc-L{candidate.history_length}-{level}-{rank:02d}"
        state_id = f"{pair_id}__state_visible"
        history_id = f"{pair_id}__history_only"
        left, boat_side = candidate.state
        right = frozenset(candidate.spec.items) - left
        features = memory_features(candidate.spec, candidate.trace)
        pair_rows.append(
            {
                "pair_id": pair_id,
                "underlying_state_id": pair_id,
                "contrast_level": level,
                "custom_id_state_visible": state_id,
                "custom_id_history_only": history_id,
                "puzzle_id": candidate.spec.name,
                "step_idx": str(candidate.history_length),
                "trace_idx": str(rank),
                "true_left": serialize_items(left),
                "true_right": serialize_items(right),
                "true_boat": side_name(boat_side),
                "cost_to_go": str(candidate.cost_to_go),
                "object_complexity": str(candidate.object_complexity),
                **features,
            }
        )
        state_rows.append({"custom_id": state_id, "prompt": _subproblem_text(candidate.spec, candidate.state)})
        history_rows.append({"custom_id": history_id, "prompt": format_history_only_item(candidate.spec, candidate.trace)})
    return state_rows, history_rows, pair_rows


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(
        description="Build paired state-visible/history-only MMs contrast frames."
    )
    ap.add_argument("--out-state-visible", type=Path, default=OUT_STATE_VISIBLE)
    ap.add_argument("--out-history-only", type=Path, default=OUT_HISTORY_ONLY)
    ap.add_argument("--out-pairs", type=Path, default=OUT_PAIRS)
    return ap.parse_args()


def main() -> None:
    args = parse_args()
    candidates = all_candidates()
    selected = select_contrast_set(candidates)
    state_rows, history_rows, pair_rows = build_rows(selected)
    pair_fields = [
        "pair_id",
        "underlying_state_id",
        "contrast_level",
        "custom_id_state_visible",
        "custom_id_history_only",
        "puzzle_id",
        "step_idx",
        "trace_idx",
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
        "object_complexity",
        "num_object_moves",
        "num_location_updates",
        "num_repeated_moves",
    ]
    write_rows(args.out_state_visible, state_rows, ["custom_id", "prompt"])
    write_rows(args.out_history_only, history_rows, ["custom_id", "prompt"])
    write_rows(args.out_pairs, pair_rows, pair_fields)
    print(f"wrote {args.out_state_visible.relative_to(RIVERCROSS)} ({len(state_rows)} rows)")
    print(f"wrote {args.out_history_only.relative_to(RIVERCROSS)} ({len(history_rows)} rows)")
    print(f"wrote {args.out_pairs.relative_to(RIVERCROSS)} ({len(pair_rows)} rows)")


if __name__ == "__main__":
    main()
