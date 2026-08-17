"""
Tests for the annotation module (prompts, parsing, backend detection).
"""

import json
import pytest
import numpy as np
from adele.annotation.prompts import build_annotation_prompt, build_batch_request
from adele.annotation.parsing import (
    extract_demand_level,
    parse_batch_output,
    to_wide_format,
    unguessability_from_choices,
)
from adele.annotation.annotator import _is_openai_model, annotate


class TestBuildAnnotationPrompt:
    """Tests for prompt construction."""

    def test_contains_demand_name(self):
        prompt = build_annotation_prompt(
            demand_name="Attention and Scan",
            rubric_content="Level 0: No attention needed.",
            task_instance="What is 2+2?",
        )
        assert "Attention and Scan" in prompt

    def test_contains_rubric_content(self):
        rubric = "Level 0: No attention needed. Level 5: Maximum attention."
        prompt = build_annotation_prompt(
            demand_name="Test",
            rubric_content=rubric,
            task_instance="Question?",
        )
        assert rubric in prompt

    def test_contains_task_instance(self):
        prompt = build_annotation_prompt(
            demand_name="Test",
            rubric_content="Rubric",
            task_instance="What is the capital of France?",
        )
        assert "capital of France" in prompt

    def test_contains_chain_of_thought_instruction(self):
        prompt = build_annotation_prompt(
            demand_name="Test",
            rubric_content="Rubric",
            task_instance="Q?",
        )
        assert "CHAIN-OF-THOUGHTS" in prompt
        assert "SCORE" in prompt


class TestBuildBatchRequest:
    """Tests for batch request formatting."""

    def test_structure(self):
        req = build_batch_request(
            custom_id="q1",
            demand_acronym="AS",
            prompt="Test prompt",
            model="gpt-4o",
            max_completion_tokens=500,
        )
        assert req["custom_id"] == "q1__AS"
        assert req["method"] == "POST"
        assert req["url"] == "/v1/chat/completions"
        assert req["body"]["model"] == "gpt-4o"
        assert req["body"]["max_completion_tokens"] == 500

    def test_custom_id_format(self):
        req = build_batch_request("item_42", "MCr", "prompt", "gpt-4o", 1000)
        assert req["custom_id"] == "item_42__MCr"

    def test_temperature_set_for_chat_models(self):
        req = build_batch_request("q1", "AS", "p", "gpt-4o", 500)
        assert req["body"]["temperature"] == 0

    def test_temperature_omitted_for_reasoning_models(self):
        # o1/o3/o4 reject a non-default temperature; it must not be sent.
        for model in ("o1", "o3-mini", "openai/o1-mini", "o4-mini"):
            req = build_batch_request("q1", "AS", "p", model, 500)
            assert "temperature" not in req["body"], model


class TestExtractDemandLevel:
    """Tests for demand level extraction from LLM responses."""

    def test_valid_level(self):
        response = (
            "Some reasoning...\n\n"
            "Thus, the level of *Attention* demanded by the given "
            "TASK INSTANCE is: 3"
        )
        level, ok = extract_demand_level(response)
        assert ok
        assert level == 3.0

    def test_level_zero(self):
        response = "Reasoning...\n\nThe level is: 0"
        level, ok = extract_demand_level(response)
        assert ok
        assert level == 0.0

    def test_level_five(self):
        response = "Reasoning...\n\nThe level is: 5"
        level, ok = extract_demand_level(response)
        assert ok
        assert level == 5.0

    def test_empty_response(self):
        level, ok = extract_demand_level("")
        assert not ok
        assert np.isnan(level)

    def test_none_response(self):
        level, ok = extract_demand_level(None)
        assert not ok

    def test_out_of_range(self):
        response = "Reasoning...\n\nThe level is: 7"
        level, ok = extract_demand_level(response)
        assert not ok

    def test_multi_digit_out_of_range(self):
        """A multi-digit 'is: 12' must be rejected, not truncated to '1'."""
        response = "Reasoning...\n\nThe level is: 12"
        level, ok = extract_demand_level(response)
        assert not ok

    def test_structured_out_of_range_does_not_fabricate(self):
        """An out-of-range structured score must not fall through and grab an
        unrelated in-range number from the text."""
        response = "Based on criterion 3 of the rubric, the level is: 7"
        level, ok = extract_demand_level(response)
        assert not ok  # must be NaN/False, NOT 3.0/True

    def test_structured_pattern_no_paragraphs(self):
        """Should extract via 'is: SCORE' even without paragraph breaks."""
        response = (
            "The task requires moderate reasoning. "
            "The level of *Reasoning* demanded by the given TASK INSTANCE is: 4"
        )
        level, ok = extract_demand_level(response)
        assert ok
        assert level == 4.0

    def test_structured_pattern_preferred_over_fallback(self):
        """The structured 'is: SCORE' should win over stray numbers."""
        response = (
            "Step 1: analyse 3 aspects. Step 2: review 5 items.\n\n"
            "The level of *Knowledge* demanded is: 2"
        )
        level, ok = extract_demand_level(response)
        assert ok
        assert level == 2.0

    def test_truncated_response_with_conclusion(self):
        """A truncated response that still contains 'is: SCORE' should work."""
        response = (
            "Very long reasoning that was truncated... "
            "the level is: 3 and I would have continued but"
        )
        level, ok = extract_demand_level(response)
        assert ok
        assert level == 3.0


