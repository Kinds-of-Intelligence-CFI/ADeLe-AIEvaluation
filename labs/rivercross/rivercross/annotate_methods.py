"""Per-method demand-annotation glue for the river-crossing testbed.

Builds the LLM-judge input frames for the three annotation regimes and pairs the
state/transition rows with the solver's exact value oracle, so methods 1b and 2
carry ground-truth difficulty without a learned value model:

* 1a -- one row per instance; demands of the whole task from its description.
* 1b -- one row per (instance, state); demand-to-go, paired with cost-to-go Phi.
* 2  -- one row per (instance, transition); demand of the crossing, paired with
        the exact transition value Phi(s') - Phi(s).

Actual annotation is delegated to ``adele.annotation.annotate``. Runs are
cost-gated (see ADELE_v2/CLAUDE.md): ``run_annotation`` defaults to a dry run
that only reports a token estimate.
"""

from __future__ import annotations

import pandas as pd

from .play import moves_from_trace
from .puzzle import PuzzleSpec, describe_rules, render_prompt
from .solver import State, goal_state, solve

# A "small group of key rubrics" -- a subset of ADeLe dimensions. QLl is v1.0
# (Logical Reasoning); PLp/MMs are v2 agentic (Planning / Working memory); MCt is
# v1.0 (Critical Thinking). Dimension choice is a methodology call -- confirm
# before a real run. Mixing v1.0 and v2 rubrics needs a composed catalog.
DEFAULT_DIMENSIONS = ["QLl", "PLp", "MMs", "MCt"]

# Convenience aliases for the judge/agent model. ids are adjustable; the judge
# path (litellm) and the Inspect agent path may want slightly different forms
# (e.g. Inspect: "anthropic/<id>", "google/<id>").
MODEL_PRESETS = {
    "haiku": "claude-haiku-4-5-20251001",
    "gemini-flash": "gemini/gemini-2.0-flash",
    "gpt-4o": "gpt-4o",
}


def describe_state(spec: PuzzleSpec, state: State) -> str:
    """A plain-language snapshot of which items are on each bank and the boat side."""
    left, side = state
    right = sorted(set(spec.items) - left)
    left_s = ", ".join(sorted(left)) or "nothing"
    right_s = ", ".join(right) or "nothing"
    boat = "left" if side == "L" else "right"
    return f"Left bank: {left_s}. Right bank: {right_s}. The boat is on the {boat} bank."


def _subproblem_text(spec: PuzzleSpec, state: State) -> str:
    return (
        f"You are partway through a river-crossing puzzle. {describe_rules(spec)} "
        f"Current situation -- {describe_state(spec, state)} "
        "Find a sequence of crossings that gets everything to the right bank from here."
    )


def _transition_text(
    spec: PuzzleSpec, src: State, dst: State, load: frozenset[str]
) -> str:
    movers = ", ".join(sorted(load))
    frm = "left" if src[1] == "L" else "right"
    return (
        f"{describe_rules(spec)} Consider a single crossing in this puzzle. "
        f"Before -- {describe_state(spec, src)} The boat carries {movers} from the "
        f"{frm} bank to the other side. After -- {describe_state(spec, dst)} "
        "Consider only the demands of carrying out this single crossing."
    )


def method_1a_frame(specs: list[PuzzleSpec]) -> pd.DataFrame:
    """Method 1a: annotate the whole task from its initial description."""
    return pd.DataFrame(
        [{"custom_id": spec.name, "prompt": render_prompt(spec)} for spec in specs]
    )


def method_1b_frame(pairs: list[tuple[PuzzleSpec, list[State]]]) -> pd.DataFrame:
    """Method 1b: demand-to-go from each non-terminal state, with exact cost-to-go."""
    rows = []
    for spec, trajectory in pairs:
        sol = solve(spec)
        goal = goal_state(spec)
        for i, state in enumerate(trajectory):
            if state == goal:
                continue
            rows.append(
                {
                    "custom_id": f"{spec.name}#s{i}",
                    "instance": spec.name,
                    "state_index": i,
                    "prompt": _subproblem_text(spec, state),
                    "dist_to_goal": sol.dist.get(state),
                    "phi": sol.potential(state),
                    "solvable": sol.solvable(state),
                }
            )
    return pd.DataFrame(rows)


