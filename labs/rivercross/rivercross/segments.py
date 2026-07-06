"""Flexible multi-step segments for the transition-annotation method (method 2).

The doc's method 2 pins a "transition" to a single ``(action, observation)`` step.
On a horizon-keyed rubric like PLe that is degenerate: one crossing has horizon 1,
immediate legality feedback and no subtask, so every step is pinned to level 0-1 and
the annotated column has ~zero variance (see ``labs/rivercross/README.md``).

This module generalises the unit to a **segment**: a contiguous window of ``L``
committed moves, with ``L`` flexible. ``L == 1`` recovers the old single transition;
``L == M`` (all committed moves) is the whole task (method 1a); the useful regime is
in between. A longer window has a genuinely longer horizon, more corrections and more
feedback points, so a horizon-keyed rubric can finally discriminate.

Each segment is paired with the solver's exact value change over the window --
``dPhi = Phi(s_j) - Phi(s_i)`` -- plus per-step move classes and the count of illegal
attempts inside it. That is the credit-assignment signal method 2 exists for: does a
high-demand stretch coincide with where the agent loses value or errs? No learned value
model is needed; the BFS solver is the oracle.

Everything here is pure and typed (no I/O, no Inspect, no LLM). The driver
``ple/build_segments.py`` feeds it captured interactive sessions and writes frames.
"""

from __future__ import annotations

from dataclasses import dataclass

from .puzzle import PuzzleSpec, describe_rules
from .solver import Solution, State

# ---------------------------------------------------------------------------
# Captured-session replay
# ---------------------------------------------------------------------------

MoveClass = str  # one of: optimal, lateral, backward, recovering, fatal


def _deserialize(entry: dict) -> State:
    return (frozenset(entry["left"]), entry["boat"])


@dataclass(frozen=True)
class Entry:
    """One agent attempt in a captured session (legal move or rejected try)."""

    before: State
    load: frozenset[str]
    legal: bool
    reason: str
    after: State  # == before for an illegal (rejected) attempt
    dest: str  # bank the crossing heads to: "left" or "right"


def replay_session(spec: PuzzleSpec, data: dict) -> tuple[list[State], list[Entry]]:
    """Recover the committed state sequence and the full attempt list.

    ``data`` is a captured interactive session: ``trajectory`` holds only committed
    states (start + one per legal move); ``attempts`` holds every try, legal or not.
    Returns ``(states, entries)`` where ``states[k]`` is the state after ``k`` committed
    moves (so ``len(states) == M + 1``) and ``entries`` is in play order.
    """
    traj = data["trajectory"]
    entries: list[Entry] = []
    cur = _deserialize(traj[0])
    ti = 1
    for att in data["attempts"]:
        dest = "right" if cur[1] == "L" else "left"
        load = frozenset(att["load"])
        reason = att.get("reason", "")
        if att["legal"]:
            after = _deserialize(traj[ti])
            ti += 1
            entries.append(Entry(cur, load, True, reason, after, dest))
            cur = after
        else:
            entries.append(Entry(cur, load, False, reason, cur, dest))
    states = [_deserialize(s) for s in traj]
    return states, entries


def _legal_positions(entries: list[Entry]) -> list[int]:
    """Index in ``entries`` of each committed (legal) move, in order."""
    return [k for k, e in enumerate(entries) if e.legal]


# ---------------------------------------------------------------------------
# Window-selection strategies  (spans over committed-move indices 0..M)
# ---------------------------------------------------------------------------
# A span ``(i, j)`` with ``0 <= i < j <= M`` covers committed moves ``i+1..j``,
# i.e. the stretch from state ``s_i`` to state ``s_j``.


def sliding_windows(m: int, length: int, stride: int = 1) -> list[tuple[int, int]]:
    """All windows of a fixed ``length`` (clamped to the trajectory)."""
    if m <= 0:
        return []
    length = max(1, min(length, m))
    return [(i, i + length) for i in range(0, m - length + 1, stride)]


def multi_length_windows(m: int, lengths: tuple[int, ...]) -> list[tuple[int, int]]:
    """Union of sliding windows over several lengths -- deliberately varies horizon."""
    spans: set[tuple[int, int]] = set()
    for length in lengths:
        spans.update(sliding_windows(m, length))
    return sorted(spans)


def event_anchored_windows(
    sol: Solution, states: list[State], radius: int = 1
) -> list[tuple[int, int]]:
    """Windows centred on non-progress steps (backward / lateral / recovering / fatal).

    These are the interesting execution-control moments -- where the agent burned a
    move or had to recover. ``radius`` committed moves of context are included on
    each side, so the window shows the run-up and the recovery around the event.
    """
    m = len(states) - 1
    spans: set[tuple[int, int]] = set()
    for t in range(1, m + 1):
        if sol.classify_move(states[t - 1], states[t]) != "optimal":
            spans.add((max(0, t - 1 - radius), min(m, t + radius)))
    return sorted(spans)


def subgoal_windows(sol: Solution, states: list[State]) -> list[tuple[int, int]]:
    """Segment boundaries at genuine progress milestones.

    A boundary falls wherever the optimal cost-to-go reaches a new all-time low for
    the trajectory (an irreversible step towards the goal). Consecutive boundaries
    delimit one subgoal's worth of execution, so segment length adapts to how much
    detour the agent took between real progress.
    """
    m = len(states) - 1
    if m <= 0:
        return []
    bounds = [0]
    best = sol.dist.get(states[0], 10**9)
    for t in range(1, m + 1):
        d = sol.dist.get(states[t], 10**9)
        if d < best:
            best = d
            bounds.append(t)
    if bounds[-1] != m:
        bounds.append(m)
    return [(a, b) for a, b in zip(bounds, bounds[1:]) if a < b]


