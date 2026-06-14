"""Parametrized river-crossing testbed for demand-annotation methods.

``puzzle`` defines the parametrized problem family; ``solver`` provides the exact
value oracle (cost-to-go, transition value) that replaces a learned value model.
"""

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
    "Solution",
    "State",
    "conflict_graph_puzzle",
    "generate_family",
    "generate_instances",
    "goal_state",
    "initial_state",
    "linear_conflict_spec",
    "missionaries_cannibals",
    "neighbors",
    "render_prompt",
    "solve",
    "wolf_goat_cabbage",
]
