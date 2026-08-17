"""Tests for adele.results — schema, joins, and every offline fetcher path."""

import json

import pandas as pd
import pytest

from adele.results import concat_results, normalize, success_matrix, validate_results
from adele.results.join import coverage_report
from adele.results.schema import merge_trials
from adele.results.sources import arcprize, inspect_scores, swebench, tau2


# ---------------------------------------------------------------- schema

def test_normalize_fills_defaults_and_orders_columns():
    df = pd.DataFrame({"instance_id": ["a"], "model": ["m"], "success": [1]})
    out = normalize(df, benchmark="b", source="s")
    assert list(out.columns[:7]) == [
        "benchmark", "instance_id", "model", "scaffold", "success", "n_trials", "source"
    ]
    assert out.loc[0, "scaffold"] == "none" and out.loc[0, "n_trials"] == 1


def test_validate_rejects_percentages_and_empty_ids():
    base = dict(benchmark="b", model="m", scaffold="s", n_trials=1, source="x")
    with pytest.raises(ValueError, match="percentage"):
        validate_results(pd.DataFrame([{**base, "instance_id": "i", "success": 78.5}]))
    with pytest.raises(ValueError, match="aggregate-only"):
        validate_results(pd.DataFrame([{**base, "instance_id": "", "success": 0.5}]))


def test_validate_rejects_duplicate_cells():
    row = dict(benchmark="b", instance_id="i", model="m", scaffold="s",
               success=1.0, n_trials=1, source="x")
    with pytest.raises(ValueError, match="duplicate"):
        validate_results(pd.DataFrame([row, row]))


def test_merge_trials_averages():
    df = normalize(pd.DataFrame({
        "instance_id": ["i", "i", "i", "j"],
        "model": "m", "success": [1, 0, 0, 1],
    }), benchmark="b", source="s", trial_level=True)
    merged = merge_trials(df)
    assert len(merged) == 2
    i = merged.set_index("instance_id")
    assert i.loc["i", "success"] == pytest.approx(1 / 3)
    assert i.loc["i", "n_trials"] == 3


# ---------------------------------------------------------------- join

def _mini_results():
    return normalize(pd.DataFrame({
        "instance_id": ["t1", "t2", "t1", "t2"],
        "model": ["m1", "m1", "m2", "m2"],
        "success": [1.0, 0.0, 1.0, 1.0],
    }), benchmark="bench", source="src")


def test_success_matrix_and_coverage():
    df = _mini_results()
    mat = success_matrix(df, benchmark="bench")
    assert mat.shape == (2, 2)
    assert mat.loc[("bench", "t2"), "m1/none"] == 0.0
    cov = coverage_report(df)
    assert cov.loc["bench", "m2/none"] == 2


def test_concat_results_keeps_sources_distinct():
    a = _mini_results()
    b = a.copy(); b["source"] = "other-src"
    out = concat_results([a, b])
    assert len(out) == 8  # same cells from two publishers coexist


# ---------------------------------------------------------------- swebench

def test_swebench_fetch_from_fixture_tree(tmp_path):
    entry = tmp_path / "evaluation" / "verified" / "20260101_myscaffold_claude-opus-5" / "results"
    entry.mkdir(parents=True)
    (entry / "results.json").write_text(json.dumps(
        {"resolved": ["repo__repo-1", "repo__repo-2"], "no_generation": 0}))
    entry2 = tmp_path / "evaluation" / "verified" / "20260102_other_gpt-5.6" / "results"
    entry2.mkdir(parents=True)
    (entry2 / "results.json").write_text(json.dumps({"resolved": ["repo__repo-2"]}))

    df = swebench.fetch(tmp_path)
    assert set(df["benchmark"]) == {"swe-bench-verified"}
    assert df["instance_id"].nunique() == 2 and len(df) == 4  # union universe
    cell = df.set_index(["model", "instance_id"])["success"]
    assert cell.loc[("claude-opus-5", "repo__repo-1")] == 1.0
    assert cell.loc[("gpt-5.6", "repo__repo-1")] == 0.0
    assert set(df["scaffold"]) == {"myscaffold", "other"}


def test_swebench_entry_name_split():
    assert swebench.split_entry_name("20251215_livesweagent_claude-opus-4-5") == (
        "livesweagent", "claude-opus-4-5")
    assert swebench.split_entry_name("20251110_frogboss-32b")[1] == "unknown"


# ---------------------------------------------------------------- tau2

def test_tau2_aggregates_from_fixture(tmp_path):
    sub = tmp_path / "web" / "leaderboard" / "public" / "submissions" / "m_org_2026-01-01"
    sub.mkdir(parents=True)
    (sub / "submission.json").write_text(json.dumps({
        "model_name": "Claude Fable 5",
        "results": {"banking_knowledge": {"pass_1": 39.7, "pass_2": 32.8},
                    "airline": None},
        "trajectories_available": True,
    }))
    df = tau2.fetch_aggregates(tmp_path)
    assert len(df) == 1  # null domains skipped
    assert df.loc[0, "benchmark"] == "tau2-banking_knowledge"
    assert df.loc[0, "pass_1"] == 39.7
    # aggregate frames must NOT pass instance-level validation
    assert "instance_id" not in df.columns


# ---------------------------------------------------------------- arcprize (parser only)

def test_arcprize_parse_json_blob_and_glyph_fallback():
    html_json = '{"task_id": "0a1b2c3d", "passed": true} {"task_id": "ffffaaaa", "passed": false}'
    df = arcprize.parse_page(html_json)
    assert df.set_index("instance_id")["success"].to_dict() == {
        "0a1b2c3d": True, "ffffaaaa": False}
    html_glyph = '<tr><td>0a1b2c3d</td><td>✓</td></tr><tr><td>ffffaaaa</td><td>✗</td></tr>'
    df2 = arcprize.parse_page(html_glyph)
    assert df2.set_index("instance_id")["success"].to_dict() == {
        "0a1b2c3d": True, "ffffaaaa": False}


# ---------------------------------------------------------------- partner CSV

def test_ingest_partner_csv_merges_epochs_and_drops_noanswer(tmp_path):
    csv = tmp_path / "scores.csv"
    csv.write_text(
        "benchmark,model,sample_id,epoch,score,log_sha256_12\n"
        "gpqa_diamond,claude-fable-5,q1,1,C,abc\n"
        "gpqa_diamond,claude-fable-5,q1,2,I,abc\n"
        "gpqa_diamond,claude-fable-5,q2,1,N,abc\n"
        "gpqa_diamond,gpt-5.6-sol,q1,1,0.5,def\n"
    )
    df = inspect_scores.from_csv(csv)
    cell = df.set_index(["model", "instance_id"])
    assert cell.loc[("claude-fable-5", "q1"), "success"] == 0.5
    assert cell.loc[("claude-fable-5", "q1"), "n_trials"] == 2
    assert ("claude-fable-5", "q2") not in cell.index          # NOANSWER dropped
    assert cell.loc[("gpt-5.6-sol", "q1"), "success"] == 0.5   # numeric passthrough
