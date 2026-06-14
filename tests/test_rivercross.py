"""Tests for the river-crossing parametrization and exact solver."""

import math

from adele.rivercross import (
    PuzzleSpec,
    conflict_graph_puzzle,
    generate_family,
    generate_instances,
    goal_state,
    initial_state,
    linear_conflict_spec,
    missionaries_cannibals,
    neighbors,
    render_prompt,
    solve,
    wolf_goat_cabbage,
)


def test_wolf_goat_cabbage_optimal_is_7():
    sol = solve(wolf_goat_cabbage())
    assert sol.optimal_len == 7


def test_missionaries_cannibals_optimal_is_11():
    sol = solve(missionaries_cannibals(n=3, boat_capacity=2))
    assert sol.optimal_len == 11


def test_optimal_trace_starts_at_initial_ends_at_goal():
    spec = wolf_goat_cabbage()
    sol = solve(spec)
    trace = sol.optimal_trace()
    assert trace is not None
    assert trace[0] == initial_state(spec)
    assert trace[-1] == goal_state(spec)
    assert len(trace) == sol.optimal_len + 1


def test_potential_increases_by_one_each_optimal_step():
    spec = wolf_goat_cabbage()
    sol = solve(spec)
    trace = sol.optimal_trace()
    for src, dst in zip(trace, trace[1:]):
        assert sol.transition_value(src, dst) == 1
        assert sol.classify_move(src, dst) == "optimal"


def test_transitions_are_reversible():
    spec = wolf_goat_cabbage()
    sol = solve(spec)
    for state in sol.dist:
        for nb in neighbors(spec, state):
            assert state in neighbors(spec, nb)


def test_unsolvable_instance_reports_unsolvable():
    # Three mutually-conflicting items, boat of 1: any move strands a conflicting
    # pair, so there is no legal move and the goal is unreachable.
    spec = conflict_graph_puzzle(
        cargo=("a", "b", "c"),
        conflicts=(("a", "b"), ("b", "c"), ("a", "c")),
        boat_capacity=1,
    )
    sol = solve(spec)
    assert sol.optimal_len is None
    assert not sol.solvable(initial_state(spec))
    assert neighbors(spec, initial_state(spec)) == []
    # The value oracle marks a step into the unsolvable region as fatal (-inf).
    assert sol.transition_value(goal_state(spec), initial_state(spec)) == -math.inf
    assert sol.classify_move(goal_state(spec), initial_state(spec)) == "fatal"


def test_render_prompt_mentions_items_and_goal():
    prompt = render_prompt(wolf_goat_cabbage())
    for word in ("farmer", "wolf", "goat", "cabbage", "right bank"):
        assert word in prompt


def test_generate_instances_columns_and_values():
    df = generate_instances([wolf_goat_cabbage(), missionaries_cannibals()])
    assert list(df["custom_id"]) == ["wolf-goat-cabbage", "missionaries-cannibals-3"]
    assert set(df.columns) >= {
        "custom_id",
        "prompt",
        "solvable",
        "optimal_len",
        "n_states",
        "n_items",
        "boat_capacity",
    }
    assert df.loc[0, "optimal_len"] == 7
    assert bool(df["solvable"].all())


def test_linear_chain_3_reproduces_wgc_length():
    assert solve(linear_conflict_spec(3, boat_capacity=1)).optimal_len == 7


def test_generate_family_is_solvable_and_has_difficulty_gradient():
    family = generate_family(n_cargo_values=range(3, 6), boat_capacities=(1, 2, 3))
    assert len(family) >= 3
    df = generate_instances(family)
    assert bool(df["solvable"].all())  # solvable_only filtered the rest
    assert df["optimal_len"].nunique() > 1  # a real difficulty gradient
    assert df["n_states"].max() > df["n_states"].min()


def test_spec_validation_rejects_unknown_ferryman():
    try:
        PuzzleSpec(items=("a", "b"), ferryman="missing")
    except ValueError:
        return
    raise AssertionError("expected ValueError for unknown ferryman")
