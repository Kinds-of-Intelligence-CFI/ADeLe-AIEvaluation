"""
Tests for the ability profiling module.
"""

import pytest
import numpy as np
import pandas as pd
from typing import Dict, List

from adele.analysis.ability import (
    AbilityModel,
    LogisticAbilityModel,
    compute_ability_scores,
    _compute_sample_weights_with_anchor,
    DEMAND_ORDER,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def synthetic_data():
    """Create synthetic demand profiles and correctness data."""
    np.random.seed(42)
    n = 300
    demands = ["AS", "MCr", "KNa"]

    profiles = pd.DataFrame({d: np.random.randint(0, 6, n) for d in demands})
    # Higher max demand → lower probability of correct
    max_demand = profiles.max(axis=1)
    correct = (np.random.rand(n) > max_demand / 6.0).astype(int)

    model_data = pd.DataFrame({
        "custom_id": [f"q{i}" for i in range(n)],
        "correct": correct,
    })
    annotations = profiles.copy()
    annotations["custom_id"] = [f"q{i}" for i in range(n)]

    return model_data, annotations, demands


# ---------------------------------------------------------------------------
# AbilityModel ABC
# ---------------------------------------------------------------------------

class TestAbilityModelABC:
    """Test the abstract base class contract."""

    def test_is_abstract(self):
        import inspect
        assert inspect.isabstract(AbilityModel)

    def test_abstract_methods(self):
        assert "fit" in AbilityModel.__abstractmethods__
        assert "ability_scores" in AbilityModel.__abstractmethods__

    def test_cannot_instantiate(self):
        with pytest.raises(TypeError):
            AbilityModel()

    def test_custom_subclass_works(self):
        class ConstantModel(AbilityModel):
            def fit(self, demand_profiles, correctness, demands, **kw):
                self._demands = demands

            @property
            def ability_scores(self) -> Dict[str, float]:
                return {d: 0.5 for d in self._demands}

        model = ConstantModel()
        profiles = pd.DataFrame({"AS": [1, 2, 3], "MCr": [4, 5, 0]})
        model.fit(profiles, np.array([1, 0, 1]), ["AS", "MCr"])
        scores = model.ability_scores
        assert scores == {"AS": 0.5, "MCr": 0.5}

    def test_predict_default_returns_zeros(self):
        class MinimalModel(AbilityModel):
            def fit(self, demand_profiles, correctness, demands, **kw):
                pass

            @property
            def ability_scores(self) -> Dict[str, float]:
                return {}

        model = MinimalModel()
        model.fit(pd.DataFrame({"AS": [1, 2]}), np.array([0, 1]), ["AS"])
        probs = model.predict_success_probability(pd.DataFrame({"AS": [1, 2, 3]}))
        assert probs.shape == (3,)
        assert np.all(probs == 0)


# ---------------------------------------------------------------------------
# LogisticAbilityModel
# ---------------------------------------------------------------------------

class TestLogisticAbilityModel:
    """Tests for the default logistic regression ability model."""

    def test_is_subclass(self):
        assert issubclass(LogisticAbilityModel, AbilityModel)

    def test_fit_returns_scores_for_all_demands(self, synthetic_data):
        _, annotations, demands = synthetic_data
        profiles = annotations[demands]
        correct = np.random.randint(0, 2, len(profiles))

        model = LogisticAbilityModel()
        model.fit(profiles, correct, demands, level_diff=None)
        scores = model.ability_scores
        assert set(scores.keys()) == set(demands)

    def test_scores_are_bounded(self, synthetic_data):
        _, annotations, demands = synthetic_data
        profiles = annotations[demands]
        correct = np.random.randint(0, 2, len(profiles))

        model = LogisticAbilityModel()
        model.fit(profiles, correct, demands, level_diff=None)
        for d, score in model.ability_scores.items():
            assert 0 <= score <= 1, f"Score for {d} = {score} out of [0, 1]"

    def test_perfect_model_higher_than_zero_model(self):
        """A perfect model should have higher ability than a zero model."""
        profiles = pd.DataFrame({"AS": np.tile([1, 2, 3, 4, 5], 50)})

        perfect = LogisticAbilityModel()
        perfect.fit(profiles, np.ones(250), ["AS"], level_diff=None)

        zero = LogisticAbilityModel()
        zero.fit(profiles, np.zeros(250), ["AS"], level_diff=None)

        assert perfect.ability_scores["AS"] > zero.ability_scores["AS"]

    def test_zero_model_low_ability(self):
        """A model that always fails should have low ability."""
        profiles = pd.DataFrame({"AS": np.tile([1, 2, 3, 4, 5], 50)})
        correct = np.zeros(250)

        model = LogisticAbilityModel()
        model.fit(profiles, correct, ["AS"], level_diff=None)
        assert model.ability_scores["AS"] < 0.2

    def test_predict_success_probability_shape(self, synthetic_data):
        _, annotations, demands = synthetic_data
        profiles = annotations[demands]
        correct = np.random.randint(0, 2, len(profiles))

        model = LogisticAbilityModel()
        model.fit(profiles, correct, demands, level_diff=None)
        probs = model.predict_success_probability(profiles.head(10))
        assert probs.shape == (10,)
        assert np.all((probs >= 0) & (probs <= 1))

    def test_empty_profiles(self):
        profiles = pd.DataFrame({"AS": pd.Series([], dtype=int)})
        correct = np.array([])

        model = LogisticAbilityModel()
        model.fit(profiles, correct, ["AS"], level_diff=None)
        assert model.ability_scores["AS"] == 0.0


# ---------------------------------------------------------------------------
# Sample weights helper
# ---------------------------------------------------------------------------

class TestSampleWeights:
    """Tests for _compute_sample_weights_with_anchor."""

    def test_adds_anchor_point(self):
        X = np.array([1, 2, 3, 4, 5]).reshape(-1, 1)
        y = np.array([1, 1, 0, 0, 0])
        X_out, y_out, w = _compute_sample_weights_with_anchor(X, y)
        assert len(X_out) == len(X) + 1  # anchor added
        assert X_out[-1, 0] == 20  # anchor at level 20
        assert y_out[-1] == 0  # anchor label is 0

    def test_all_weights_positive(self):
        X = np.array([1, 2, 3, 4, 5] * 20).reshape(-1, 1)
        y = np.random.randint(0, 2, 100)
        _, _, w = _compute_sample_weights_with_anchor(X, y, dup_threshold=10)
        assert np.all(w >= 0)

    def test_empty_input_returns_original(self):
        X = np.array([]).reshape(-1, 1)
        y = np.array([])
        X_out, y_out, w = _compute_sample_weights_with_anchor(X, y)
        # With no data, weights are just ones for whatever comes through
        assert len(X_out) == len(y_out) == len(w)


# ---------------------------------------------------------------------------
# compute_ability_scores (integration)
# ---------------------------------------------------------------------------

class TestComputeAbilityScores:
    """Integration tests for the main API function."""

    def test_basic_flow(self, synthetic_data):
        model_data, annotations, demands = synthetic_data
        scores = compute_ability_scores(
            model_data, annotations, demands=demands, level_diff=None
        )
        assert set(scores.keys()) == set(demands)
        for d, s in scores.items():
            assert 0 <= s <= 1

    def test_custom_model_class(self, synthetic_data):
        model_data, annotations, demands = synthetic_data

        class FixedModel(AbilityModel):
            def fit(self, demand_profiles, correctness, demands, **kw):
                self._demands = demands

            @property
            def ability_scores(self) -> Dict[str, float]:
                return {d: 0.99 for d in self._demands}

        scores = compute_ability_scores(
            model_data, annotations,
            demands=demands,
            model_class=FixedModel,
        )
        assert all(s == 0.99 for s in scores.values())

    def test_auto_detects_demands(self, synthetic_data):
        model_data, annotations, _ = synthetic_data
        scores = compute_ability_scores(model_data, annotations)
        # Should auto-detect AS, MCr, KNa from annotations columns
        assert "AS" in scores
        assert "MCr" in scores
        assert "KNa" in scores

    def test_ug_threshold_filtering(self, synthetic_data):
        model_data, annotations, demands = synthetic_data
        # Add a UG column: all instances have UG=50, which is below default 75
        annotations["UG"] = 50
        scores = compute_ability_scores(
            model_data, annotations, demands=demands, level_diff=None
        )
        # All should be 0 because everything gets filtered out
        assert all(s == 0.0 for s in scores.values())