class TestUnguessabilityFromChoices:
    """The UG_choice_num (answer-format) -> 0-100 unguessability mapping."""

    def test_open_ended_is_max(self):
        assert unguessability_from_choices("open") == 100.0
        assert unguessability_from_choices("Open-ended") == 100.0

    def test_four_choices_matches_threshold(self):
        # 4 choices -> 75, which is exactly the analysis ug_threshold default.
        assert unguessability_from_choices(4) == 75.0

    def test_two_choices(self):
        assert unguessability_from_choices("2") == 50.0

    def test_single_choice_is_zero(self):
        assert unguessability_from_choices(1) == 0.0

    def test_many_choices(self):
        assert unguessability_from_choices(12) == pytest.approx(100 * 11 / 12)

    def test_unparseable_is_nan(self):
        assert np.isnan(unguessability_from_choices("garbage"))
        assert np.isnan(unguessability_from_choices(None))


class TestBackendDetection:
    """Tests for auto-detecting the annotation backend."""

    @pytest.mark.parametrize("model", [
        "gpt-4o", "gpt-4o-mini", "openai/gpt-4o",
        "o1", "o3-mini", "o4-mini", "chatgpt-4o-latest",
    ])
    def test_openai_models_detected(self, model):
        assert _is_openai_model(model) is True

    @pytest.mark.parametrize("model", [
        "gemini/gemini-2.0-flash",
        "claude-sonnet-4-20250514",
        "anthropic/claude-3-5-haiku",
        "meta-llama/Llama-3-8B",
        "mistral/mistral-large",
        # OpenAI-shaped names behind another provider must NOT use the
        # OpenAI batch client (wrong client/credentials).
        "azure/gpt-4o",
        "openrouter/openai/gpt-4o",
    ])
    def test_non_openai_models_detected(self, model):
        assert _is_openai_model(model) is False


class TestParallelAnnotation:
    """Tests for parallel execution in _annotate_direct."""

    def test_runs_in_parallel(self, monkeypatch, tmp_path):
        """Verify actual concurrency via a high-water-mark counter."""
        import threading
        from adele.annotation.annotator import _annotate_direct
        from adele.rubrics.catalog import RubricsCatalog
        import pandas as pd

        data = pd.DataFrame({
            "prompt": ["p1", "p2", "p3", "p4", "p5"],
            "custom_id": ["1", "2", "3", "4", "5"]
        })
        catalog = RubricsCatalog()
        demands = ["AS"]

        # Track peak concurrency with a thread-safe counter
        lock = threading.Lock()
        active = 0
        peak = 0

        def mock_completion(**kwargs):
            import time
            nonlocal active, peak
            with lock:
                active += 1
                if active > peak:
                    peak = active
            time.sleep(0.05)  # hold the slot briefly
            with lock:
                active -= 1
            class MockResponse:
                class Choice:
                    class Message:
                        content = "Reasoning... The level is: 3"
                    message = Message()
                choices = [Choice()]
            return MockResponse()

        monkeypatch.setattr("litellm.completion", mock_completion)

        _annotate_direct(
            data=data,
            catalog=catalog,
            demands=demands,
            model="mock-model",
            max_completion_tokens=10,
            output_path=tmp_path,
            max_concurrent=5,
        )

        # If truly parallel, peak concurrency should exceed 1
        assert peak >= 2, f"Peak concurrency was {peak}, expected >= 2"


