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
