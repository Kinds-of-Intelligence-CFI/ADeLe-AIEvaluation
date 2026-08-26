"""Tests for the agentic v2 rubric library and the validation harness."""

import pandas as pd
import pytest

pytest.importorskip("sklearn", reason="needs the [agentic] extra")
pytest.importorskip("scipy", reason="needs the [agentic] extra")

from pathlib import Path

from adele.agentic import (
    DATA_V2_DIR,
    active_demands,
    load_active_catalog,
    read_manifest,
    verify_manifest,
    _DEFERRED_MULTIMODAL,
)
from adele.agentic.hal import human_label_template, run_judge
from adele.agentic.validation import rubric_agreement
from adele.rubrics.catalog import RubricsCatalog, validate_rubric

# The active set is the 7 text/tool-relevant agentic dimensions; the 4
# sensory/motor rubrics live in the library but are deferred (see _DEFERRED_MULTIMODAL).
# MSe was renamed PLs and then withdrawn 2026-08-16 (rubric deleted from the catalogue);
# ECc was dropped (propensity, not ability); MSm is v1's MS carried into v2.
EXPECTED_CODES = {"PLp", "PLe", "MSm", "MSc", "MMe", "MMp", "MMs"}


# ---------------------------------------------------------------------------
# Rubric library
# ---------------------------------------------------------------------------

def test_active_catalog_is_the_text_relevant_seven():
    catalog = load_active_catalog()
    assert set(catalog.acronyms) == EXPECTED_CODES
    # The deferred multimodal dims are excluded from the active set...
    assert not (set(_DEFERRED_MULTIMODAL) & set(catalog.acronyms))


def test_deferred_multimodal_rubrics_still_in_library():
    # ...but their files remain available and valid for later embodied work.
    catalog = RubricsCatalog(str(DATA_V2_DIR / "Paolo_Pablo"))
    for code in _DEFERRED_MULTIMODAL:
        rubric = catalog.get(code)
        assert rubric is not None, f"{code} missing from Paolo_Pablo/"
        ok, msg = validate_rubric(rubric.content)
        assert ok, f"{code}: {msg}"


def test_active_rubrics_pass_validation():
    for rubric in load_active_catalog():
        ok, msg = validate_rubric(rubric.content)
        assert ok, f"{rubric.acronym}: {msg}"


def test_manifest_has_no_drift():
    # Recorded sha256s match the committed rubric files.
    assert verify_manifest() == []


def _levels(content):
    """Split rubric text into {level_number: block}, examples included."""
    import re
    parts = re.split(r"(?m)^Level (\d):", content)
    return {int(parts[i]): parts[i + 1].strip() for i in range(1, len(parts), 2)}


def test_MSm_adds_only_the_MSc_carve_out_to_v1():
    """MSm is v1's rubric plus one carve-out at L4/L5, so a stance stated outright is not
    scored twice (labs/rubric-qa/r31). Everything else — title, preamble, levels 0-3 —
    must be byte-identical to v1, and the v1 file itself must stay frozen."""
    v1_dir = DATA_V2_DIR.parent / "data_v1"
    assert (v1_dir / "MSm.txt").is_file() and not (v1_dir / "MS.txt").exists()
    v1 = RubricsCatalog(str(v1_dir))["MSm"]
    v2 = load_active_catalog()["MSm"]
    assert v1.full_name == v2.full_name
    a, b = _levels(v1.content), _levels(v2.content)
    for lvl in (0, 1, 2, 3):
        assert a[lvl] == b[lvl], f"level {lvl} must not drift from v1"
    # L4 and L5 differ from v1 by the carve-out sentences and by nothing else: strike those
    # out of the v2 text and what is left must be v1's, character for character.
    CARVE_4 = (" Critically, a stance the other party has stated outright, together with their "
               "reasons, does not have to be modelled: where the task hands over what they "
               "believe and want, the inferring has already been done, and moving them from "
               "that stance is interaction work, not mind modelling. What "
               "places a task at this level is that the mental states driving behaviour must "
               "be worked out, not merely acted upon.")
    CARVE_5 = (" The same carve-out applies here: several parties whose positions are each "
               "stated outright demand no more mind modelling than one, however hard they are "
               "to reconcile.")
    assert CARVE_4 in b[4] and CARVE_5 in b[5]
    assert b[4].replace(CARVE_4, "") == a[4]
    assert b[5].replace(CARVE_5, "") == a[5]


def test_active_catalog_is_single_version():
    """Every active rubric is a v2 draft, so nothing straddles two rubric versions."""
    from adele.rubrics.catalog import warn_if_mixed_versions
    assert load_active_catalog().versions == {"v2-draft"}
    assert warn_if_mixed_versions(load_active_catalog()) is None


def test_MS_code_is_retired_but_aliased_for_published_data():
    """DEMAND_ORDER carries the new code; the released battery's MS column maps to it."""
    from adele.constants import DEMAND_ORDER, LEGACY_DEMAND_ALIASES
    assert "MSm" in DEMAND_ORDER and "MS" not in DEMAND_ORDER
    assert LEGACY_DEMAND_ALIASES["MS"] == "MSm"


