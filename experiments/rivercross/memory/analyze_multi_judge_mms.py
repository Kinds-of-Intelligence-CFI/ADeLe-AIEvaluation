"""Analyze multi-judge paired MMs labels for the rivercross contrast pilot."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr, wilcoxon


HERE = Path(__file__).resolve().parent
RIVERCROSS = HERE.parent
DEFAULT_PAIRS = RIVERCROSS / "frames" / "ground_truth" / "1b_memory_contrast_pairs.csv"
DEFAULT_HISTORY_FRAME = RIVERCROSS / "frames" / "1b_memory_contrast_history_only.csv"
FEATURES = [
    "history_length",
    "object_location_updates",
    "num_reversals",
    "interference_count",
    "cost_to_go",
    "history_prompt_tokens",
]


@dataclass(frozen=True)
class JudgeSpec:
    name: str
    state_visible: Path
    history_only: Path


def parse_judge(value: str) -> JudgeSpec:
    parts = value.split(":", 2)
    if len(parts) != 3:
        raise argparse.ArgumentTypeError(
            "judge must be formatted as name:state_visible_labels.csv:history_only_labels.csv"
        )
    name, state_visible, history_only = parts
    if not name:
        raise argparse.ArgumentTypeError("judge name cannot be empty")
    return JudgeSpec(name=name, state_visible=Path(state_visible), history_only=Path(history_only))


def read_labels(path: Path, id_column: str, level_column: str, out_column: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    missing = {id_column, level_column} - set(df.columns)
    if missing:
        raise SystemExit(f"{path} missing columns: {sorted(missing)}")
    return df[[id_column, level_column]].rename(
        columns={id_column: "custom_id", level_column: out_column}
    )


def standardized_regression(df: pd.DataFrame, y_col: str, x_cols: list[str]) -> pd.Series:
    data = df[[y_col, *x_cols]].astype(float).dropna()
    if len(data) <= len(x_cols):
        return pd.Series({name: np.nan for name in x_cols})
    y = data[y_col].to_numpy()
    x = data[x_cols].to_numpy()
    y = (y - y.mean()) / (y.std(ddof=0) or 1.0)
    x_std = x.std(axis=0, ddof=0)
    x = (x - x.mean(axis=0)) / np.where(x_std == 0, 1.0, x_std)
    x = np.column_stack([np.ones(len(x)), x])
    beta, *_ = np.linalg.lstsq(x, y, rcond=None)
    return pd.Series(beta[1:], index=x_cols)


def load_judge_df(pairs: pd.DataFrame, judge: JudgeSpec, id_column: str, level_column: str) -> pd.DataFrame:
    sv = read_labels(judge.state_visible, id_column, level_column, "mms_state_visible")
    ho = read_labels(judge.history_only, id_column, level_column, "mms_history_only")
    df = pairs.merge(
        sv, left_on="custom_id_state_visible", right_on="custom_id", how="left"
    ).drop(columns=["custom_id"])
    df = df.merge(
        ho, left_on="custom_id_history_only", right_on="custom_id", how="left"
    ).drop(columns=["custom_id"])
    if df[["mms_state_visible", "mms_history_only"]].isna().any().any():
        missing = df[df[["mms_state_visible", "mms_history_only"]].isna().any(axis=1)]
        raise SystemExit(f"{judge.name}: missing labels for {len(missing)} pairs")
    for col in ["mms_state_visible", "mms_history_only", *FEATURES]:
        df[col] = pd.to_numeric(df[col])
    df["mms_delta"] = df["mms_history_only"] - df["mms_state_visible"]
    df["judge"] = judge.name
    return df


def attach_prompt_tokens(pairs: pd.DataFrame, history_frame: Path) -> pd.DataFrame:
    """Whitespace token count of each history-only prompt.

    In the v3 design object mentions in the history scale with
    object_location_updates, so a judge that merely counts history verbosity
    is observationally similar to one that tracks state updates. Reporting
    Spearman(delta, history_prompt_tokens) alongside the design features makes
    that collinearity explicit instead of hiding it.
    """
    frame = pd.read_csv(history_frame)
    tokens = frame.assign(
        history_prompt_tokens=frame["prompt"].str.split().str.len()
    )[["custom_id", "history_prompt_tokens"]]
    return pairs.merge(
        tokens, left_on="custom_id_history_only", right_on="custom_id", how="left"
    ).drop(columns=["custom_id"])


def summarize_cells(df: pd.DataFrame, judge: str) -> None:
    """Aggregate replicate pairs into design cells before testing.

    The -01/-02 replicates share identical feature vectors, so pair-level
    p-values overstate the evidence (pseudo-replication). Cell-level stats on
    the ~9 unique design cells are the honest unit of analysis.
    """
    cell_key = df["pair_id"].str.rsplit("-", n=1).str[0]
    cells = (
        df.assign(cell=cell_key)
        .groupby("cell", sort=False)
        .agg(
            n=("mms_delta", "size"),
            mms_delta=("mms_delta", "mean"),
            object_location_updates=("object_location_updates", "mean"),
            history_length=("history_length", "mean"),
        )
    )
    print(f"Per-cell (replicates averaged, n_cells={len(cells)}):")
    print(cells.to_string(float_format=lambda v: f"{v:.2f}"))
    try:
        stat, p = wilcoxon(cells["mms_delta"], alternative="greater")
        print(f"cell_wilcoxon_delta_gt_zero: statistic={stat:.3f}, p={p:.4g}")
    except ValueError as exc:
        print(f"cell_wilcoxon_delta_gt_zero: unavailable ({exc})")
    if cells["mms_delta"].nunique() >= 2:
        rho, p = spearmanr(cells["mms_delta"], cells["object_location_updates"])
        print(f"cell_spearman(delta, object_location_updates): rho={rho:.3f}, p={p:.4g}")


def quadratic_weighted_kappa(a: np.ndarray, b: np.ndarray) -> float:
    a = np.asarray(a, dtype=int)
    b = np.asarray(b, dtype=int)
    lo = min(a.min(), b.min())
    hi = max(a.max(), b.max())
    if lo == hi:
        return 1.0
    labels = np.arange(lo, hi + 1)
    n = len(labels)
    index = {label: i for i, label in enumerate(labels)}
    observed = np.zeros((n, n), dtype=float)
    for x, y in zip(a, b):
        observed[index[x], index[y]] += 1
    hist_a = observed.sum(axis=1)
    hist_b = observed.sum(axis=0)
    expected = np.outer(hist_a, hist_b) / observed.sum()
    weights = np.zeros((n, n), dtype=float)
    denom = (n - 1) ** 2
    for i in range(n):
        for j in range(n):
            weights[i, j] = ((i - j) ** 2) / denom
    observed_weighted = (weights * observed).sum()
    expected_weighted = (weights * expected).sum()
    if expected_weighted == 0:
        return 1.0
    return 1.0 - observed_weighted / expected_weighted


def summarize_judge(df: pd.DataFrame, judge: str) -> None:
    print(f"\n## {judge}")
    print(f"n_pairs: {len(df)}")
    print(f"mean_mms_state_visible: {df['mms_state_visible'].mean():.3f}")
    print(f"mean_mms_history_only: {df['mms_history_only'].mean():.3f}")
    print(f"mean_mms_delta: {df['mms_delta'].mean():.3f}")
    try:
        stat, p = wilcoxon(df["mms_delta"], alternative="greater")
        print(f"wilcoxon_delta_gt_zero: statistic={stat:.3f}, p={p:.4g}")
    except ValueError as exc:
        print(f"wilcoxon_delta_gt_zero: unavailable ({exc})")
    print("Spearman(delta, feature):")
    for feature in FEATURES:
        if df["mms_delta"].nunique() < 2 or df[feature].nunique() < 2:
            print(f"  {feature}: unavailable")
            continue
        rho, p = spearmanr(df["mms_delta"], df[feature])
        print(f"  {feature}: rho={rho:.3f}, p={p:.4g}")
    beta = standardized_regression(
        df,
        "mms_delta",
        ["object_location_updates", "history_length", "cost_to_go"],
    )
    print("Regression: mms_delta ~ object_location_updates + history_length + cost_to_go")
    for name, value in beta.items():
        print(f"  {name}: beta={value:.3f}")
    if df["history_prompt_tokens"].notna().all():
        beta_tokens = standardized_regression(
            df, "mms_delta", ["object_location_updates", "history_prompt_tokens"]
        )
        print("Regression: mms_delta ~ object_location_updates + history_prompt_tokens")
        for name, value in beta_tokens.items():
            print(f"  {name}: beta={value:.3f}")
    summarize_cells(df, judge)


def summarize_cross_judge(all_df: pd.DataFrame) -> None:
    judges = list(dict.fromkeys(all_df["judge"].tolist()))
    if len(judges) < 2:
        print("\n## Cross-judge agreement")
        print("Need at least two judges for cross-judge agreement diagnostics.")
        return
    wide = all_df.pivot(index="pair_id", columns="judge", values="mms_delta")
    print("\n## Cross-judge agreement on mms_delta")
    for i, left in enumerate(judges):
        for right in judges[i + 1:]:
            pair = wide[[left, right]].dropna()
            if len(pair) == 0:
                print(f"{left} vs {right}: no overlapping pairs")
                continue
            if pair[left].nunique() < 2 or pair[right].nunique() < 2:
                rho, p = np.nan, np.nan
            else:
                rho, p = spearmanr(pair[left], pair[right])
            within_1 = (pair[left].sub(pair[right]).abs() <= 1).mean()
            qwk = quadratic_weighted_kappa(pair[left].to_numpy(), pair[right].to_numpy())
            print(
                f"{left} vs {right}: n={len(pair)}, "
                f"spearman_delta={rho:.3f}, p={p:.4g}, "
                f"within1={within_1:.3f}, qwk={qwk:.3f}"
            )


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pairs", type=Path, default=DEFAULT_PAIRS)
    ap.add_argument("--history-frame", type=Path, default=DEFAULT_HISTORY_FRAME)
    ap.add_argument("--judge", action="append", type=parse_judge, required=True)
    ap.add_argument("--id-column", default="custom_id")
    ap.add_argument("--level-column", default="level")
    args = ap.parse_args()

    pairs = pd.read_csv(args.pairs)
    if args.history_frame.exists():
        pairs = attach_prompt_tokens(pairs, args.history_frame)
    else:
        pairs["history_prompt_tokens"] = np.nan
    dfs = [load_judge_df(pairs, judge, args.id_column, args.level_column) for judge in args.judge]
    for df in dfs:
        summarize_judge(df, df["judge"].iloc[0])
    summarize_cross_judge(pd.concat(dfs, ignore_index=True))


if __name__ == "__main__":
    main()
