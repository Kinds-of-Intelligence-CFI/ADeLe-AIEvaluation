"""Tests for adele.instances — canonicalization, validation, manifest, joins."""

import pandas as pd
import pytest

from adele.instances import (
    CANONICALIZERS,
    canonicalize,
    check_join,
    estimate_cost,
    prepare,
    validate_instances,
)


def _loader_frame(prompts, source_ids, benchmark):
    return pd.DataFrame({
        "custom_id": [f"x-{i}" for i in range(len(prompts))],
        "prompt": prompts,
        "benchmark": benchmark,
        "source_id": source_ids,
    })


# ------------------------------------------------------------ canonicalize

def test_canonicalize_aime_splits_years():
    raw = _loader_frame(["p1" * 20, "p2" * 20], ["2025/3", "2026/12"], "aime")
    out = canonicalize("aime", raw)
    assert list(out["benchmark"]) == ["aime-2025", "aime-2026"]
    assert list(out["instance_id"]) == ["3", "12"]


def test_canonicalize_swebench_and_tau():
    raw = _loader_frame(["p" * 40], ["astropy__astropy-12907"], "swebench")
    out = canonicalize("swebench", raw)
    assert out.loc[0, "benchmark"] == "swe-bench-verified"
    assert out.loc[0, "instance_id"] == "astropy__astropy-12907"
    tau = canonicalize("taubench", _loader_frame(["p" * 40], ["airline/task_042"], "taubench"))
    assert tau.loc[0, "benchmark"] == "tau2-airline"
    assert tau.loc[0, "instance_id"] == "task_042"


def test_canonicalize_unknown_loader_fails_loudly():
    with pytest.raises(ValueError, match="CANONICALIZERS"):
        canonicalize("nope", _loader_frame(["p" * 40], ["a"], "nope"))


def test_every_registered_loader_has_a_canonicalizer():
    from adele.agentic.benchmarks import BENCH_LOADERS
    assert set(BENCH_LOADERS) <= set(CANONICALIZERS)


# ------------------------------------------------------------ validate

def test_validate_rejects_duplicates_and_short_prompts():
    ok = pd.DataFrame({"benchmark": ["b"] * 2, "instance_id": ["1", "2"],
                       "prompt": ["x" * 30, "y" * 30]})
    assert validate_instances(ok) == []
    dupe = pd.concat([ok, ok.iloc[[0]]], ignore_index=True)
    with pytest.raises(ValueError, match="duplicate"):
        validate_instances(dupe)
    short = ok.assign(prompt=["x" * 30, "hi"])
    with pytest.raises(ValueError, match="shorter than"):
        validate_instances(short)


def test_validate_warns_on_long_and_identical_prompts():
    df = pd.DataFrame({
        "benchmark": ["b"] * 3, "instance_id": ["1", "2", "3"],
        "prompt": ["z" * 30_000, "same " * 10, "same " * 10],
    })
    warnings = validate_instances(df)
    assert any("exceed" in w for w in warnings)
    assert any("identical" in w for w in warnings)


# ------------------------------------------------------------ cost

def test_estimate_cost_scales_with_dimensions():
    df = pd.DataFrame({"benchmark": ["b"], "instance_id": ["1"], "prompt": ["x" * 4000]})
    est1 = estimate_cost(df, n_dimensions=1)
    est7 = estimate_cost(df, n_dimensions=7)
    assert est7["calls"] == 7 * est1["calls"]
    assert est7["tokens_in"] == pytest.approx(7 * est1["tokens_in"])
    priced = estimate_cost(df, n_dimensions=7, usd_per_mtok_in=1.0, usd_per_mtok_out=5.0)
    assert priced["usd"] > 0


# ------------------------------------------------------------ prepare + join

def _fake_loaders():
    return {
        "aime": lambda: _loader_frame(
            ["problem one " * 5, "problem two " * 5], ["2025/1", "2025/2"], "aime"),
        "swebench": lambda: _loader_frame(
            ["fix the bug " * 5], ["repo__repo-1"], "swebench"),
    }


def test_prepare_freezes_files_and_manifest(tmp_path):
    manifest = prepare(["aime", "swebench"], tmp_path, loaders=_fake_loaders(),
                       n_dimensions=7, fmt="csv")
    assert set(manifest["benchmark"]) == {"aime-2025", "swe-bench-verified"}
    assert (tmp_path / "INSTANCES.tsv").exists()
    frozen = pd.read_csv(tmp_path / "instances_aime-2025.csv", dtype={"instance_id": str})
    assert list(frozen["instance_id"]) == ["1", "2"]
    # manifest hash is stable across a re-run on identical data
    manifest2 = prepare(["aime"], tmp_path, loaders=_fake_loaders(), n_dimensions=7, fmt="csv")
    assert (manifest.set_index("benchmark").loc["aime-2025", "sha256"]
            == manifest2.set_index("benchmark").loc["aime-2025", "sha256"])


def test_check_join_flags_mismatched_canonicalization(tmp_path):
    prepare(["aime", "swebench"], tmp_path, loaders=_fake_loaders(), fmt="csv")
    results = pd.DataFrame({
        "benchmark": ["aime-2025", "aime-2025", "swe-bench-verified"],
        "instance_id": ["1", "2", "DIFFERENT-id"],
        "model": "m", "scaffold": "s", "success": 1.0, "n_trials": 1, "source": "x",
    })
    try:
        results.to_parquet(tmp_path / "results.parquet")
        res_path = tmp_path / "results.parquet"
    except ImportError:
        results.to_csv(tmp_path / "results.csv", index=False)
        res_path = tmp_path / "results.csv"
    report = check_join(tmp_path, res_path).set_index("benchmark")
    assert report.loc["aime-2025", "match_rate"] == 1.0
    assert report.loc["swe-bench-verified", "match_rate"] == 0.0


# ------------------------------------------------------------ dedupe/propagate

def test_unique_prompt_view_and_propagate():
    from adele.instances import propagate_labels, unique_prompt_view
    df = canonicalize("taubench", _loader_frame(
        ["scenario A text long enough", "scenario A text long enough",
         "scenario B text long enough"],
        ["telecom/t1", "telecom/t2", "telecom/t3"], "taubench"))
    view = unique_prompt_view(df)
    assert len(view) == 2                       # 3 tasks -> 2 distinct prompts
    assert view["n_duplicates"].sum() == 3
    assert (view["instance_id"] == view["prompt_sha12"]).all()

    labels = pd.DataFrame({"custom_id": view["prompt_sha12"], "PLp": [2, 4]})
    full = propagate_labels(labels, df)
    assert len(full) == 3
    by = full.set_index("instance_id")["PLp"]
    assert by["t1"] == by["t2"]                 # duplicates share the label
    assert by["t3"] != by["t1"]
