"""Exact BFS solver over the river-crossing state graph.

This is the value oracle that replaces a learned value model. A backward BFS
from the goal yields the exact optimal cost-to-go ``dist_to_goal(s)`` for every
state that can reach the goal. From it we derive solvability, optimal traces, a
potential ``Phi(s) = -dist_to_goal(s)``, and the exact transition value used by
the transition-annotation method (2).

State = ``(items on the left bank, boat side)`` with boat side ``"L"`` or ``"R"``.
Transitions are reversible (you can always row back), so the state graph is
undirected and a single BFS from the goal gives cost-to-go for all states.
"""

from __future__ import annotations

import itertools
import math
from collections import deque
from dataclasses import dataclass

import pandas as pd

from .puzzle import (
    CONFLICT_TOPOLOGIES,
    PuzzleSpec,
    conflict_topology_spec,
    render_prompt,
)

State = tuple[frozenset[str], str]


def initial_state(spec: PuzzleSpec) -> State:
    return (frozenset(spec.items), "L")


def goal_state(spec: PuzzleSpec) -> State:
    return (frozenset(), "R")


def neighbors(spec: PuzzleSpec, state: State) -> list[State]:
    """All legal states reachable from ``state`` in one crossing."""
    left, side = state
    here = left if side == "L" else frozenset(spec.items) - left

    loads: list[frozenset[str]] = []
    if spec.ferryman is not None:
        if spec.ferryman not in here:
            return []
        others = sorted(here - {spec.ferryman})
        for k in range(spec.boat_capacity + 1):
            for combo in itertools.combinations(others, k):
                loads.append(frozenset(combo) | {spec.ferryman})
    else:
        ordered = sorted(here)
        for k in range(1, spec.boat_capacity + 1):
            for combo in itertools.combinations(ordered, k):
                loads.append(frozenset(combo))

    result: list[State] = []
    for load in loads:
        if side == "L":
            new_left, new_side = left - load, "R"
        else:
            new_left, new_side = left | load, "L"
        if spec.legal_configuration(new_left):
            result.append((new_left, new_side))
    return result


@dataclass
class Solution:
    """The solved state graph: optimal cost-to-go for every reachable state."""

    spec: PuzzleSpec
    dist: dict[State, int]  # state -> optimal crossings remaining to the goal

    def solvable(self, state: State) -> bool:
        return state in self.dist

    @property
    def optimal_len(self) -> int | None:
        """Optimal number of crossings from the initial state, or None if unsolvable."""
        return self.dist.get(initial_state(self.spec))

    def potential(self, state: State) -> float:
        """Phi(s) = -dist_to_goal(s); -inf for states that cannot reach the goal."""
        return -self.dist[state] if state in self.dist else -math.inf

    def transition_value(self, src: State, dst: State) -> float:
        """Exact optimal progress made by a transition: Phi(dst) - Phi(src).

        +1 for an optimal step, 0 for a lateral move, -1 for a backward move,
        and -inf for a move into a region from which the goal is unreachable.
        """
        return self.potential(dst) - self.potential(src)

    def classify_move(self, src: State, dst: State) -> str:
        """Label a transition by its effect on optimal cost-to-go."""
        if dst not in self.dist:
            return "fatal"
        if src not in self.dist:
            return "recovering"
        delta = self.dist[src] - self.dist[dst]
        return {1: "optimal", 0: "lateral", -1: "backward"}.get(delta, "other")

    def optimal_trace(self) -> list[State] | None:
        """One shortest path from the initial state to the goal, or None."""
        state = initial_state(self.spec)
        if state not in self.dist:
            return None
        trace = [state]
        while self.dist[state] > 0:
            state = min(
                neighbors(self.spec, state),
                key=lambda nb: self.dist.get(nb, math.inf),
            )
            trace.append(state)
        return trace


def solve(spec: PuzzleSpec) -> Solution:
    """Backward BFS from the goal; fills cost-to-go for every state that reaches it."""
    goal = goal_state(spec)
    dist: dict[State, int] = {goal: 0}
    queue: deque[State] = deque([goal])
    while queue:
        state = queue.popleft()
        for nb in neighbors(spec, state):
            if nb not in dist:
                dist[nb] = dist[state] + 1
                queue.append(nb)
    return Solution(spec, dist)


def generate_family(
    n_cargo_values: range | tuple[int, ...],
    boat_capacities: tuple[int, ...] = (1,),
    topology: str = "chain",
    solvable_only: bool = True,
) -> list[PuzzleSpec]:
    """A parametrized family of conflict-graph puzzles of one ``topology``
    (the natural wolf-goat-cabbage generalization) swept over item count and boat
    capacity. With ``solvable_only`` (default) only instances whose goal is
    reachable are kept, so larger capacities can "unlock" otherwise-stuck shapes.
    """
    family: list[PuzzleSpec] = []
    for n_cargo in n_cargo_values:
        for capacity in boat_capacities:
            spec = conflict_topology_spec(n_cargo, topology, capacity)
            if solvable_only and solve(spec).optimal_len is None:
                continue
            family.append(spec)
    return family


def generate_mixed_family(
    n_cargo_values: range | tuple[int, ...],
    boat_capacities: tuple[int, ...] = (2, 3),
    topologies: tuple[str, ...] = CONFLICT_TOPOLOGIES,
    solvable_only: bool = True,
) -> list[PuzzleSpec]:
    """A family spanning several conflict-graph topologies at once."""
    family: list[PuzzleSpec] = []
    for topology in topologies:
        family.extend(
            generate_family(n_cargo_values, boat_capacities, topology, solvable_only)
        )
    return family


def generate_instances(specs: list[PuzzleSpec]) -> pd.DataFrame:
    """Build an annotation-ready frame (one row per spec) with solver difficulty.

    Columns match the annotation/Inspect pipeline (``custom_id``, ``prompt``)
    plus solver-measured difficulty (``optimal_len``, ``n_states``).
    """
    rows = []
    for spec in specs:
        sol = solve(spec)
        rows.append(
            {
                "custom_id": spec.name,
                "prompt": render_prompt(spec),
                "solvable": sol.optimal_len is not None,
                "optimal_len": sol.optimal_len,
                "n_states": len(sol.dist),
                "n_items": len(spec.items),
                "boat_capacity": spec.boat_capacity,
            }
        )
    return pd.DataFrame(rows)
