"""
Tests for the annotation module (prompts, parsing, backend detection).
"""

import pytest
import numpy as np
from adele.annotation.prompts import build_annotation_prompt, build_batch_request
from adele.annotation.parsing import extract_demand_level, parse_batch_output
from adele.annotation.annotator import _is_openai_model


class TestBuildAnnotationPrompt:
    """Tests for prompt construction."""

    def test_contains_demand_name(self):
        prompt = build_annotation_prompt(
            demand_name="Attention and Search",
            rubric_content="Level 0: No attention needed.",
            task_instance="What is 2+2?",
        )
        assert "Attention and Search" in prompt

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


class TestBackendDetection:
    """Tests for auto-detecting the annotation backend."""

    @pytest.mark.parametrize("model", [
        "gpt-4o", "gpt-4o-mini", "openai/gpt-4o",
        "o1", "o3-mini", "chatgpt-4o-latest",
    ])
    def test_openai_models_detected(self, model):
        assert _is_openai_model(model) is True

    @pytest.mark.parametrize("model", [
        "gemini/gemini-2.0-flash",
        "claude-sonnet-4-20250514",
        "anthropic/claude-3-5-haiku",
        "meta-llama/Llama-3-8B",
        "mistral/mistral-large",
    ])
    def test_non_openai_models_detected(self, model):
        assert _is_openai_model(model) is False
