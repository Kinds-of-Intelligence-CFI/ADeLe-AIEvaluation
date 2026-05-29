"""
Tests for the CLI entry point.
"""

import pytest
from click.testing import CliRunner
from adele.cli import main


@pytest.fixture
def runner():
    return CliRunner()


class TestCLIBasics:
    """Test that CLI commands exist and show help."""

    def test_main_help(self, runner):
        result = runner.invoke(main, ["--help"])
        assert result.exit_code == 0
        assert "ADeLe" in result.output

    def test_version(self, runner):
        result = runner.invoke(main, ["--version"])
        assert result.exit_code == 0
        assert "version" in result.output.lower()


class TestRubricsCLI:
    """Tests for `adele rubrics list`."""

    def test_rubrics_list(self, runner):
        result = runner.invoke(main, ["rubrics", "list"])
        assert result.exit_code == 0
        assert "AS" in result.output
        assert "Attention and Scan" in result.output
        assert "18 rubrics loaded" in result.output


class TestBenchmarksCLI:
    """Tests for `adele benchmarks list`."""

    def test_benchmarks_list(self, runner):
        result = runner.invoke(main, ["benchmarks", "list"])
        assert result.exit_code == 0
        assert "mmlu-pro" in result.output
        assert "21 benchmarks registered" in result.output


class TestAnnotateCLI:
    """Tests for `adele annotate` argument parsing."""

    def test_annotate_help(self, runner):
        result = runner.invoke(main, ["annotate", "--help"])
        assert result.exit_code == 0
        assert "--model" in result.output
        assert "--backend" in result.output
        assert "batch" in result.output
        assert "direct" in result.output

    def test_annotate_no_args(self, runner):
        result = runner.invoke(main, ["annotate"])
        assert result.exit_code != 0  # missing DATASET


class TestEvaluateCLI:
    """Tests for `adele evaluate` argument parsing."""

    def test_evaluate_help(self, runner):
        result = runner.invoke(main, ["evaluate", "--help"])
        assert result.exit_code == 0
        assert "MODEL_ID" in result.output
        assert "DATASET" in result.output

    def test_evaluate_no_args(self, runner):
        result = runner.invoke(main, ["evaluate"])
        assert result.exit_code != 0  # missing arguments


class TestProfileCLI:
    """Tests for `adele profile` argument parsing."""

    def test_profile_help(self, runner):
        result = runner.invoke(main, ["profile", "--help"])
        assert result.exit_code == 0
        assert "ANNOTATIONS_CSV" in result.output
