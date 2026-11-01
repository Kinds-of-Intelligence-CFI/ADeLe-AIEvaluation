"""Tests for the predictive-power (RF assessor) module."""

import numpy as np
import pandas as pd
import pytest

pytest.importorskip("sklearn", reason="needs the [analysis] extra")

from adele.analysis.prediction import (
    compute_predictive_power,
    compute_feature_importances,
    _calculate_ece,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _make_data(n=400, informative=True, seed=0):
    """Synthetic battery: AS strongly (inversely) drives correctness when
    ``informative``; otherwise correctness is independent of the demands."""
    rng = np.random.RandomState(seed)
    AS = rng.randint(0, 6, n)
    MCr = rng.randint(0, 6, n)
    KNa = rng.randint(0, 6, n)
    UG = rng.randint(50, 101, n)

    if informative:
        # higher AS -> lower P(correct)
        p = 1.0 / (1.0 + np.exp(AS - 2.5))
        correct = (rng.rand(n) < p).astype(int)
    else:
        correct = rng.randint(0, 2, n)

    annotations = pd.DataFrame({
        "custom_id": [f"q{i}" for i in range(n)],
        "AS": AS, "MCr": MCr, "KNa": KNa, "UG": UG,
        "benchmark": [f"bench{i % 8}" for i in range(n)],
        "task": [f"task{i % 12}" for i in range(n)],
    })
    model_data = pd.DataFrame({
        "custom_id": [f"q{i}" for i in range(n)],
        "correct": correct,
    })
    return model_data, annotations


# ---------------------------------------------------------------------------
# ECE (pure function)
# ---------------------------------------------------------------------------

class TestECE:
    def test_perfectly_confident_and_correct_is_zero(self):
        y_true = np.ones(50)
        y_prob = np.ones(50)
        assert _calculate_ece(y_true, y_prob) == pytest.approx(0.0)

    def test_confident_but_wrong_is_one(self):
        y_true = np.zeros(50)
        y_prob = np.ones(50)
        assert _calculate_ece(y_true, y_prob) == pytest.approx(1.0)

    def test_bounded(self):
        rng = np.random.RandomState(1)
        ece = _calculate_ece(rng.randint(0, 2, 200), rng.rand(200))
        assert 0.0 <= ece <= 1.0


# ---------------------------------------------------------------------------
# compute_predictive_power
# ---------------------------------------------------------------------------

class TestPredictivePower:
    def test_informative_demands_beat_chance(self):
        model_data, annotations = _make_data(informative=True, seed=1)
        res = compute_predictive_power(
            model_data, annotations, n_folds=5, seeds=(42,)
        )
        assert res["roc_auc"] > 0.65        # demands genuinely predict correctness
        assert 0.0 <= res["ece"] <= 1.0
        assert 0.0 <= res["brier"] <= 1.0
        assert 0.0 <= res["accuracy"] <= 1.0
        assert res["group_by"] == "instance"
        assert res["n_instances"] == 400

    def test_uninformative_demands_near_chance(self):
        model_data, annotations = _make_data(informative=False, seed=2)
        res = compute_predictive_power(
            model_data, annotations, n_folds=5, seeds=(42,)
        )
        # out-of-fold + min_samples_split=50 should not overfit pure noise
        assert res["roc_auc"] < 0.6

    def test_ood_by_benchmark_and_task_run(self):
        model_data, annotations = _make_data(informative=True, seed=3)
        for grp in ("benchmark", "task"):
            res = compute_predictive_power(
                model_data, annotations, group_by=grp, n_folds=4, seeds=(42,)
            )
            assert res["group_by"] == grp
            assert not np.isnan(res["roc_auc"])
            assert res["roc_auc"] > 0.5     # still predictive on held-out groups

    def test_per_seed_recorded(self):
        model_data, annotations = _make_data(seed=4)
        res = compute_predictive_power(
            model_data, annotations, n_folds=5, seeds=(1, 42)
        )
        assert res["n_seeds"] == 2
        assert len(res["per_seed"]["roc_auc"]) == 2
        assert res["roc_auc_std"] >= 0.0

    def test_unknown_group_by_raises(self):
        model_data, annotations = _make_data(seed=5)
        with pytest.raises(ValueError, match="group_by"):
            compute_predictive_power(model_data, annotations, group_by="nope")

    def test_single_class_target_is_degenerate(self):
        model_data, annotations = _make_data(seed=6)
        model_data["correct"] = 1          # only one class
        res = compute_predictive_power(model_data, annotations, seeds=(42,))
        assert res["n_seeds"] == 0
        assert res["accuracy"] == pytest.approx(1.0)
        assert np.isnan(res["roc_auc"])

    def test_include_ug_toggles_feature(self):
        model_data, annotations = _make_data(seed=7)
        with_ug = compute_feature_importances(model_data, annotations, include_ug=True)
        without_ug = compute_feature_importances(model_data, annotations, include_ug=False)
        assert "UG" in with_ug
        assert "UG" not in without_ug


# ---------------------------------------------------------------------------
# compute_feature_importances
# ---------------------------------------------------------------------------

class TestFeatureImportances:
    def test_keys_and_normalisation(self):
        model_data, annotations = _make_data(seed=8)
        imp = compute_feature_importances(model_data, annotations, n_folds=5)
        assert set(imp) == {"UG", "AS", "MCr", "KNa"}
        # impurity importances sum to ~1 across features
        assert sum(imp.values()) == pytest.approx(1.0, abs=1e-6)

    def test_informative_feature_dominates(self):
        model_data, annotations = _make_data(informative=True, seed=9)
        imp = compute_feature_importances(model_data, annotations, n_folds=5)
        # AS drives correctness, so it should be the most important feature
        assert imp["AS"] == max(imp.values())
