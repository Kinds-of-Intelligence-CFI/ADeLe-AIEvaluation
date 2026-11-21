"""Analyze paired MMs labels for the rivercross history-only pilot."""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr, wilcoxon


HERE = Path(__file__).resolve().parent
RIVERCROSS = HERE.parent
DEFAULT_PAIRS = RIVERCROSS / "frames" / "ground_truth" / "1b_memory_pairs.csv"
FEATURES = [
    "history_length",
    "boat_side_updates",
    "object_location_updates",
    "num_unique_objects_moved",
    "num_reversals",
    "interference_count",
    "cost_to_go",
]


def read_labels(path: Path, id_column: str, level_column: str, out_column: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    missing = {id_column, level_column} - set(df.columns)
    if missing:
        raise SystemExit(f"{path} missing columns: {sorted(missing)}")
    return df[[id_column, level_column]].rename(
        columns={id_column: "custom_id", level_column: out_column}
    )


def standardized_regression(df: pd.DataFrame, y_col: str, x_cols: list[str]) -> pd.Series:
    cols = [y_col, *x_cols]
    data = df[cols].astype(float).dropna()
    y = data[y_col].to_numpy()
    x = data[x_cols].to_numpy()
    if len(data) <= len(x_cols):
        raise SystemExit("not enough rows for regression diagnostic")
    y = (y - y.mean()) / (y.std(ddof=0) or 1.0)
    x = (x - x.mean(axis=0)) / np.where(x.std(axis=0, ddof=0) == 0, 1.0, x.std(axis=0, ddof=0))
    x = np.column_stack([np.ones(len(x)), x])
    beta, *_ = np.linalg.lstsq(x, y, rcond=None)
    return pd.Series(beta[1:], index=x_cols)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--state-visible-labels", type=Path, required=True)
    ap.add_argument("--history-only-labels", type=Path, required=True)
    ap.add_argument("--pairs", type=Path, default=DEFAULT_PAIRS)
    ap.add_argument("--id-column", default="custom_id")
    ap.add_argument("--level-column", default="level")
    args = ap.parse_args()

    pairs = pd.read_csv(args.pairs)
    sv = read_labels(args.state_visible_labels, args.id_column, args.level_column, "mms_state_visible")
    ho = read_labels(args.history_only_labels, args.id_column, args.level_column, "mms_history_only")

    df = pairs.merge(
        sv, left_on="custom_id_state_visible", right_on="custom_id", how="left"
    ).drop(columns=["custom_id"])
    df = df.merge(
        ho, left_on="custom_id_history_only", right_on="custom_id", how="left"
    ).drop(columns=["custom_id"])
    if df[["mms_state_visible", "mms_history_only"]].isna().any().any():
        missing = df[df[["mms_state_visible", "mms_history_only"]].isna().any(axis=1)]
        raise SystemExit(f"missing labels for {len(missing)} pairs")

    for col in ["mms_state_visible", "mms_history_only", *FEATURES]:
        df[col] = pd.to_numeric(df[col])
    df["mms_delta"] = df["mms_history_only"] - df["mms_state_visible"]

    print(f"n_pairs: {len(df)}")
    print(f"mean_mms_state_visible: {df['mms_state_visible'].mean():.3f}")
    print(f"mean_mms_history_only: {df['mms_history_only'].mean():.3f}")
    print(f"mean_mms_delta: {df['mms_delta'].mean():.3f}")
    try:
        stat, p = wilcoxon(df["mms_delta"], alternative="greater")
        print(f"wilcoxon_delta_gt_zero: statistic={stat:.3f}, p={p:.4g}")
    except ValueError as exc:
        print(f"wilcoxon_delta_gt_zero: unavailable ({exc})")

    print()
    print("Spearman correlations with mms_delta:")
    for feature in FEATURES:
        if df["mms_delta"].nunique() < 2 or df[feature].nunique() < 2:
            print(f"  {feature}: unavailable (constant input)")
            continue
        rho, p = spearmanr(df["mms_delta"], df[feature])
        print(f"  {feature}: rho={rho:.3f}, p={p:.4g}")

    print()
    print("Standardized regression diagnostics:")
    beta_object = standardized_regression(
        df, "mms_delta", ["object_location_updates", "history_length"]
    )
    print("  mms_delta ~ object_location_updates + history_length")
    for name, value in beta_object.items():
        print(f"    {name}: beta={value:.3f}")

    beta_reversal = standardized_regression(
        df, "mms_delta", ["object_location_updates", "num_reversals", "interference_count", "history_length"]
    )
    print("  mms_delta ~ object_location_updates + num_reversals + interference_count + history_length")
    for name, value in beta_reversal.items():
        print(f"    {name}: beta={value:.3f}")

    beta_controls = standardized_regression(
        df, "mms_delta", ["object_location_updates", "num_reversals", "interference_count", "history_length", "cost_to_go"]
    )
    print("  mms_delta ~ object_update_complexity + history_length + cost_to_go")
    for name, value in beta_controls.items():
        print(f"    {name}: beta={value:.3f}")

    print()
    print("Fixed-history-length means:")
    grouped = df.groupby("history_length")[
        ["mms_delta", "object_location_updates", "num_reversals", "interference_count", "cost_to_go"]
    ].agg(["count", "min", "max", "mean"])
    print(grouped.to_string())


if __name__ == "__main__":
    main()