class TestBatchChunking:
    """_create_input_files splits each demand into <=chunk_size-row jobs."""

    def _data(self, n):
        import pandas as pd
        return pd.DataFrame({
            "custom_id": [f"q{i}" for i in range(n)],
            "prompt": [f"Question {i}" for i in range(n)],
        })

    def test_splits_large_demand_into_chunks(self, tmp_path):
        from adele.annotation.annotator import _create_input_files
        from adele.rubrics.catalog import RubricsCatalog
        files = _create_input_files(
            data=self._data(5), catalog=RubricsCatalog(), demands=["AS", "MCr"],
            model="gpt-4o", max_completion_tokens=10, output_dir=tmp_path, chunk_size=2,
        )
        # 5 rows / chunk 2 = 3 chunks per demand × 2 demands
        assert len(files) == 6
        for path in files.values():
            assert sum(1 for line in open(path) if line.strip()) <= 2
        # total requests preserved per demand
        as_lines = sum(sum(1 for _ in open(p)) for k, p in files.items() if k.startswith("AS"))
        assert as_lines == 5

    def test_single_chunk_keeps_plain_filename(self, tmp_path):
        from adele.annotation.annotator import _create_input_files
        from adele.rubrics.catalog import RubricsCatalog
        files = _create_input_files(
            data=self._data(3), catalog=RubricsCatalog(), demands=["AS"],
            model="gpt-4o", max_completion_tokens=10, output_dir=tmp_path, chunk_size=50000,
        )
        assert set(files) == {"AS"}  # no chunk suffix when it fits in one job


class TestToWideFormat:
    """Pivot from long to wide demand columns."""

    def test_keeps_all_nan_demand_column(self):
        import pandas as pd
        # CL failed extraction for every instance -> all NaN. It must still
        # appear as a column rather than silently vanishing.
        long = pd.DataFrame({
            "custom_id": ["a", "b", "a", "b"],
            "demand": ["AS", "AS", "CL", "CL"],
            "level": [2.0, 3.0, float("nan"), float("nan")],
        })
        wide = to_wide_format(long)
        assert "CL" in wide.columns
        assert wide["CL"].isna().all()
        assert wide.columns.name is None


class TestParseBatchOutput:
    """Tests for parsing OpenAI Batch API JSONL output."""

    def _write_jsonl(self, path, items):
        with open(path, "w") as f:
            for item in items:
                f.write(json.dumps(item) + "\n")

    def _make_batch_item(self, custom_id, content, finish_reason="stop"):
        return {
            "custom_id": custom_id,
            "response": {
                "body": {
                    "choices": [{
                        "finish_reason": finish_reason,
                        "message": {"content": content},
                    }]
                }
            },
        }

    def test_parses_valid_output(self, tmp_path):
        output_file = tmp_path / "output.jsonl"
        self._write_jsonl(output_file, [
            self._make_batch_item(
                "q1__AS",
                "Reasoning...\n\nThe level is: 3",
            ),
            self._make_batch_item(
                "q2__MCr",
                "Analysis...\n\nThe level is: 1",
            ),
        ])

        df = parse_batch_output(str(output_file))
        assert len(df) == 2
        assert df.iloc[0]["custom_id"] == "q1"
        assert df.iloc[0]["demand"] == "AS"
        assert df.iloc[0]["level"] == 3.0
        assert df.iloc[1]["custom_id"] == "q2"
        assert df.iloc[1]["demand"] == "MCr"
        assert df.iloc[1]["level"] == 1.0

    def test_truncated_response_still_extracted(self, tmp_path):
        """finish_reason='length' but response contains a valid score."""
        output_file = tmp_path / "output.jsonl"
        self._write_jsonl(output_file, [
            self._make_batch_item(
                "q3__KNa",
                "Long reasoning... the level is: 4 and I would",
                finish_reason="length",
            ),
        ])

        df = parse_batch_output(str(output_file))
        assert len(df) == 1
        assert df.iloc[0]["level"] == 4.0

    def test_error_response_returns_nan(self, tmp_path):
        output_file = tmp_path / "output.jsonl"
        self._write_jsonl(output_file, [
            {"custom_id": "q4__VO", "response": {"body": {}}},
        ])

        df = parse_batch_output(str(output_file))
        assert len(df) == 1
        assert np.isnan(df.iloc[0]["level"])


