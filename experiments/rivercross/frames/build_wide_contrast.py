"""Build the v6 widened MMs contrast set (pre-registered in
memory/PREREGISTRATION_v5_v6.md).

Closes the three v3 design gaps:
- history_length in {3, 7, 10} with high-complexity length-10 cells probing
  the untested level 4-5 anchors;
- cost_to_go allowed to vary across cells (v3 pinned it to {1,2}), so the
  difficulty-independence gate is testable;
- decoupling cells at matched update counts (zero reversals vs many
  reversals) to break the v3 updates/reversals collinearity.

Length-3 candidates are enumerated exhaustively; lengths 7 and 10 are
sampled with seeded random walks (exhaustive enumeration is infeasible).
Seed fixed below and recorded in the pairs file header row semantics.
"""

from __future__ import annotations

import argparse
import random
from collections import defaultdict
from pathlib import Path
from sys import path as sys_path

sys_path.insert(0, str(Path(__file__).resolve().parent))

from build_frames import (
    format_history_only_item,
    memory_features,
    serialize_items,
    side_name,
    write_rows,
)
from build_memory_contrast import Candidate, candidate_from_trace, specs
import build_memory_contrast
from adele.testbeds.rivercross.annotate_methods import _subproblem_text
from adele.testbeds.rivercross.solver import goal_state, initial_state, neighbors, solve


HERE = Path(__file__).resolve().parent
OUT_STATE_VISIBLE = HERE / "1b_wide_contrast_state_visible.csv"
OUT_HISTORY_ONLY = HERE / "1b_wide_contrast_history_only.csv"
OUT_PAIRS = HERE / "ground_truth" / "1b_wide_contrast_pairs.csv"
HISTORY_LENGTHS = (3, 7, 10)
SEED = 20260710
WALKS_PER_SPEC = 400
REPEATS = 2


def sampled_candidates() -> list[Candidate]:
    """Length-3 exhaustively; lengths 7/10 by seeded random walks."""
    build_memory_contrast.HISTORY_LENGTHS = HISTORY_LENGTHS
    rng = random.Random(SEED)
    out: list[Candidate] = []
    seen: set[tuple] = set()

    def add(spec, trace, sol):
        candidate = candidate_from_trace(spec, trace, sol)
        if candidate is None or candidate.signature in seen:
            return
        seen.add(candidate.signature)
        out.append(candidate)

    for spec in specs():
        sol = solve(spec)
        goal = goal_state(spec)
        # exhaustive length-3
        stack = [[initial_state(spec)]]
        while stack:
            trace = stack.pop()
            if len(trace) - 1 == 3:
                add(spec, trace, sol)
                continue
            for nxt in neighbors(spec, trace[-1]):
                stack.append([*trace, nxt])
        # sampled lengths 7 and 10
        for target_len in (7, 10):
            for _ in range(WALKS_PER_SPEC):
                trace = [initial_state(spec)]
                ok = True
                for _step in range(target_len):
                    options = [s for s in neighbors(spec, trace[-1]) if s != goal]
                    if not options:
                        ok = False
                        break
                    trace.append(rng.choice(options))
                if ok:
                    add(spec, trace, sol)
    return out


def pick(pool: list[Candidate], used: set[tuple], k: int = REPEATS) -> list[Candidate]:
    """Pick k candidates, preferring distinct specs and distinct cost_to_go.

    `used` holds (spec.name, state) keys already selected in ANY cell, so the
    same underlying state never appears twice in the annotation frame.
    """
    picked: list[Candidate] = []
    for require_new_spec, require_new_cost in ((True, True), (True, False), (False, False)):
        for c in pool:
            if len(picked) == k:
                return picked
            key = (c.spec.name, c.state)
            if key in used:
                continue
            if any(p.signature == c.signature or p.state == c.state for p in picked):
                continue
            if require_new_spec and any(p.spec.name == c.spec.name for p in picked):
                continue
            if require_new_cost and any(p.cost_to_go == c.cost_to_go for p in picked):
                continue
            picked.append(c)
            used.add(key)
    if len(picked) < k:
        raise SystemExit(f"could not fill a cell: only {len(picked)} candidates")
    return picked


