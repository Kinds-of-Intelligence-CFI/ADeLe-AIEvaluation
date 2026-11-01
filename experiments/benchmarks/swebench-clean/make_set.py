"""Build the SWE-bench Verified clean set (PREREGISTRATION.md): Pablo's rule of 2026-10-01.

Keep every SWE-bench Verified task except:
  never_solved      no entry of the 135 in SWE-bench/experiments (40f164d) resolves it
  openai_named      named by OpenAI's 2026 audit as having tests that reject correct fixes or check unstated
                    behaviour (pylint-dev__pylint-4551, sympy__sympy-18199, django__django-14725)
  utboost_weak      UTBoost (ACL 2025) found its tests too weak: they accept wrong patches (augTest.json, pinned)

Writes tasks.csv: every one of the 500 tasks with its solve count, its exclusion reasons and `keep`.

    python experiments/benchmarks/swebench-clean/make_set.py
"""

import hashlib
import json
import urllib.request
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
UTBOOST_URL = ("https://raw.githubusercontent.com/CUHK-Shenzhen-SE/UTBoost/"
               "47a47c2acd07634fef63535be50a5bbb6bed2c7f/assets/useful_scripts/augTest.json")
UTBOOST_SHA256 = "66cc8846b3e7585853ef57deb39b1698acf4ad17d83c740968e0517fb9e46619"
OPENAI_NAMED = {"pylint-dev__pylint-4551", "sympy__sympy-18199", "django__django-14725"}


def main() -> None:
    raw = urllib.request.urlopen(UTBOOST_URL, timeout=60).read()
    assert hashlib.sha256(raw).hexdigest() == UTBOOST_SHA256, "UTBoost list changed"
    utboost = set(json.loads(raw))

    res = pd.read_parquet(ROOT / "data/results/swebench.parquet")
    assert res.groupby("instance_id")["entry"].nunique().eq(135).all()
    solved = res.groupby("instance_id")["success"].sum().astype(int)
    rate = res.groupby("instance_id")["success"].mean()
    # The same solve rates as swebench-pl's pre-registered sample.
    sample = pd.read_csv(HERE.parent / "swebench-pl/sample.csv").set_index("instance_id")
    assert (rate.reindex(sample.index) - sample["solve_rate"]).abs().max() < 1e-3

    rows = []
    for iid in sorted(rate.index):
        reasons = [r for r, hit in (("never_solved", solved[iid] == 0), ("openai_named", iid in OPENAI_NAMED),
                                    ("utboost_weak", iid in utboost)) if hit]
        rows.append({"instance_id": iid, "solved_by": int(solved[iid]), "of_entries": 135,
                     "solve_rate": round(float(rate[iid]), 4), "excluded_by": ";".join(reasons), "keep": not reasons})
    out = pd.DataFrame(rows)
    assert len(out) == 500 and OPENAI_NAMED <= set(out["instance_id"])
    out.to_csv(HERE / "tasks.csv", index=False)
    ex = out[~out["keep"]]["excluded_by"].str.split(";").explode().value_counts().to_dict()
    print(f"kept {int(out['keep'].sum())} of 500; exclusions by reason (a task can have several): {ex}")


if __name__ == "__main__":
    main()
