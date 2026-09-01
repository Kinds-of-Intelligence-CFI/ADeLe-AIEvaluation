"""Generate a human MMs annotation template for any paired frame set.

Produces one row per pair with the design features, both prompts, and blank
annotation columns including explicit annotator/date fields (the original
9-row spot-check template recorded neither, which the review flagged).

Examples:
  python build_human_template.py \
    --pairs ../frames/ground_truth/1b_memory_contrast_pairs.csv \
    --state-frame ../frames/1b_memory_contrast_state_visible.csv \
    --history-frame ../frames/1b_memory_contrast_history_only.csv \
    --out human_template_v3_full.csv
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
FRAMES = HERE.parent / "frames"

FEATURES = [
    "history_length", "cost_to_go", "object_location_updates",
    "num_reversals", "interference_count", "object_complexity",
]
BLANK_COLUMNS = [
    "annotator", "date", "sv_manual_level", "ho_manual_level",
    "delta_direction_ok", "notes",
]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pairs", type=Path, required=True)
    ap.add_argument("--state-frame", type=Path, required=True)
    ap.add_argument("--history-frame", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()

    pairs = pd.read_csv(args.pairs)
    sv = pd.read_csv(args.state_frame).set_index("custom_id")["prompt"]
    ho = pd.read_csv(args.history_frame).set_index("custom_id")["prompt"]

    lead = ["pair_id"] + (["contrast_level"] if "contrast_level" in pairs.columns else [])
    features = [f for f in FEATURES if f in pairs.columns]
    out = pairs[lead + features].copy()
    out["state_visible_prompt"] = pairs["custom_id_state_visible"].map(sv)
    out["history_only_prompt"] = pairs["custom_id_history_only"].map(ho)
    if out[["state_visible_prompt", "history_only_prompt"]].isna().any().any():
        raise SystemExit("some pairs have no matching prompt in the frames")
    for column in BLANK_COLUMNS:
        out[column] = ""
    out.to_csv(args.out, index=False)
    print(f"wrote {args.out} ({len(out)} pairs)")


if __name__ == "__main__":
    main()
