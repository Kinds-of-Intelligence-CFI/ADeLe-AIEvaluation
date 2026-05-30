"""Tests for content-addressed result versioning."""

import re

from adele.evaluation.version import (
    BATTERY_VERSION,
    RUBRICS_LABEL,
    SCORER_LABEL,
    _fingerprint,
    result_version,
    rubrics_version,
    scorer_suite_version,
    version_hash,
)


def test_versions_carry_label_plus_fingerprint():
    rv, sv = rubrics_version(), scorer_suite_version()
    assert rv.startswith(f"{RUBRICS_LABEL}+")
    assert sv.startswith(f"{SCORER_LABEL}+")
    # fingerprint is 8 hex chars
    assert re.fullmatch(r"[0-9a-f]{8}", rv.split("+", 1)[1])
    assert re.fullmatch(r"[0-9a-f]{8}", sv.split("+", 1)[1])


def test_result_version_keys_and_judge_passthrough():
    v = result_version("openai/gpt-4o")
    assert set(v) == {"rubrics", "battery", "scorer_suite", "judge"}
    assert v["battery"] == BATTERY_VERSION
    assert v["judge"] == "openai/gpt-4o"
    assert result_version()["judge"] is None


def test_version_hash_is_deterministic_and_judge_sensitive():
    assert re.fullmatch(r"[0-9a-f]{12}", version_hash("openai/gpt-4o"))
    assert version_hash("openai/gpt-4o") == version_hash("openai/gpt-4o")
    # MC (no judge) and Open-ended (judged) must not collide
    assert version_hash(None) != version_hash("openai/gpt-4o")


def test_fingerprint_is_content_sensitive_and_order_independent(tmp_path):
    a = tmp_path / "a.txt"; a.write_text("alpha")
    b = tmp_path / "b.txt"; b.write_text("beta")
    base = _fingerprint([a, b])

    # order-independent (sorted by name internally)
    assert _fingerprint([b, a]) == base
    # a one-byte content edit changes the fingerprint
    a.write_text("alphax")
    assert _fingerprint([a, b]) != base
