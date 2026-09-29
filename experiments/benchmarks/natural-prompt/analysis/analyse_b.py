"""Pre-registered analysis of variant B (PREREGISTRATION.md, amendment 1). Writes results/variant_b.json.

Targets come from the 21 cells whose label changed between the old prompt (swepl-gate-low) and the plain
prompt (np-gate-opuslow), judged against the rubric text on 2026-09-29:
  T1  the 12 PLe cells keep the plain prompt's 3 (at least 10 of 12);
  T2  the 4 PLp 1->2 cells and the 2 PLs 1->2 cells go back to the old label (at least 5 of 6);
  T3  the other 111 cells (all but the 21) match the old labels: exact 0.85 or more, and every rubric's
      mean shift within +-0.10;
  A   Sonnet 5.5 high answers the 44 PLp cells: at most 2 without an answer after one retry;
  P   at least 95% of the 132 Opus cells labelled by claude-opus-5-5 and parsed.
The 3 contested PLp cells (11451 and 12143 at 0->1, 15629 at 2->3) are reported, not scored.

    python experiments/benchmarks/natural-prompt/analysis/analyse_b.py
"""

import json
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parents[1]
BENCH = HERE.parent
DIMS = ["PLp", "PLe", "PLs"]
PLE_KEEP = ["django__django-10880", "django__django-11451", "django__django-12143", "django__django-13449",
            "django__django-13741", "django__django-13820", "django__django-14608", "django__django-14787",
            "django__django-15572", "django__django-15930", "sympy__sympy-17139", "sympy__sympy-19346"]
REVERT = [("astropy__astropy-7671", "PLp"), ("django__django-11433", "PLp"),
          ("scikit-learn__scikit-learn-14894", "PLp"), ("sympy__sympy-20916", "PLp"),
          ("django__django-15629", "PLs"), ("django__django-15916", "PLs")]
CONTESTED = [("django__django-11451", "PLp"), ("django__django-12143", "PLp"), ("django__django-15629", "PLp")]


def levels(path: Path, model: str | None = None) -> pd.Series:
    lab = pd.read_csv(path, dtype={"instance_id": str})
    ok = lab["valid"]
    if model:
        ok &= lab["writer_model"].astype(str).str.startswith(model)
    return lab[ok].set_index(["instance_id", "demand"])["level"]


def main() -> None:
    old = levels(BENCH / "swebench-pl/labels/swepl-gate-low/labels_long.csv")
    plain = levels(HERE / "labels/np-gate-opuslow/labels_long.csv", "claude-opus-5-5")
    b = levels(HERE / "labels/npb-gate-opuslow/labels_long.csv", "claude-opus-5-5")
    expected = len(pd.read_csv(HERE / "labels/npb-gate-opuslow/prompts_index.csv"))
    disputed = set(old.index[(old - plain.reindex(old.index)).fillna(0) != 0])
    assert len(disputed) == 21 and {(i, "PLe") for i in PLE_KEEP} | set(REVERT) | set(CONTESTED) == disputed

    t1 = sum(b.get((i, "PLe")) == 3 for i in PLE_KEEP)
    t2 = sum(b.get(c) == old[c] for c in REVERT)
    rest = [c for c in old.index if c not in disputed and c in b.index]
    d = (b[rest] - old[rest])
    by = {dim: round(float(d[[c for c in rest if c[1] == dim]].mean()), 3) for dim in DIMS}
    t3_exact = round(float((d == 0).mean()), 3)

    sa = levels(HERE / "labels/npb-plp-s55h/labels_long.csv", "claude-sonnet-5-5")
    idx = pd.read_csv(HERE / "labels/npb-plp-s55h/prompts_index.csv", dtype={"instance_id": str})
    calls = pd.read_csv(HERE / "labels/npb-plp-s55h/calls.csv")
    unanswered = len(idx) - len(sa)

    checks = {"T1_PLe_kept_ge_10_of_12": t1 >= 10, "T2_reverted_ge_5_of_6": t2 >= 5,
              "T3_rest_exact_ge_0.85": t3_exact >= 0.85, "T3_rest_shift_within_0.10": all(abs(v) <= 0.10 for v in by.values()),
              "A_unanswered_le_2": unanswered <= 2, "P_counted_ge_0.95": len(b) >= 0.95 * expected}
    out = {"T1_PLe_kept": t1, "T2_reverted": t2, "T3_rest_cells": len(rest), "T3_rest_exact": t3_exact,
           "T3_rest_mean_shift": by, "contested": {f"{i}@{dm}": {"old": old[(i, dm)], "plain": plain[(i, dm)],
                                                               "B": b.get((i, dm))} for i, dm in CONTESTED},
           "A_unanswered": unanswered, "A_calls_stopped_by_a_safeguard": int(calls["safeguard_stops"].sum()),
           "B_vs_old_all": {"exact": round(float((b - old.reindex(b.index)).eq(0).mean()), 3),
                            "mean_shift": round(float((b - old.reindex(b.index)).mean()), 3)},
           "checks": checks, "passes": all(checks.values())}
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results/variant_b.json").write_text(json.dumps(out, indent=2, default=float) + "\n")
    print(json.dumps(out, indent=1, default=float))


if __name__ == "__main__":
    main()
