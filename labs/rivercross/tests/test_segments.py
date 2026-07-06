"""Tests for the flexible multi-step segment builder (method 2, generalised).

No API/LLM calls: everything is exercised against the exact BFS solver oracle on a
synthetic wolf-goat-cabbage session (optimal trace + one injected illegal attempt).
"""

import pytest

from rivercross import (
    WINDOW_STRATEGIES,
    build_spans,
    moves_from_trace,
    replay_session,
    segment_oracle,
    segment_prompt,
    solve,
    wolf_goat_cabbage,
)


def _session():
    """A captured-session dict: the 7-move optimal WGC trace with one illegal try
    injected at the start (farmer takes the wolf first, leaving goat+cabbage)."""
    spec = wolf_goat_cabbage()
    sol = solve(spec)
    trace = sol.optimal_trace()  # 8 states, 7 committed moves
    loads = moves_from_trace(trace)
    trajectory = [{"left": sorted(s[0]), "boat": s[1]} for s in trace]
    attempts = [{"load": ["farmer", "wolf"], "legal": False, "reason": "unsafe"}]
    attempts += [{"load": sorted(load), "legal": True, "reason": "ok"} for load in loads]
    data = {"trajectory": trajectory, "attempts": attempts}
    return spec, sol, data


def test_replay_recovers_states_and_attempts():
    spec, sol, data = _session()
    states, entries = replay_session(spec, data)
    assert len(states) == 8  # start + 7 committed
    assert sum(e.legal for e in entries) == 7
    assert entries[0].legal is False  # the injected illegal attempt at state 0
    assert states[0] == (frozenset(spec.items), "L")
    assert states[-1] == (frozenset(), "R")


def test_dphi_telescopes_to_potential_difference():
    spec, sol, data = _session()
    states, entries = replay_session(spec, data)
    for (i, j) in build_spans(sol, states, "multilen"):
        orc = segment_oracle(sol, states, entries, i, j)
        assert orc["length"] == j - i
        # exact identity: net progress == Phi(s_j) - Phi(s_i)
        assert orc["d_phi"] == sol.potential(states[j]) - sol.potential(states[i])
        # on a perfectly optimal trace every step advances by one, no dip
        assert orc["d_phi"] == j - i
        assert orc["min_phi_dip"] == 0
        assert orc["n_optimal"] == j - i


def test_illegal_attempt_is_attributed_to_the_opening_window_only():
    spec, sol, data = _session()
    states, entries = replay_session(spec, data)
    opening = segment_oracle(sol, states, entries, 0, 2)  # covers state 0
    later = segment_oracle(sol, states, entries, 2, 4)
    assert opening["n_illegal"] == 1
    assert later["n_illegal"] == 0


def test_prompt_mentions_the_rejected_attempt_and_banks():
    spec, sol, data = _session()
    states, entries = replay_session(spec, data)
    prompt = segment_prompt(spec, states, entries, 0, 3)
    assert "ILLEGAL" in prompt          # the correction is surfaced
    assert "Starting situation:" in prompt and "Ending situation:" in prompt
    assert "Score the demand" in prompt


@pytest.mark.parametrize("strategy", WINDOW_STRATEGIES)
def test_spans_are_well_formed(strategy):
    spec, sol, data = _session()
    states, entries = replay_session(spec, data)
    m = len(states) - 1
    spans = build_spans(sol, states, strategy)
    for (i, j) in spans:
        assert 0 <= i < j <= m
    # multilen mixes lengths -> horizon genuinely varies (the whole point)
    if strategy == "multilen":
        assert len({j - i for (i, j) in spans}) >= 2


def test_unknown_strategy_raises():
    spec, sol, data = _session()
    states, _ = replay_session(spec, data)
    with pytest.raises(ValueError):
        build_spans(sol, states, "nonsense")
