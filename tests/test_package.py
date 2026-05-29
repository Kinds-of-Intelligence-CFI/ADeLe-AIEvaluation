"""The documented top-level API (adele.load_benchmark / annotate / evaluate)."""

import adele


def test_top_level_api_is_callable():
    # The package docstring's Quick Start references these names directly.
    assert callable(adele.load_benchmark)
    assert callable(adele.load_battery)
    assert callable(adele.annotate)
    assert callable(adele.evaluate)


def test_evaluate_aliases_evaluate_model():
    from adele.evaluation import evaluate_model
    assert adele.evaluate is evaluate_model


def test_unknown_attribute_raises():
    import pytest
    with pytest.raises(AttributeError):
        adele.does_not_exist