WINDOW_STRATEGIES = ("sliding", "multilen", "event", "subgoal")


def build_spans(
    sol: Solution,
    states: list[State],
    strategy: str = "multilen",
    *,
    length: int = 3,
    lengths: tuple[int, ...] = (2, 3, 4),
    radius: int = 1,
) -> list[tuple[int, int]]:
    """Dispatch to a window-selection strategy. ``m = len(states) - 1`` committed moves."""
    m = len(states) - 1
    if strategy == "sliding":
        return sliding_windows(m, length)
    if strategy == "multilen":
        return multi_length_windows(m, lengths)
    if strategy == "event":
        return event_anchored_windows(sol, states, radius)
    if strategy == "subgoal":
        return subgoal_windows(sol, states)
    raise ValueError(f"unknown strategy {strategy!r}; choose from {WINDOW_STRATEGIES}")


# ---------------------------------------------------------------------------
# Oracle value summary for one segment
# ---------------------------------------------------------------------------


def _class_counts(sol: Solution, states: list[State], i: int, j: int) -> dict[str, int]:
    counts = {c: 0 for c in ("optimal", "lateral", "backward", "recovering", "fatal")}
    for k in range(i, j):
        counts[sol.classify_move(states[k], states[k + 1])] += 1
    return counts


def segment_oracle(
    sol: Solution, states: list[State], entries: list[Entry], i: int, j: int
) -> dict:
    """Exact value signal for the window ``(i, j)`` -- the credit-assignment target.

    ``d_phi`` = Phi(s_j) - Phi(s_i) = optimal moves of net progress over the window
    (equals ``length`` on a perfectly optimal stretch, less when the agent detours).
    ``min_phi_dip`` = how far below Phi(s_i) the potential fell inside the window
    (a wasted excursion that later recovered). ``n_illegal`` counts rejected attempts
    inside the window -- extra execution-control load the horizon alone misses.
    """
    m = len(states) - 1
    phi_i, phi_j = sol.potential(states[i]), sol.potential(states[j])
    min_phi = min(sol.potential(states[k]) for k in range(i, j + 1))
    counts = _class_counts(sol, states, i, j)
    legal_pos = _legal_positions(entries)
    start = 0 if i == 0 else legal_pos[i - 1] + 1
    end = legal_pos[j - 1]  # inclusive
    window = entries[start : end + 1]
    return {
        "i": i,
        "j": j,
        "length": j - i,
        "d_phi": phi_j - phi_i,
        "cost_to_go_start": sol.dist.get(states[i]),
        "cost_to_go_end": sol.dist.get(states[j]),
        "min_phi_dip": phi_i - min_phi,
        "n_optimal": counts["optimal"],
        "n_lateral": counts["lateral"],
        "n_backward": counts["backward"],
        "n_recovering": counts["recovering"],
        "n_fatal": counts["fatal"],
        "n_illegal": sum(1 for e in window if not e.legal),
        "reaches_goal": j == m,
    }


# ---------------------------------------------------------------------------
# Prompt rendering for one segment  (situation text only; the rubric header and
# per-dimension instruction are prepended at annotation time, as in prompt_PLe_*.txt)
# ---------------------------------------------------------------------------


def banks(spec: PuzzleSpec, state: State) -> str:
    left = sorted(state[0])
    right = sorted(set(spec.items) - state[0])
    side = "left" if state[1] == "L" else "right"
    return (
        f"Left: {', '.join(left) or 'nothing'}; "
        f"Right: {', '.join(right) or 'nothing'}; boat on {side}"
    )


def load_str(spec: PuzzleSpec, load: frozenset[str]) -> str:
    items = list(load)
    if spec.ferryman and spec.ferryman in items:
        others = [x for x in items if x != spec.ferryman]
        return spec.ferryman + (" with " + ", ".join(sorted(others)) if others else " alone")
    return ", ".join(sorted(items)) or "(nobody)"


def _step_text(spec: PuzzleSpec, e: Entry, n: int | None) -> str:
    r = e.reason or "(no reason given)"
    if e.legal:
        return (
            f'move {n}: took {load_str(spec, e.load)} to {e.dest} '
            f'(agent: "{r}") -> {banks(spec, e.after)}'
        )
    return (
        f'rejected: tried {load_str(spec, e.load)} to {e.dest} '
        f'(agent: "{r}") -> ILLEGAL, recognised and changed'
    )


def segment_prompt(
    spec: PuzzleSpec, states: list[State], entries: list[Entry], i: int, j: int
) -> str:
    """Single-line situation text for the window ``(i, j)``.

    Frames the stretch to be scored: the rules and goal, how many moves are already
    done, the starting situation, the sequence of committed moves and any rejected
    attempts *inside* the window, and the ending situation.
    """
    rules = describe_rules(spec).strip()
    legal_pos = _legal_positions(entries)
    start = 0 if i == 0 else legal_pos[i - 1] + 1
    end = legal_pos[j - 1]
    window = entries[start : end + 1]

    steps, n = [], i  # committed-move counter continues from i
    for e in window:
        if e.legal:
            n += 1
        steps.append(_step_text(spec, e, n if e.legal else None))
    stretch = " | ".join(steps)

    prior = "none yet" if i == 0 else f"{i} move(s) already completed"
    return (
        f"{rules} Goal: get everything to the right bank. "
        f"Context: {prior}. Starting situation: {banks(spec, states[i])}. "
        f"During this stretch the agent made the following crossings "
        f"(rejected attempts shown where the agent caught its own error): {stretch}. "
        f"Ending situation: {banks(spec, states[j])}. "
        f"Score the demand of carrying out this stretch of execution."
    )
