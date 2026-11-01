"""Tests for the river-crossing play logic and the Inspect task wiring."""

from inspect_ai import eval as inspect_eval
from inspect_ai.model import GenerateConfig, ModelAPI, ModelOutput, get_model, modelapi
from inspect_ai.scorer import CORRECT, INCORRECT

from adele.testbeds.rivercross import (
    initial_state,
    goal_state,
    moves_from_trace,
    parse_moves,
    render_solution,
    replay,
    solve,
    wolf_goat_cabbage,
)
from adele.testbeds.rivercross.task import river_crossing, task_from_specs


def _optimal_loads(spec):
    return moves_from_trace(solve(spec).optimal_trace())


# --- pure play logic (no model needed) ---

def test_optimal_loads_replay_to_goal():
    spec = wolf_goat_cabbage()
    result = replay(spec, _optimal_loads(spec))
    assert result.success
    assert result.first_illegal is None
    assert result.trajectory[0] == initial_state(spec)
    assert result.trajectory[-1] == goal_state(spec)
    assert result.n_moves == 7


def test_render_then_parse_roundtrips():
    spec = wolf_goat_cabbage()
    loads = _optimal_loads(spec)
    text = render_solution(spec, loads)
    assert parse_moves(spec, text) == loads
    assert replay(spec, parse_moves(spec, text)).success


def test_illegal_move_is_flagged():
    spec = wolf_goat_cabbage()
    # First trip takes the wolf, stranding goat+cabbage with no farmer.
    bad = [frozenset({"farmer", "wolf"})]
    result = replay(spec, bad)
    assert not result.success
    assert result.first_illegal == 0


def test_legal_but_incomplete_is_not_success():
    spec = wolf_goat_cabbage()
    # A single legal trip (farmer takes goat) that does not finish the puzzle.
    result = replay(spec, [frozenset({"farmer", "goat"})])
    assert not result.success
    assert result.first_illegal is None


def test_parse_ignores_prose_lines():
    spec = wolf_goat_cabbage()
    text = (
        "Here is my reasoning about the puzzle.\n"
        "1. farmer, goat\n"
        "Then the farmer returns.\n"
        "2. farmer\n"
    )
    assert parse_moves(spec, text) == [
        frozenset({"farmer", "goat"}),
        frozenset({"farmer"}),
    ]


# --- end-to-end Inspect run with a scripted (no-API) model ---

_REPLIES: dict[str, str] = {}


@modelapi(name="rcscript")
def _provider():
    return _ScriptedModel


class _ScriptedModel(ModelAPI):
    def __init__(self, model_name, base_url=None, api_key=None,
                 config=GenerateConfig(), **kwargs):
        super().__init__(model_name, base_url, api_key, [], config)
        self._reply = _REPLIES[model_name.split("/", 1)[-1]]

    async def generate(self, input, tools, tool_choice, config):
        return ModelOutput.from_content(model="rcscript", content=self._reply)


def _fixed_model(content: str):
    key = f"m{len(_REPLIES)}"
    _REPLIES[key] = content
    return get_model(f"rcscript/{key}")


def test_task_scores_optimal_solution_correct(tmp_path):
    spec = wolf_goat_cabbage()
    model = _fixed_model(render_solution(spec, _optimal_loads(spec)))
    task = task_from_specs([spec], name="t")
    log = inspect_eval(tasks=[task], model=model, log_dir=str(tmp_path))[0]

    assert log.status == "success"
    score = log.samples[0].scores["river_crossing_scorer"]
    assert score.value == CORRECT
    # the trajectory rode through into the score metadata and ends at the goal
    trajectory = score.metadata["trajectory"]
    assert trajectory[0] == {"left": sorted(spec.items), "boat": "L"}
    assert trajectory[-1] == {"left": [], "boat": "R"}


def test_task_scores_garbage_incorrect(tmp_path):
    spec = wolf_goat_cabbage()
    model = _fixed_model("I cannot solve this puzzle.")
    task = task_from_specs([spec], name="t")
    log = inspect_eval(tasks=[task], model=model, log_dir=str(tmp_path))[0]
    assert log.samples[0].scores["river_crossing_scorer"].value == INCORRECT


def test_river_crossing_task_builds_family():
    task = river_crossing(n_min=3, n_max=4, capacities="2,3")
    assert len(task.dataset) >= 2
