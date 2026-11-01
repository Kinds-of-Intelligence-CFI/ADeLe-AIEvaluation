"""Tests for the three-method annotation glue (no API calls)."""

import math
from types import SimpleNamespace

from adele.testbeds.rivercross import (
    MODEL_PRESETS,
    estimate_cost,
    method_1a_frame,
    method_1b_frame,
    method_2_frame,
    reference_trajectories,
    run_annotation,
    trajectories_from_log,
    wolf_goat_cabbage,
)


def _wgc_pairs():
    return reference_trajectories([wolf_goat_cabbage()])


def test_method_1a_frame_one_row_per_instance():
    frame = method_1a_frame([wolf_goat_cabbage()])
    assert list(frame["custom_id"]) == ["wolf-goat-cabbage"]
    assert "river" in frame.loc[0, "prompt"]


def test_method_1b_frame_pairs_states_with_cost_to_go():
    frame = method_1b_frame(_wgc_pairs())
    # 7-move optimal trace -> 7 non-terminal states (goal excluded).
    assert len(frame) == 7
    assert list(frame["custom_id"])[0] == "wolf-goat-cabbage#s0"
    # along the optimal trace, cost-to-go strictly decreases and Phi increases.
    assert list(frame["dist_to_goal"]) == sorted(frame["dist_to_goal"], reverse=True)
    assert bool(frame["solvable"].all())
    assert frame.loc[0, "phi"] == -7


def test_method_2_frame_pairs_transitions_with_exact_value():
    frame = method_2_frame(_wgc_pairs())
    assert len(frame) == 7  # 7 transitions
    assert list(frame["custom_id"])[0] == "wolf-goat-cabbage#t0"
    # every optimal step advances cost-to-go by exactly one.
    assert all(v == 1 for v in frame["transition_value"])
    assert all(c == "optimal" for c in frame["move_class"])


def test_trajectories_from_log_roundtrips_metadata():
    spec = wolf_goat_cabbage()
    score = SimpleNamespace(
        metadata={"trajectory": [{"left": sorted(spec.items), "boat": "L"},
                                 {"left": [], "boat": "R"}]}
    )
    sample = SimpleNamespace(id=spec.name, scores={"river_crossing_scorer": score})
    log = SimpleNamespace(samples=[sample])
    out = trajectories_from_log(log)
    assert out[spec.name][0] == (frozenset(spec.items), "L")
    assert out[spec.name][-1] == (frozenset(), "R")


def test_estimate_cost_scales_with_rows_and_dimensions():
    frame = method_1b_frame(_wgc_pairs())
    est = estimate_cost(frame, ["QLl", "PLp"])
    assert est["n_requests"] == len(frame) * 2
    assert est["approx_input_tokens"] > 0
    assert est["approx_output_tokens"] > 0


def test_run_annotation_dry_run_resolves_preset_and_makes_no_call():
    frame = method_1a_frame([wolf_goat_cabbage()])
    result = run_annotation(frame, ["QLl"], model="haiku")  # dry_run defaults True
    assert result["dry_run"] is True
    assert result["model"] == MODEL_PRESETS["haiku"]
    assert result["estimate"]["n_requests"] == 1
