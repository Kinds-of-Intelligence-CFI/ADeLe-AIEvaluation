"""Inspect AI task for river-crossing puzzles.

Single-shot: the model reads a puzzle and emits a numbered list of crossings.
The scorer replays the moves through the exact rules, marks success (all moves
legal and the goal reached), and records the full state trajectory in the score
metadata so the demand-annotation methods (1a/1b/2) can consume it later.

Run programmatically (``inspect_eval(tasks=[river_crossing()], model=...)``) or,
after a reinstall that registers the entry point, via ``inspect eval``.
"""

from __future__ import annotations

from inspect_ai import Task, task
from inspect_ai.dataset import MemoryDataset, Sample
from inspect_ai.scorer import (
    CORRECT,
    INCORRECT,
    Score,
    Target,
    accuracy,
    scorer,
    stderr,
)
from inspect_ai.solver import TaskState, generate

from .play import parse_moves, replay
from .puzzle import PuzzleSpec, render_prompt
from .solver import State, generate_family, solve


def _output_instructions(spec: PuzzleSpec) -> str:
    rower = f" Include the {spec.ferryman} on every trip." if spec.ferryman else ""
    return (
        "\n\nPresent your solution as a numbered list with one crossing per line, "
        "naming the passengers in the boat on that trip using the exact item "
        f"names.{rower} For example:\n1. <passenger>, <passenger>\n2. <passenger>"
    )


def _serialize_state(state: State) -> dict:
    left, side = state
    return {"left": sorted(left), "boat": side}


def task_from_specs(specs: list[PuzzleSpec], name: str = "river_crossing") -> Task:
    """Build an Inspect Task from explicit puzzle specs."""
    samples = []
    for spec in specs:
        samples.append(
            Sample(
                input=render_prompt(spec) + _output_instructions(spec),
                id=spec.name,
                metadata={
                    "puzzle": spec.to_dict(),
                    "optimal_len": solve(spec).optimal_len,
                },
            )
        )
    return Task(
        dataset=MemoryDataset(samples=samples, name=name),
        solver=[generate()],
        scorer=river_crossing_scorer(),
    )


@scorer(metrics=[accuracy(), stderr()])
def river_crossing_scorer():
    """Replay the model's moves; CORRECT iff all legal and the goal is reached."""

    async def score(state: TaskState, target: Target) -> Score:
        spec = PuzzleSpec.from_dict(state.metadata["puzzle"])
        optimal = state.metadata.get("optimal_len")
        loads = parse_moves(spec, state.output.completion)
        result = replay(spec, loads)

        if result.success:
            explanation = f"Solved in {result.n_moves} crossings (optimal {optimal})."
        elif not loads:
            explanation = "No parseable moves in the response."
        elif result.first_illegal is not None:
            explanation = f"Illegal move at step {result.first_illegal + 1}."
        else:
            explanation = "Moves were legal but did not reach the goal."

        return Score(
            value=CORRECT if result.success else INCORRECT,
            answer=f"{result.n_moves} crossings",
            explanation=explanation,
            metadata={
                "trajectory": [_serialize_state(s) for s in result.trajectory],
                "n_moves": result.n_moves,
                "first_illegal": result.first_illegal,
                "optimal_len": optimal,
            },
        )

    return score


@task
def river_crossing(
    n_min: int = 3,
    n_max: int = 5,
    capacities: str = "1,2,3",
    limit: int | None = None,
) -> Task:
    """A parametrized family of conflict-chain river-crossing puzzles.

    ``capacities`` is a comma-separated list of boat capacities. Only solvable
    instances are kept; ``limit`` truncates the family.
    """
    boat_capacities = tuple(int(c) for c in capacities.split(","))
    specs = generate_family(range(n_min, n_max + 1), boat_capacities)
    if limit is not None:
        specs = specs[:limit]
    return task_from_specs(specs)
