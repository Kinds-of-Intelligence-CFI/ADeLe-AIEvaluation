"""Zero-cost tests for the Inspect evaluation path (mock models, no API key)."""

import os
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from inspect_ai import eval as inspect_eval
from inspect_ai.model import (
    GenerateConfig,
    ModelAPI,
    ModelOutput,
    get_model,
    modelapi,
)

from adele.data import load_battery
from adele.evaluation import (
    adele_battery,
    create_task,
    dataframe_to_samples,
    evaluate_model,
    results_from_log,
)
from adele.evaluation.scoring import choice_letter, final_segment

# Use the real gated battery when ADELE_BATTERY_CSV is set; otherwise fall back
# to the committed mini fixture so the end-to-end eval path is always exercised.
_FIXTURE = Path(__file__).parent / "fixtures" / "mini_battery.csv"
CSV = os.environ.get("ADELE_BATTERY_CSV") or str(_FIXTURE)
needs_csv = pytest.mark.skipif(not CSV, reason="set ADELE_BATTERY_CSV to the battery CSV")


# --- pure scorer logic (no data needed) ---

def test_final_segment_uses_last_marker():
    assert final_segment("the correct answer is: A ... Thus, the correct answer is: C") == "C"


def test_choice_letter_completion_and_groundtruth():
    assert choice_letter("Thus, the correct answer is: B") == "B"
    assert choice_letter("B.Rely on the authority of an expert.") == "B"
    assert choice_letter("no option here") is None


def test_dataframe_to_samples_handles_list_valued_choices():
    # Registry benchmarks with a choices_column (mmlu-pro, sat, ...) load
    # choices as arrays/lists. Regression: pd.notna on a list-valued cell
    # returned an array, raising "truth value ... is ambiguous".
    df = pd.DataFrame({
        "prompt": ["Q1?", "Q2?", "Q3?", "Q4?"],
        "custom_id": ["a", "b", "c", "d"],
        "target": ["A", "B", "C", "D"],
        "choices": [np.array(["x", "y"]), ["u", "v"], "p, q", float("nan")],
    })
    samples = dataframe_to_samples(df)
    assert samples[0].choices == ["x", "y"]   # numpy array (HF datasets)
    assert samples[1].choices == ["u", "v"]   # plain list
    assert samples[2].choices == ["p", "q"]   # comma-separated string (CSV)
    assert samples[3].choices is None         # NaN -> no choices


# --- battery loader + end-to-end with mock models ---

# Per-test reply functions, keyed by id, so the registered provider (which is
# built by name with only string args) can look up the right closure.
_REPLY_FNS = {}


@modelapi(name="scripted")
def _scripted_provider():
    return _ScriptedModel


class _ScriptedModel(ModelAPI):
    """Content-aware mock model: reply = ``fn(last_user_message_text)``.

    The bundled ``mockllm`` only supports a fixed iterable of outputs (consumed
    per call, order-dependent under concurrency), which can't express
    gold-dependent answers. This reads the prompt and computes a reply instead.
    """

    def __init__(self, model_name, base_url=None, api_key=None,
                 config=GenerateConfig(), **model_args):
        super().__init__(model_name, base_url, api_key, [], config)
        self._fn = _REPLY_FNS[model_name.split("/", 1)[-1]]

    async def generate(self, input, tools, tool_choice, config):
        text = input[-1].text
        return ModelOutput.from_content(model="scripted", content=self._fn(text))


def _model(fn):
    key = f"m{len(_REPLY_FNS)}"
    _REPLY_FNS[key] = fn
    return get_model(f"scripted/{key}")


def _fixed_model(content: str):
    return _model(lambda _text: content)


@needs_csv
def test_load_battery_schema():
    df = load_battery(answer_format="MC", max_samples=5, csv_path=CSV)
    assert len(df) == 5
    for col in ("custom_id", "prompt", "target", "answer_format", "CL", "UG", "benchmark"):
        assert col in df.columns
    assert (df["answer_format"] == "MC").all()


@needs_csv
def test_mc_eval_demands_in_metadata_and_correct():
    df = load_battery(answer_format="MC", max_samples=4, csv_path=CSV)
    gold = {str(r["prompt"]): choice_letter(str(r["target"])) for _, r in df.iterrows()}

    model = _model(lambda text: f"Thus, the correct answer is: {gold.get(text, 'A')}")
    task = create_task(df, name="t")
    log = inspect_eval(tasks=[task], model=model, log_dir="/tmp/adele_eval_test")[0]

    assert log.status == "success"
    # demands rode through into the log
    assert log.samples[0].metadata["CL"] is not None
    assert log.samples[0].metadata["answer_format"] == "MC"
    # version recorded
    assert log.eval.metadata["adele_version_hash"]
    # all scored correct (mock answered gold)
    assert all(s.scores["adele_scorer"].value == "C" for s in log.samples)


@needs_csv
def test_evaluate_model_returns_join_contract():
    df = load_battery(answer_format="MC", max_samples=3, csv_path=CSV)
    model = _fixed_model("Thus, the correct answer is: A")
    out = evaluate_model(model, df, log_dir="/tmp/adele_eval_test")
    assert list(out.columns) == ["custom_id", "correct", "model_answer"]
    assert len(out) == 3


@needs_csv
def test_open_ended_routes_to_mock_judge():
    df = load_battery(answer_format="Open-ended", max_samples=2, csv_path=CSV)
    judge = _fixed_model("Looks right.\nGRADE: C")
    task = create_task(df, name="t", judge_model=judge)
    answerer = _fixed_model("Thus, the correct answer is: a response.")
    log = inspect_eval(tasks=[task], model=answerer, log_dir="/tmp/adele_eval_test")[0]
    assert log.status == "success"
    assert all(s.scores["adele_scorer"].value != "N" for s in log.samples)  # not NOANSWER


@needs_csv
def test_results_from_log_bridges_native_run(tmp_path):
    # Inspect-native path: run -> .eval log on disk -> results_from_log -> analysis frame.
    df = load_battery(answer_format="MC", max_samples=3, csv_path=CSV)
    gold = {s.input: choice_letter(s.target) for s in create_task(df, name="t").dataset}

    model = _model(lambda text: f"Thus, the correct answer is: {gold.get(text, 'A')}")
    inspect_eval(tasks=[adele_battery(csv_path=CSV, answer_format="MC", limit=3)],
                 model=model, log_dir=str(tmp_path))

    log_file = next(str(p) for p in tmp_path.glob("*.eval"))
    out = results_from_log(log_file)              # read from disk, by path
    assert list(out.columns) == ["custom_id", "correct", "model_answer"]
    assert len(out) == 3 and out["correct"].sum() == 3
