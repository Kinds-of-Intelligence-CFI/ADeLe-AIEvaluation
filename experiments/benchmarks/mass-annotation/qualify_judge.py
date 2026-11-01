"""Is a new judge good enough to annotate alongside ours? Compare its labels on the reference subset with the released
labels, against the noise of rerunning our own judge.

    python experiments/benchmarks/mass-annotation/qualify_judge.py qualify-<judge>-pl qualify-<judge>-ms

The runs come from specs/qualify-judge-{pl,ms}.toml.example (150 tasks x PL, 40 tau2 tasks x MS). For each rubric:
- exact agreement and mean shift of the new judge against the released labels (label set "current");
- the yardstick: the same for a same-day rerun of the released judge (runs noreason-ref and noreason-ref-ms,
  Opus 5.5 low with written reasoning);
- agreement with the production judge (Opus 5.5 low, bare digit: runs noreason-pl and noreason-ms).

Verdict, from the agreement and coverage parts of the rule pre-registered for Sonnet (noreason amendment 4). The bar is
the production judge: the gap is the new judge's exact agreement with the released labels minus the production
judge's, per rubric. (Measured against the rerun yardstick, our own production judge sits at -6 points on PLp.)
- **qualified** if every PL rubric's gap is at most 5 points, every MS rubric's at most 10 (only 40 cells each, so
  one cell is 2.5 points), and coverage is at least 95%;
- **not qualified** if the gap is 10 points or more on at least two PL rubrics, or coverage is below 90%;
- **mixed** otherwise.
Qualified means its labels may be compared with ours. Its labels still go in their own label set, never merged into
ours. Criterion validity needs the full sets; check it before any analysis that relies on the new judge alone.
"""

import sys
from pathlib import Path

import pandas as pd

from adele.mass.collect import is_requested
from adele.mass.labelset import load_labelset, labels
from adele.mass.pin import RUNS_ROOT, load_run

KEY = ["benchmark", "instance_id", "rubric"]
YARDSTICK = ["noreason-ref", "noreason-ref-ms"]
PRODUCTION = ["noreason-pl", "noreason-ms"]
PL = ["v2/PLp", "v2/PLe", "v2/PLs"]


def run_labels(runs: list[str], col: str) -> tuple[pd.DataFrame, int]:
    """Valid labels written by each run's requested model, and the number of cells pinned."""
    parts, pinned = [], 0
    for r in runs:
        run = load_run(r)
        pinned += len(run.cells)
        f = RUNS_ROOT / r / "labels.csv"
        if not f.exists():
            continue
        lab = pd.read_csv(f, dtype={"instance_id": str})
        lab = lab[lab["valid"].astype(bool) & lab["writer_model"].astype(str).map(
            lambda w: is_requested(w, run.judge.model))]
        parts.append(pd.DataFrame({"benchmark": lab["benchmark"], "instance_id": lab["instance_id"],
                                   "rubric": lab["rubric_ref"], col: lab["level"].astype(int)}))
    return (pd.concat(parts, ignore_index=True) if parts else pd.DataFrame(columns=KEY + [col])), pinned


def agree(a: pd.Series, b: pd.Series) -> dict:
    ok = a.notna() & b.notna()
    a, b = a[ok].astype(int), b[ok].astype(int)
    return {"n": int(ok.sum()), "exact": round(float((a == b).mean()), 3) if len(a) else None,
            "shift": round(float((a - b).mean()), 2) if len(a) else None}


def main(runs: list[str]) -> None:
    new, pinned = run_labels(runs, "new")
    rel = labels(load_labelset("current"))[KEY + ["level"]].rename(columns={"level": "released"})
    ref, _ = run_labels(YARDSTICK, "ref")
    prod, _ = run_labels(PRODUCTION, "prod")
    df = new.merge(rel, on=KEY, how="left").merge(ref, on=KEY, how="left").merge(prod, on=KEY, how="left")
    df = df[df["ref"].notna()]  # agreement on the reference cells only, where the yardstick exists
    coverage = len(new) / pinned if pinned else 0.0
    rows, gaps = [], {}
    for rubric, g in df.groupby("rubric"):
        a, y = agree(g["new"], g["released"]), agree(g["ref"], g["released"])
        b, p = agree(g["prod"], g["released"]), agree(g["new"], g["prod"])
        if a["exact"] is not None and b["exact"] is not None:
            gaps[rubric] = round(100 * (a["exact"] - b["exact"]))
        rows.append({"rubric": rubric, "n": a["n"], "new vs released": a["exact"], "shift": a["shift"],
                     "production vs released": b["exact"], "gap (points)": gaps.get(rubric),
                     "rerun yardstick": y["exact"], "new vs production": p["exact"]})
    print(pd.DataFrame(rows).to_string(index=False))
    pl_gaps = [gaps[r] for r in PL if r in gaps]
    if coverage < 0.90 or sum(g <= -10 for g in pl_gaps) >= 2:
        verdict = "not qualified"
    elif (len(pl_gaps) == 3 and all(g >= -5 for g in pl_gaps) and coverage >= 0.95
          and all(gaps.get(r, 0) >= -10 for r in ("v2/MSm", "v2/MSc"))):
        verdict = "qualified"
    else:
        verdict = "mixed"
    print(f"\ncoverage {coverage:.3f} ({len(new)} of {pinned} cells labelled by the requested model)")
    print(f"verdict: {verdict}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    main(sys.argv[1:])