def test_manifest_sources_split_memory_from_Marko():
    by_code = {e.code: e for e in read_manifest()}
    assert by_code["PLp"].source == "Paolo_Pablo"
    assert by_code["MMe"].source == "Marko"
    assert by_code["MSm"].source == "Paolo_Pablo"
    # Every active rubric is a v2 draft now; nothing is carried over from v1 as-is.
    assert {e.source for e in read_manifest()} == {"Paolo_Pablo", "Marko"}


def test_from_paths_composes_across_folders():
    entries = read_manifest()
    paths = [e.path for e in entries[:2]] + [e.path for e in entries[-1:]]
    catalog = RubricsCatalog.from_paths(paths)
    assert len(catalog) == 3
    assert catalog["MMs"].full_name == "Working and short-term memory"


# ---------------------------------------------------------------------------
# Agreement metrics
# ---------------------------------------------------------------------------

def test_rubric_agreement_perfect_and_offset():
    judge = pd.DataFrame({
        "custom_id": ["a", "b", "c", "d"],
        "MMe": [0, 2, 4, 5],   # identical to human
        "PLp": [0, 1, 2, 3],   # one instance off by one vs human
    })
    human = pd.DataFrame({
        "custom_id": ["a", "b", "c", "d"],
        "MMe": [0, 2, 4, 5],
        "PLp": [0, 1, 2, 4],
    })
    report = rubric_agreement(judge, human)

    mme = report.dimensions["MMe"]
    assert mme.n == 4
    assert mme.exact == 1.0 and mme.adjacent == 1.0 and mme.mae == 0.0
    assert mme.quadratic_kappa == 1.0 and mme.spearman == pytest.approx(1.0)

    plp = report.dimensions["PLp"]
    assert plp.exact == 0.75 and plp.adjacent == 1.0 and plp.mae == pytest.approx(0.25)
    assert -1.0 <= plp.quadratic_kappa < 1.0
    # Confusion matrix is the full 6×6 grid and counts every instance.
    assert plp.confusion.shape == (6, 6)
    assert int(plp.confusion.to_numpy().sum()) == 4


def test_rubric_agreement_constant_annotator_gives_nan_kappa():
    judge = pd.DataFrame({"custom_id": ["a", "b"], "PLp": [3, 3]})
    human = pd.DataFrame({"custom_id": ["a", "b"], "PLp": [3, 3]})
    plp = rubric_agreement(judge, human).dimensions["PLp"]
    assert plp.exact == 1.0
    assert plp.quadratic_kappa != plp.quadratic_kappa  # NaN: undefined, not 0/1


def test_rubric_agreement_drops_unscored_instances():
    judge = pd.DataFrame({"custom_id": ["a", "b", "c"], "PLp": [1, 2, 3]})
    human = pd.DataFrame({"custom_id": ["a", "b", "c"], "PLp": [1, 2, None]})
    plp = rubric_agreement(judge, human).dimensions["PLp"]
    assert plp.n == 2  # the NaN-human row is dropped


# ---------------------------------------------------------------------------
# Ingest helpers + judge path (mocked, no API)
# ---------------------------------------------------------------------------

def test_human_label_template_schema():
    tasks = pd.DataFrame({"custom_id": ["t1", "t2"], "prompt": ["a", "b"]})
    sheet = human_label_template(tasks, ["PLp", "MMe"])
    assert list(sheet.columns) == ["custom_id", "prompt", "PLp", "MMe"]
    assert sheet[["PLp", "MMe"]].isna().all().all()


def test_sample_pilot_is_seeded_and_join_safe():
    from adele.agentic.benchmarks import sample_pilot, _frame

    fake = {
        "a": lambda: _frame([f"p{i}" for i in range(20)], [f"s{i}" for i in range(20)], "a", "a"),
        "b": lambda: _frame([f"q{i}" for i in range(20)], [f"t{i}" for i in range(20)], "b", "b"),
    }
    s1 = sample_pilot(["a", "b"], n_per=5, seed=0, loaders=fake)
    s2 = sample_pilot(["a", "b"], n_per=5, seed=0, loaders=fake)

    assert len(s1) == 10 and set(s1["benchmark"]) == {"a", "b"}
    assert list(s1["custom_id"]) == list(s2["custom_id"])         # reproducible
    assert not any("__" in cid for cid in s1["custom_id"])        # safe join key
    with pytest.raises(ValueError):
        sample_pilot(["nope"], loaders=fake)


def test_run_judge_uses_active_catalog(monkeypatch, tmp_path):
    tasks = pd.DataFrame({
        "custom_id": ["t1", "t2"],
        "prompt": ["Plan a trip.", "Recall a list."],
    })

    def mock_completion(**kwargs):
        class R:
            class Choice:
                class Message:
                    content = "Reasoning. Thus, the level of *X* demanded by the given TASK INSTANCE is: 2"
                message = Message()
            choices = [Choice()]
        return R()

    monkeypatch.setattr("litellm.completion", mock_completion)
    result = run_judge(
        tasks, model="mock/model", backend="direct",
        output_dir=str(tmp_path), max_concurrent=2,
    )
    # Wide frame over the full active demand set.
    assert "custom_id" in result.columns
    assert set(active_demands()).issubset(set(result.columns))
    assert len(result) == 2
