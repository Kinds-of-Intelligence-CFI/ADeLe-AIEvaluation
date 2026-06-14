"""Parametrized river-crossing testbed for demand-annotation methods.

``puzzle`` defines the parametrized problem family; ``solver`` provides the exact
value oracle (cost-to-go, transition value) that replaces a learned value model;
``play`` replays/parses agent move-sequences. The Inspect task lives in ``task``
(imported separately, since it needs the optional ``inspect_ai`` dependency).
"""

from .play import (
    ReplayResult,
    apply_move,
    moves_from_trace,
    parse_moves,
    render_solution,
    replay,
)
from .puzzle import (
    PuzzleSpec,
    conflict_graph_puzzle,
    linear_conflict_spec,
    missionaries_cannibals,
    render_prompt,
    wolf_goat_cabbage,
)
from .solver import (
    Solution,
    State,
    generate_family,
    generate_instances,
    goal_state,
    initial_state,
    neighbors,
    solve,
)

__all__ = [
    "PuzzleSpec",
    "ReplayResult",
    "Solution",
    "State",
    "apply_move",
    "conflict_graph_puzzle",
    "generate_family",
    "generate_instances",
    "goal_state",
    "initial_state",
    "linear_conflict_spec",
    "missionaries_cannibals",
    "moves_from_trace",
    "neighbors",
    "parse_moves",
    "render_prompt",
    "render_solution",
    "replay",
    "solve",
    "wolf_goat_cabbage",
]