def method_2_frame(pairs: list[tuple[PuzzleSpec, list[State]]]) -> pd.DataFrame:
    """Method 2: demand of each crossing, with the exact transition value."""
    rows = []
    for spec, trajectory in pairs:
        sol = solve(spec)
        loads = moves_from_trace(trajectory)
        for i, (src, dst, load) in enumerate(zip(trajectory, trajectory[1:], loads)):
            rows.append(
                {
                    "custom_id": f"{spec.name}#t{i}",
                    "instance": spec.name,
                    "transition_index": i,
                    "prompt": _transition_text(spec, src, dst, load),
                    "transition_value": sol.transition_value(src, dst),
                    "move_class": sol.classify_move(src, dst),
                }
            )
    return pd.DataFrame(rows)


def reference_trajectories(
    specs: list[PuzzleSpec],
) -> list[tuple[PuzzleSpec, list[State]]]:
    """Canonical (optimal) rollouts from the solver, so 1b/2 can be annotated
    before any agent is run."""
    out = []
    for spec in specs:
        trace = solve(spec).optimal_trace()
        if trace is not None:
            out.append((spec, trace))
    return out


def trajectories_from_log(
    log, scorer_name: str = "river_crossing_scorer"
) -> dict[str, list[State]]:
    """Recover replayed state trajectories from a completed Inspect eval log."""

    def deserialize(entry: dict) -> State:
        return (frozenset(entry["left"]), entry["boat"])

    out: dict[str, list[State]] = {}
    for sample in getattr(log, "samples", None) or []:
        score = (sample.scores or {}).get(scorer_name)
        meta = getattr(score, "metadata", None) if score else None
        trajectory = (meta or {}).get("trajectory")
        if trajectory:
            out[sample.id] = [deserialize(s) for s in trajectory]
    return out


def estimate_cost(
    frame: pd.DataFrame,
    dimensions: list[str],
    *,
    chars_per_token: int = 4,
    rubric_overhead_tokens: int = 700,
    completion_tokens: int = 400,
) -> dict:
    """Rough token estimate: one judge call per row per dimension. Order-of-magnitude."""
    n_requests = len(frame) * len(dimensions)
    prompt_chars = int(frame["prompt"].str.len().sum()) if len(frame) else 0
    input_tokens = (
        prompt_chars * len(dimensions)
    ) // chars_per_token + n_requests * rubric_overhead_tokens
    return {
        "n_requests": n_requests,
        "approx_input_tokens": int(input_tokens),
        "approx_output_tokens": int(n_requests * completion_tokens),
    }


def run_annotation(
    frame: pd.DataFrame,
    dimensions: list[str] | None = None,
    *,
    model: str = "haiku",
    backend: str | None = None,
    catalog=None,
    rubrics_folder: str | None = None,
    output_dir: str = "./rivercross_annotations",
    dry_run: bool = True,
    **annotate_kwargs,
) -> dict:
    """Annotate ``frame`` over ``dimensions`` with the chosen judge.

    ``model`` may be a ``MODEL_PRESETS`` key ("haiku", "gemini-flash", ...) or a
    raw model string. Defaults to a DRY RUN that returns only a cost estimate;
    pass ``dry_run=False`` to actually call the judge (cost-gated -- review the
    estimate first). Non-OpenAI models route through ``annotate``'s direct
    (litellm) backend and need the provider package + API key.
    """
    dimensions = dimensions or DEFAULT_DIMENSIONS
    model_id = MODEL_PRESETS.get(model, model)
    estimate = estimate_cost(frame, dimensions)
    if dry_run:
        return {
            "dry_run": True,
            "model": model_id,
            "dimensions": dimensions,
            "estimate": estimate,
        }

    from adele.annotation import annotate  # lazy: pulls litellm / provider deps

    annotations = annotate(
        frame,
        demands=dimensions,
        catalog=catalog,
        rubrics_folder=rubrics_folder,
        model=model_id,
        backend=backend,
        output_dir=output_dir,
        **annotate_kwargs,
    )
    return {
        "dry_run": False,
        "model": model_id,
        "dimensions": dimensions,
        "estimate": estimate,
        "annotations": annotations,
    }
