"""Parametrized river-crossing testbed for demand-annotation methods.

``puzzle`` defines the parametrized problem family; ``solver`` provides the exact
value oracle (cost-to-go, transition value) that replaces a learned value model;
``play`` replays/parses agent move-sequences. The Inspect task lives in ``task``
(imported separately, since it needs the optional ``inspect_ai`` dependency).
"""

from .annotate_methods import (
    DEFAULT_DIMENSIONS,
    MODEL_PRESETS,
    estimate_cost,
    method_1a_frame,
    method_1b_frame,
    method_2_frame,
    reference_trajectories,
    run_annotation,
    trajectories_from_log,
)
from .play import (
    ReplayResult,
    apply_move,
    moves_from_trace,
    parse_moves,
    render_solution,
    replay,
)
from .puzzle import (
    CONFLICT_TOPOLOGIES,
    PuzzleSpec,
    conflict_graph_puzzle,
    conflict_topology_spec,
    describe_rules,
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
    generate_mixed_family,
    goal_state,
    initial_state,
    neighbors,
    solve,
)

__all__ = [
    "CONFLICT_TOPOLOGIES",
    "DEFAULT_DIMENSIONS",
    "MODEL_PRESETS",
    "PuzzleSpec",
    "ReplayResult",
    "Solution",
    "State",
    "apply_move",
    "conflict_graph_puzzle",
    "conflict_topology_spec",
    "describe_rules",
    "estimate_cost",
    "generate_family",
    "generate_instances",
    "generate_mixed_family",
    "goal_state",
    "initial_state",
    "linear_conflict_spec",
    "method_1a_frame",
    "method_1b_frame",
    "method_2_frame",
    "missionaries_cannibals",
    "moves_from_trace",
    "neighbors",
    "parse_moves",
    "reference_trajectories",
    "render_prompt",
    "render_solution",
    "replay",
    "run_annotation",
    "solve",
    "trajectories_from_log",
    "wolf_goat_cabbage",
]
