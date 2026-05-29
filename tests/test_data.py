"""
Tests for the data registry and loader.
"""

import pytest
from adele.data.registry import BenchmarkConfig, get_benchmark, list_benchmarks


class TestBenchmarkRegistry:
    """Tests for the benchmark registry."""

    def test_list_benchmarks_nonempty(self):
        benchmarks = list_benchmarks()
        assert len(benchmarks) == 21

    def test_all_entries_are_configs(self):
        for bm in list_benchmarks():
            assert isinstance(bm, BenchmarkConfig)
            assert bm.name
            assert bm.hf_dataset_id

    def test_get_known_benchmark(self):
        cfg = get_benchmark("mmlu-pro")
        assert cfg is not None
        assert cfg.hf_dataset_id == "TIGER-Lab/MMLU-Pro"

    def test_get_unknown_returns_none(self):
        assert get_benchmark("nonexistent-benchmark") is None

    def test_unique_names(self):
        names = [bm.name for bm in list_benchmarks()]
        assert len(names) == len(set(names))

    def test_all_have_split(self):
        for bm in list_benchmarks():
            assert bm.split, f"{bm.name} has no split"

    def test_all_have_prompt_column(self):
        for bm in list_benchmarks():
            assert bm.prompt_column, f"{bm.name} has no prompt_column"

    def test_mmlu_pro_has_choices_column(self):
        cfg = get_benchmark("mmlu-pro")
        assert cfg.choices_column == "options"


class TestLoader:
    """Tests for load_benchmark."""

    def test_preserves_choices_column(self):
        # We can't easily mock load_dataset, so we test _build_output directly
        # or use a local file test if we had one.
        # Alternatively, we can use a mock df.
        from adele.data.loader import _build_output
        import pandas as pd

        df = pd.DataFrame({
            "q": ["Question 1"],
            "ans": ["A"],
            "opts": [["A", "B", "C", "D"]]
        })
        
        out = _build_output(
            df,
            prompt_column="q",
            id_column=None,
            target_column="ans",
            choices_column="opts",
        )
        assert "choices" in out.columns
        assert out.iloc[0]["choices"] == ["A", "B", "C", "D"]

    def test_list_valued_prompt_column_is_joined(self):
        # LiveBench stores the prompt as a list (`turns`); it must become text.
        from adele.data.loader import _build_output
        import pandas as pd

        df = pd.DataFrame({"turns": [["Solve this puzzle."]], "gt": ["42"]})
        out = _build_output(
            df, prompt_column="turns", id_column=None, target_column="gt",
        )
        assert out.iloc[0]["prompt"] == "Solve this puzzle."
        assert not out.iloc[0]["prompt"].startswith("[")


class TestLoadFromFile:
    """Tests for load_from_file."""

    def test_loads_csv_with_standard_columns(self, tmp_path):
        import pandas as pd
        from adele.data.loader import load_from_file

        csv_path = tmp_path / "test.csv"
        pd.DataFrame({
            "prompt": ["Q1", "Q2"],
            "custom_id": ["a", "b"],
        }).to_csv(csv_path, index=False)

        result = load_from_file(str(csv_path))
        assert list(result.columns) == ["prompt", "custom_id"]
        assert len(result) == 2

    def test_maps_custom_column_names(self, tmp_path):
        import pandas as pd
        from adele.data.loader import load_from_file

        csv_path = tmp_path / "test.csv"
        pd.DataFrame({
            "question": ["Q1"],
            "answer": ["A1"],
        }).to_csv(csv_path, index=False)

        result = load_from_file(
            str(csv_path),
            prompt_column="question",
            id_column=None,
            target_column="answer",
        )
        assert "prompt" in result.columns
        assert "target" in result.columns
        assert result.iloc[0]["prompt"] == "Q1"
        assert result.iloc[0]["target"] == "A1"

    def test_rejects_unsupported_format(self, tmp_path):
        bad_path = tmp_path / "data.xlsx"
        bad_path.touch()
        from adele.data.loader import load_from_file
        with pytest.raises(ValueError, match="Unsupported"):
            load_from_file(str(bad_path))