def select_cells(candidates: list[Candidate]) -> list[tuple[str, int, Candidate]]:
    selected: list[tuple[str, int, Candidate]] = []
    used: set[tuple] = set()
    by_len: dict[int, list[Candidate]] = defaultdict(list)
    for c in candidates:
        by_len[c.history_length].append(c)

    # decoupling cells first (their matched-updates constraint is the tightest)
    pool7 = by_len[7]
    nr_pool = sorted(
        (c for c in pool7 if c.num_reversals == 0),
        key=lambda c: (-c.object_location_updates, c.spec.name),
    )
    nrev = pick(nr_pool, used)
    target_updates = sum(c.object_location_updates for c in nrev) / len(nrev)
    rev_pool = sorted(
        (c for c in pool7 if c.num_reversals >= 3),
        key=lambda c: (abs(c.object_location_updates - target_updates), -c.num_reversals, c.spec.name),
    )
    rev = pick(rev_pool, used)
    selected.extend(("nrev", 7, c) for c in nrev)
    selected.extend(("rev", 7, c) for c in rev)

    for length in HISTORY_LENGTHS:
        pool = by_len[length]
        if not pool:
            raise SystemExit(f"no candidates at history_length={length}")
        low_pool = sorted(pool, key=lambda c: (c.object_complexity, c.spec.name))
        high_pool = sorted(pool, key=lambda c: (-c.object_complexity, c.spec.name))
        low = pick(low_pool, used)
        high = pick(high_pool, used)
        low_max = max(c.object_complexity for c in low)
        high_min = min(c.object_complexity for c in high)
        midpoint = (low_max + high_min) / 2
        med_pool = sorted(
            (c for c in pool if low_max < c.object_complexity < high_min),
            key=lambda c: (c.num_reversals > 0, abs(c.object_complexity - midpoint), c.spec.name),
        )
        medium = pick(med_pool, used)
        for cell, group in (("low", low), ("medium", medium), ("high", high)):
            selected.extend((cell, length, c) for c in group)
    return selected


def build_rows(selected):
    state_rows, history_rows, pair_rows = [], [], []
    counters: dict[tuple[int, str], int] = defaultdict(int)
    for cell, length, candidate in selected:
        counters[(length, cell)] += 1
        rank = counters[(length, cell)]
        pair_id = f"memw-L{length}-{cell}-{rank:02d}"
        state_id = f"{pair_id}__state_visible"
        history_id = f"{pair_id}__history_only"
        left, boat_side = candidate.state
        right = frozenset(candidate.spec.items) - left
        features = memory_features(candidate.spec, candidate.trace)
        pair_rows.append({
            "pair_id": pair_id,
            "underlying_state_id": pair_id,
            "contrast_level": cell,
            "custom_id_state_visible": state_id,
            "custom_id_history_only": history_id,
            "puzzle_id": candidate.spec.name,
            "step_idx": str(length),
            "trace_idx": str(rank),
            "true_left": serialize_items(left),
            "true_right": serialize_items(right),
            "true_boat": side_name(boat_side),
            "cost_to_go": str(candidate.cost_to_go),
            "object_complexity": str(candidate.object_complexity),
            **features,
        })
        state_rows.append({"custom_id": state_id,
                           "prompt": _subproblem_text(candidate.spec, candidate.state)})
        history_rows.append({"custom_id": history_id,
                             "prompt": format_history_only_item(candidate.spec, candidate.trace)})
    return state_rows, history_rows, pair_rows


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out-state-visible", type=Path, default=OUT_STATE_VISIBLE)
    ap.add_argument("--out-history-only", type=Path, default=OUT_HISTORY_ONLY)
    ap.add_argument("--out-pairs", type=Path, default=OUT_PAIRS)
    args = ap.parse_args()

    candidates = sampled_candidates()
    print(f"candidate pool: {len(candidates)} (seed={SEED}, walks/spec={WALKS_PER_SPEC})")
    selected = select_cells(candidates)
    state_rows, history_rows, pair_rows = build_rows(selected)
    pair_fields = list(pair_rows[0].keys())
    write_rows(args.out_state_visible, state_rows, ["custom_id", "prompt"])
    write_rows(args.out_history_only, history_rows, ["custom_id", "prompt"])
    write_rows(args.out_pairs, pair_rows, pair_fields)
    print(f"wrote {args.out_state_visible.name} ({len(state_rows)} rows)")
    print(f"wrote {args.out_pairs.name} ({len(pair_rows)} rows)")
    for row in pair_rows:
        print(f"  {row['pair_id']:18s} cost={row['cost_to_go']:>2s} "
              f"updates={row['object_location_updates']:>3} reversals={row['num_reversals']:>3} "
              f"interference={row['interference_count']:>3} puzzle={row['puzzle_id']}")


if __name__ == "__main__":
    main()