class TestAnnotateOrchestration:
    """Tests for the main annotate() function with mocked backend."""

    def test_annotate_direct_end_to_end(self, monkeypatch, tmp_path):
        """Full orchestration: rubric loading → prompt → mock LLM → parsing."""
        import pandas as pd

        data = pd.DataFrame({
            "prompt": ["What is 2+2?", "Translate hello"],
            "custom_id": ["q1", "q2"],
        })

        def mock_completion(**kwargs):
            class MockResponse:
                class Choice:
                    class Message:
                        content = (
                            "Reasoning about the task...\n\n"
                            "The level of *demand* demanded by "
                            "the given TASK INSTANCE is: 2"
                        )
                    message = Message()
                choices = [Choice()]
            return MockResponse()

        monkeypatch.setattr("litellm.completion", mock_completion)

        result = annotate(
            data=data,
            demands=["AS"],
            model="mock/model",
            backend="direct",
            output_dir=str(tmp_path),
            max_concurrent=2,
            format="wide",
        )

        # Should return a wide-format DataFrame
        assert "custom_id" in result.columns
        assert "AS" in result.columns
        assert len(result) == 2
        # All levels should be 2.0 (from mock)
        assert (result["AS"] == 2.0).all()

    def test_annotate_rejects_missing_columns(self, tmp_path):
        import pandas as pd
        data = pd.DataFrame({"text": ["no prompt column"]})
        with pytest.raises(ValueError, match="prompt"):
            annotate(data=data, demands=["AS"], model="x",
                     output_dir=str(tmp_path))

    def test_annotate_rejects_bad_rubric(self, tmp_path):
        import pandas as pd
        data = pd.DataFrame({"prompt": ["q"], "custom_id": ["1"]})
        with pytest.raises(ValueError, match="NONEXISTENT"):
            annotate(data=data, demands=["NONEXISTENT"], model="x",
                     output_dir=str(tmp_path))

    def test_annotate_rejects_bad_backend(self, tmp_path):
        import pandas as pd
        data = pd.DataFrame({"prompt": ["q"], "custom_id": ["1"]})
        with pytest.raises(ValueError, match="bad_backend"):
            annotate(data=data, demands=["AS"], model="x",
                     backend="bad_backend", output_dir=str(tmp_path))


class TestParseBatchOutputEdgeCases:
    def test_empty_output_file_yields_empty_frame_with_schema(self, tmp_path):
        from adele.annotation.parsing import parse_batch_output

        empty = tmp_path / "output_AS.jsonl"
        empty.write_text("")
        df = parse_batch_output(empty)
        assert len(df) == 0
        assert list(df.columns) == [
            "custom_id", "demand", "level", "finish_reason", "response",
        ]


class TestResume:
    def test_load_prior_results_keeps_valid_latest_and_retries_invalid(self, tmp_path):
        import json
        from adele.annotation.annotator import _load_prior_results

        raw = tmp_path / "raw_responses.jsonl"
        lines = [
            {"custom_id": "a", "demand": "PLp", "level": 2, "valid": True, "response": "r1"},
            {"custom_id": "a", "demand": "PLp", "level": 3, "valid": True, "response": "r2"},
            {"custom_id": "a", "demand": "PLe", "level": None, "valid": False, "response": ""},
            {"custom_id": "b", "demand": "PLp", "level": 1, "valid": True, "response": "r3"},
        ]
        raw.write_text("\n".join(json.dumps(l) for l in lines) + '\n{"torn')
        prior, done = _load_prior_results(raw)
        assert done == {("a", "PLp"), ("b", "PLp")}      # invalid pair NOT done -> retried
        by = {(r["custom_id"], r["demand"]): r for r in prior}
        assert by[("a", "PLp")]["level"] == 3            # latest valid wins
        assert len(prior) == 2

    def test_load_prior_results_missing_file(self, tmp_path):
        from adele.annotation.annotator import _load_prior_results
        prior, done = _load_prior_results(tmp_path / "nope.jsonl")
        assert prior == [] and done == set()
