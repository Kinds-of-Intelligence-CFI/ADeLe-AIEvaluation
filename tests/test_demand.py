"""
Tests for the demand profiling module.
"""

import pytest
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")

from adele.analysis.demand import compute_demand_profile, plot_demand_profile


@pytest.fixture
def sample_annotations():
    """Create sample wide-format annotations."""
    np.random.seed(0)
    n = 50
    demands = ["AS", "MCr", "KNa", "VO"]
    data = {d: np.random.randint(0, 6, n) for d in demands}
    data["custom_id"] = [f"q{i}" for i in range(n)]
    return pd.DataFrame(data)


class TestComputeDemandProfile:
    """Tests for compute_demand_profile."""

    def test_returns_dataframe(self, sample_annotations):
        profile = compute_demand_profile(sample_annotations)
        assert isinstance(profile, pd.DataFrame)

    def test_all_demands_present(self, sample_annotations):
        profile = compute_demand_profile(sample_annotations)
        demand_values = profile["demand"].unique() if "demand" in profile.columns else profile.index.unique()
        for d in ["AS", "MCr", "KNa", "VO"]:
            assert d in demand_values

    def test_count_values_non_negative(self, sample_annotations):
        profile = compute_demand_profile(sample_annotations)
        if "count" in profile.columns:
            assert (profile["count"] >= 0).all()
        else:
            assert (profile.select_dtypes(include=[np.number]).values >= 0).all()


class TestPlotDemandProfile:
    """Tests for plot_demand_profile."""

    def test_returns_figure(self, sample_annotations):
        import matplotlib.pyplot as plt
        profile = compute_demand_profile(sample_annotations)
        fig = plot_demand_profile(profile)
        assert fig is not None
        plt.close("all")

    def test_save_path(self, sample_annotations, tmp_path):
        import matplotlib.pyplot as plt
        profile = compute_demand_profile(sample_annotations)
        save_path = str(tmp_path / "test_demand.png")
        fig = plot_demand_profile(profile, save_path=save_path)
        import os
        assert os.path.exists(save_path)
        plt.close("all")
