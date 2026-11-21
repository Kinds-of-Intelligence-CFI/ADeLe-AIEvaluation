"""Replay and parse agent move-sequences for river-crossing puzzles.

An agent solves a puzzle by emitting a sequence of crossings ("loads" -- the set
of items in the boat each trip). These pure helpers turn model text into loads,
replay them through the puzzle rules to recover the state trajectory and whether
the goal was reached, and render a known load-sequence back to text. No Inspect
dependency, so the scoring logic is testable on its own.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from .puzzle import PuzzleSpec
from .solver import State, goal_state, initial_state

_MOVE_LINE = re.compile(r"^\s*(?:\d+[.)]|[-*])\s+")


@dataclass
class ReplayResult:
    """Outcome of replaying a load sequence from the initial state."""

    trajectory: list[State]  # states visited, starting at the initial state
    success: bool  # every move legal and the goal reached
    first_illegal: int | None  # index of the first illegal move, if any
    n_moves: int


def moves_from_trace(trace: list[State]) -> list[frozenset[str]]:
    """The loads (items that switch banks) implied by a state trace."""
    return [a ^ b for (a, _), (b, _) in zip(trace, trace[1:])]


def apply_move(spec: PuzzleSpec, state: State, load: frozenset[str]) -> State | None:
    """The state after carrying ``load`` across, or None if the move is illegal."""
    left, side = state
    here = left if side == "L" else frozenset(spec.items) - left
    if not load <= here:
        return None
    if spec.ferryman is not None:
        if spec.ferryman not in load:
            return None
        if len(load - {spec.ferryman}) > spec.boat_capacity:
            return None
    elif not 1 <= len(load) <= spec.boat_capacity:
        return None
    new_left = left - load if side == "L" else left | load
    new_side = "R" if side == "L" else "L"
    if not spec.legal_configuration(new_left):
        return None
    return (new_left, new_side)


def replay(spec: PuzzleSpec, loads: list[frozenset[str]]) -> ReplayResult:
    """Replay ``loads`` from the initial state, stopping at the first illegal move."""
    state = initial_state(spec)
    trajectory = [state]
    for i, load in enumerate(loads):
        nxt = apply_move(spec, state, load)
        if nxt is None:
            return ReplayResult(trajectory, False, first_illegal=i, n_moves=len(loads))
        state = nxt
        trajectory.append(state)
    return ReplayResult(
        trajectory,
        success=state == goal_state(spec),
        first_illegal=None,
        n_moves=len(loads),
    )


def parse_moves(spec: PuzzleSpec, text: str) -> list[frozenset[str]]:
    """Parse loads from a numbered/bulleted move list in model output.

    Each list line contributes one load: the item names mentioned on it (the
    ferryman is always added for ferryman puzzles, since they must row).
    """
    loads: list[frozenset[str]] = []
    for line in text.splitlines():
        if not _MOVE_LINE.match(line):
            continue
        names = {
            item
            for item in spec.items
            if re.search(rf"\b{re.escape(item)}\b", line, re.IGNORECASE)
        }
        if spec.ferryman is not None:
            loads.append(frozenset(names | {spec.ferryman}))
        elif names:
            loads.append(frozenset(names))
    return loads


def render_solution(spec: PuzzleSpec, loads: list[frozenset[str]]) -> str:
    """Render a load sequence as a numbered move list (round-trips ``parse_moves``)."""
    lines = []
    for i, load in enumerate(loads, start=1):
        if spec.ferryman is not None:
            passengers = [spec.ferryman, *sorted(load - {spec.ferryman})]
        else:
            passengers = sorted(load)
        lines.append(f"{i}. " + ", ".join(passengers))
    return "\n".join(lines)
