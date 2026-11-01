"""Verdicts of the two bulk gates, by the bars set before their labels existed.

    python experiments/benchmarks/mass-annotation/analyse_gates.py api     # GATE-API-BRIDGE.md
    python experiments/benchmarks/mass-annotation/analyse_gates.py v1      # PLAN.md section 3, gate 2

api: API labels (run gate-api-bridge) against the subagent labels on byte-identical prompts (run noreason-pl).
v1:  our v1 labels (run gate-v1-bridge) against the published GPT-4o levels (data/instances/v1_bridge_reference.csv).
"""

import sys
from pathlib import Path

import pandas as pd

from adele.mass.collect import is_requested
from adele.mass.pin import RUNS_ROOT, load_run

REPO = Path(__file__).resolve().parents[3]
KEY = ["benchmark", "instance_id", "rubric_ref"]
YARDSTICK = {"v2/PLp": 0.89, "v2/PLe": 0.93, "v2/PLs": 0.93}  # noreason R' vs released (same-day rerun)


def valid(run: str) -> tuple[pd.DataFrame, int]:
    """Valid labels written by the run's requested model, and the run's number of cells."""
    r = load_run(run)
    df = pd.read_csv(RUNS_ROOT / run / "labels.csv", dtype={"instance_id": str})
    df = df[df["valid"] & df["writer_model"].map(lambda w: is_requested(w, r.judge.model))]
    return df.assign(level=df["level"].astype(int)), len(r.cells)


def api() -> None:
    new, n = valid("gate-api-bridge")
    old, _ = valid("noreason-pl")
    m = new.merge(old, on=KEY, suffixes=("_api", "_sub"))
    coverage = len(new) / n
    verdicts = []
    print(f"coverage {coverage:.3f} ({len(new)}/{n}); compared {len(m)} cells")
    for ref, g in m.groupby("rubric_ref"):
        exact = (g["level_api"] == g["level_sub"]).mean()
        shift = (g["level_api"] - g["level_sub"]).mean()
        bar = YARDSTICK[ref] - 0.05
        ok = exact >= bar and abs(shift) <= 0.15
        fail = exact < YARDSTICK[ref] - 0.10
        verdicts.append("pass" if ok else "fail" if fail else "mixed")
        print(f"{ref}: n {len(g)}, exact {exact:.3f} (bar {bar:.2f}), within 1 "
              f"{((g['level_api'] - g['level_sub']).abs() <= 1).mean():.3f}, shift {shift:+.3f} -> {verdicts[-1]}")
    if coverage < 0.90 or "fail" in verdicts:
        verdict = "FAIL"
    elif coverage >= 0.95 and all(v == "pass" for v in verdicts):
        verdict = "PASS"
    else:
        verdict = "MIXED"
    print(f"verdict: {verdict}")


def v1() -> None:
    ours, n = valid("gate-v1-bridge")
    ref = pd.read_csv(REPO / "data" / "instances" / "v1_bridge_reference.csv", dtype={"instance_id": str})
    ref = ref.drop(columns=["source"]).melt(id_vars="instance_id", var_name="code", value_name="level_ref")
    ours["code"] = ours["rubric_ref"].str.split("/").str[1]
    m = ours.merge(ref, on=["instance_id", "code"])
    print(f"coverage {len(ours)}/{n}; compared {len(m)} cells")
    miss = []
    for code, g in m.groupby("code"):
        d = g["level"] - g["level_ref"]
        within, shift = (d.abs() <= 1).mean(), d.mean()
        ok = within >= 0.85 and abs(shift) <= 0.3
        miss += [] if ok else [code]
        print(f"{code}: n {len(g)}, exact {(d == 0).mean():.3f}, within 1 {within:.3f}, shift {shift:+.2f}"
              f" -> {'comparable' if ok else 'NOT comparable to the v1 battery'}")
    print(f"not comparable: {', '.join(miss) or 'none'}")


if __name__ == "__main__":
    {"api": api, "v1": v1}[sys.argv[1] if len(sys.argv) > 1 else "api"]()
