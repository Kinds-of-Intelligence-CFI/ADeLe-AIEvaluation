"""Validate rivercross annotation frames for integrity and oracle leakage."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


HERE = Path(__file__).resolve().parent
DEFAULT_FRAME = HERE / "1b_state_visible.csv"
DEFAULT_GT = HERE / "ground_truth" / "1b_state_visible_cost_to_go.csv"
DEFAULT_HISTORY_FRAME = HERE / "1b_history_only.csv"
DEFAULT_MEMORY_PAIRS = HERE / "ground_truth" / "1b_memory_pairs.csv"

LEAK_TERMS = (
    "cost_to_go",
    "dist_to_goal",
    "solver_depth",
    "optimal_steps",
    "optimal_trace",
    "ground_truth",
)
HISTORY_ONLY_FORBIDDEN_COLUMNS = (
    "true_left",
    "true_right",
    "true_boat",
    "current_left",
    "current_right",
    "current_boat",
    "remaining_steps",
    "solution",
    "oracle",
)
HISTORY_ONLY_FORBIDDEN_PROMPT_TERMS = (
    "current situation",
    "current state",
    "left bank:",
    "right bank:",
    "the boat is on",
    "true_left",
    "true_right",
    "true_boat",
    "cost_to_go",
    "optimal_steps",
    "solver_depth",
    "oracle",
)
HISTORY_ONLY_REQUIRED_PROMPT_TERMS = (
    "initial state",
    "move history",
    "goal",
)
MEMORY_PAIR_COLUMNS = (
    "pair_id",
    "underlying_state_id",
    "custom_id_state_visible",
    "custom_id_history_only",
    "puzzle_id",
    "step_idx",
    "true_left",
    "true_right",
    "true_boat",
    "cost_to_go",
    "history_length",
    "boat_side_updates",
    "object_location_updates",
    "num_unique_objects_moved",
    "num_reversals",
    "interference_count",
    "num_object_moves",
    "num_location_updates",
    "num_repeated_moves",
)


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def validate_frame(path: Path, condition: str) -> tuple[list[dict[str, str]], list[str]]:
    errors: list[str] = []
    rows = read_rows(path)
    require(bool(rows), f"{path} has no rows", errors)
    if not rows:
        return rows, errors

    fieldnames = set(rows[0])
    require("custom_id" in fieldnames, f"{path} missing custom_id column", errors)
    require("prompt" in fieldnames, f"{path} missing prompt column", errors)

    forbidden_columns = set(LEAK_TERMS)
    if condition == "history_only":
        forbidden_columns.update(HISTORY_ONLY_FORBIDDEN_COLUMNS)
    leaked_columns = sorted(c for c in fieldnames if c.lower() in forbidden_columns)
    require(not leaked_columns, f"{path} has leaked columns: {leaked_columns}", errors)

    ids = [row.get("custom_id", "") for row in rows]
    require(len(ids) == len(set(ids)), f"{path} has duplicate custom_id values", errors)

    for i, row in enumerate(rows, start=2):
        cid = row.get("custom_id", "")
        prompt = row.get("prompt", "")
        require(bool(cid), f"{path}:{i} empty custom_id", errors)
        require(bool(prompt.strip()), f"{path}:{i} empty prompt", errors)
        lower_prompt = prompt.lower()

        leaked_terms = [term for term in LEAK_TERMS if term in lower_prompt]
        require(not leaked_terms, f"{path}:{i} prompt leaks oracle terms {leaked_terms}", errors)

        if condition == "history_only":
            missing = [
                term for term in HISTORY_ONLY_REQUIRED_PROMPT_TERMS
                if term not in lower_prompt
            ]
            forbidden = [
                term for term in HISTORY_ONLY_FORBIDDEN_PROMPT_TERMS
                if term in lower_prompt
            ]
            require(not missing, f"{path}:{i} missing history-only terms {missing}", errors)
            require(not forbidden, f"{path}:{i} leaks current-state terms {forbidden}", errors)
    return rows, errors


def validate_ground_truth(path: Path, frame_rows: list[dict[str, str]]) -> list[str]:
    errors: list[str] = []
    gt_rows = read_rows(path)
    gt_ids = {row.get("custom_id", "") for row in gt_rows}
    frame_ids = {row.get("custom_id", "") for row in frame_rows}
    require(frame_ids == gt_ids, f"{path} custom_id set does not match frame", errors)
    columns = set(gt_rows[0]) if gt_rows else set()
    require("dist_to_goal" in columns, f"{path} missing dist_to_goal", errors)
    return errors


def validate_memory_pairs(
    path: Path,
    state_visible_rows: list[dict[str, str]],
    history_rows: list[dict[str, str]],
) -> list[str]:
    errors: list[str] = []
    pair_rows = read_rows(path)
    require(bool(pair_rows), f"{path} has no rows", errors)
    if not pair_rows:
        return errors

    columns = set(pair_rows[0])
    missing_columns = [c for c in MEMORY_PAIR_COLUMNS if c not in columns]
    require(not missing_columns, f"{path} missing columns {missing_columns}", errors)

    pair_ids = [row.get("pair_id", "") for row in pair_rows]
    require(len(pair_ids) == len(set(pair_ids)), f"{path} has duplicate pair_id values", errors)

    state_ids = {row.get("custom_id", "") for row in state_visible_rows}
    history_ids = {row.get("custom_id", "") for row in history_rows}
    pair_state_ids = {row.get("custom_id_state_visible", "") for row in pair_rows}
    pair_history_ids = {row.get("custom_id_history_only", "") for row in pair_rows}
    require(pair_state_ids == state_ids, f"{path} state-visible ids do not match frame", errors)
    require(pair_history_ids == history_ids, f"{path} history-only ids do not match frame", errors)

    numeric_columns = (
        "cost_to_go",
        "history_length",
        "boat_side_updates",
        "object_location_updates",
        "num_unique_objects_moved",
        "num_reversals",
        "interference_count",
        "num_object_moves",
        "num_location_updates",
        "num_repeated_moves",
    )
    for i, row in enumerate(pair_rows, start=2):
        for column in numeric_columns:
            value = row.get(column, "")
            require(value.isdigit(), f"{path}:{i} {column} is not a nonnegative integer", errors)
    return errors


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--condition", choices=("state_visible", "history_only"), default="state_visible")
    ap.add_argument("--frame", type=Path, default=None)
    ap.add_argument("--ground-truth", type=Path, default=DEFAULT_GT)
    ap.add_argument("--state-visible-frame", type=Path, default=DEFAULT_FRAME)
    ap.add_argument("--memory-pairs", type=Path, default=DEFAULT_MEMORY_PAIRS)
    args = ap.parse_args()

    frame_path = args.frame or (DEFAULT_HISTORY_FRAME if args.condition == "history_only" else DEFAULT_FRAME)
    frame_rows, errors = validate_frame(frame_path, args.condition)

    if args.condition == "state_visible":
        if args.ground_truth.exists():
            errors.extend(validate_ground_truth(args.ground_truth, frame_rows))
        else:
            errors.append(f"missing ground truth file: {args.ground_truth}")
    else:
        if args.memory_pairs.exists():
            state_visible_rows = read_rows(args.state_visible_frame)
            errors.extend(validate_memory_pairs(args.memory_pairs, state_visible_rows, frame_rows))
        else:
            errors.append(f"missing memory pair file: {args.memory_pairs}")

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        raise SystemExit(1)
    print(f"validated {frame_path} ({len(frame_rows)} rows), no leakage found")


if __name__ == "__main__":
    main()
