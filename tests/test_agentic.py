"""Tests for the agentic v2 rubric library and the validation harness."""

import pandas as pd
import pytest

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

# The active set is the 8 text/tool-relevant agentic dimensions; the 4
# sensory/motor rubrics live in the library but are deferred (see _DEFERRED_MULTIMODAL).
EXPECTED_CODES = {"PLp", "PLe", "MSe", "MSc", "ECc", "MMe", "MMp", "MMs"}


# ---------------------------------------------------------------------------
# Rubric library
# ---------------------------------------------------------------------------

def test_active_catalog_is_the_text_relevant_eight():
    catalog = load_active_catalog()
    assert set(catalog.acronyms) == EXPECTED_CODES
    # The deferred multimodal dims are excluded from the active set...
    assert not (set(_DEFERRED_MULTIMODAL) & set(catalog.acronyms))


def test_deferred_multimodal_rubrics_still_in_library():
    # ...but their files remain available and valid for later embodied work.
    catalog = RubricsCatalog(str(DATA_V2_DIR / "ours"))
    for code in _DEFERRED_MULTIMODAL:
        rubric = catalog.get(code)
        assert rubric is not None, f"{code} missing from ours/"
        ok, msg = validate_rubric(rubric.content)
        assert ok, f"{code}: {msg}"


def test_active_rubrics_pass_validation():
    for rubric in load_active_catalog():
        ok, msg = validate_rubric(rubric.content)
        assert ok, f"{rubric.acronym}: {msg}"


def test_manifest_has_no_drift():
    # Recorded sha256s match the committed rubric files.
    assert verify_manifest() == []


def test_manifest_sources_split_memory_from_theirs():
    by_code = {e.code: e for e in read_manifest()}
    assert by_code["PLp"].source == "ours"
    assert by_code["MMe"].source == "theirs"
    assert {e.source for e in read_manifest()} == {"ours", "theirs"}


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
