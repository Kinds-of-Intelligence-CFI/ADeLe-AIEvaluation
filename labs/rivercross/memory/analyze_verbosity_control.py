"""Analyze the v4 verbosity-control MMs labels.

The v4 run annotates 6 verbose-low items (same traces as the v3 low items,
rewritten so the history text has MORE tokens/object mentions than the high
items) alongside the 12 unmodified v3 medium/high items.

Decision rule, entirely within one v4 run:
- token-counting judge  -> verbose-low scored at or above the high group;
- update-tracking judge -> verbose-low scored below the medium group,
  at the level of the v3 low labels (~1).
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd
from scipy.stats import mannwhitneyu


HERE = Path(__file__).resolve().parent
RIVERCROSS = HERE.parent
FRAMES = RIVERCROSS / "frames"
DEFAULT_CONTRAST_PAIRS = FRAMES / "ground_truth" / "1b_memory_contrast_pairs.csv"
DEFAULT_VERBOSITY_PAIRS = FRAMES / "ground_truth" / "1b_memory_verbosity_pairs.csv"
DEFAULT_FRAME = FRAMES / "1b_memory_verbosity_history_only.csv"


def group_of(custom_id: str, contrast: pd.DataFrame) -> str:
    if custom_id.startswith("memv-"):
        return "verbose-low"
    row = contrast[contrast["custom_id_history_only"] == custom_id]
    if len(row) != 1:
        raise SystemExit(f"cannot map {custom_id} to a v3 contrast group")
    return str(row["contrast_level"].iloc[0])


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--labels", type=Path, action="append", required=True,
                    help="name:path of a v4 history-only label CSV; repeatable")
    ap.add_argument("--v3-low-labels", type=Path, action="append", default=[],
                    help="name:path of the frozen v3 history-only label CSV (low reference)")
    ap.add_argument("--contrast-pairs", type=Path, default=DEFAULT_CONTRAST_PAIRS)
    ap.add_argument("--frame", type=Path, default=DEFAULT_FRAME)
    args = ap.parse_args()

    contrast = pd.read_csv(args.contrast_pairs)
    frame = pd.read_csv(args.frame)
    frame["tokens"] = frame["prompt"].str.split().str.len()

    v3_low: dict[str, pd.Series] = {}
    for spec in args.v3_low_labels:
        name, _, path = str(spec).partition(":")
        labels = pd.read_csv(path)
        merged = contrast.merge(labels, left_on="custom_id_history_only", right_on="custom_id")
        v3_low[name] = merged.loc[merged["contrast_level"] == "low", "level"]

    for spec in args.labels:
        name, _, path = str(spec).partition(":")
        labels = pd.read_csv(path)
        df = labels.merge(frame[["custom_id", "tokens"]], on="custom_id", how="left")
        if df["tokens"].isna().any():
            raise SystemExit(f"{name}: labels contain custom_ids not in the v4 frame")
        df["group"] = df["custom_id"].map(lambda c: group_of(c, contrast))
        df["level"] = pd.to_numeric(df["level"])

        print(f"\n## {name}")
        summary = df.groupby("group")[["level", "tokens"]].agg(["count", "mean", "min", "max"])
        print(summary.to_string(float_format=lambda v: f"{v:.2f}"))

        vlow = df.loc[df["group"] == "verbose-low", "level"]
        high = df.loc[df["group"] == "high", "level"]
        medium = df.loc[df["group"] == "medium", "level"]
        stat, p = mannwhitneyu(vlow, high, alternative="less")
        print(f"mannwhitney verbose-low < high: U={stat:.1f}, p={p:.4g}")
        print(f"verbose-low mean {vlow.mean():.2f} vs medium mean {medium.mean():.2f} "
              f"vs high mean {high.mean():.2f}")
        if name in v3_low:
            print(f"v3 frozen low labels ({name}): mean={v3_low[name].mean():.2f}, "
                  f"values={sorted(v3_low[name].tolist())}")
            print(f"v4 verbose-low labels: values={sorted(vlow.tolist())}")
        verdict = (
            "update-tracking (verbose-low below medium despite most tokens)"
            if vlow.mean() < medium.mean()
            else "token-counting suspected (verbose-low at/above medium)"
        )
        print(f"verdict: {verdict}")


if __name__ == "__main__":
    main()
