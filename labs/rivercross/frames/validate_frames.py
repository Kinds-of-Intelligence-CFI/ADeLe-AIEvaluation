"""Validate rivercross annotation frames for basic integrity and oracle leakage."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


HERE = Path(__file__).resolve().parent
DEFAULT_FRAME = HERE / "1b_state_visible.csv"
DEFAULT_GT = HERE / "ground_truth" / "1b_state_visible_cost_to_go.csv"
LEAK_TERMS = (
    "cost_to_go",
    "dist_to_goal",
    "solver_depth",
    "optimal_steps",
    "optimal_trace",
    "ground_truth",
)


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def validate_frame(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    errors: list[str] = []
    rows = read_rows(path)
    require(bool(rows), f"{path} has no rows", errors)
    if not rows:
        return rows, errors

    fieldnames = set(rows[0])
    require("custom_id" in fieldnames, f"{path} missing custom_id column", errors)
    require("prompt" in fieldnames, f"{path} missing prompt column", errors)
    leaked_columns = sorted(c for c in fieldnames if c.lower() in LEAK_TERMS)
    require(not leaked_columns, f"{path} has leaked oracle columns: {leaked_columns}", errors)

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
    return rows, errors


def validate_ground_truth(path: Path, frame_rows: list[dict[str, str]]) -> list[str]:
    errors: list[str] = []
    gt_rows = read_rows(path)
    gt_ids = {row.get("custom_id", "") for row in gt_rows}
    frame_ids = {row.get("custom_id", "") for row in frame_rows}
    require(frame_ids == gt_ids, f"{path} custom_id set does not match frame", errors)
    require("dist_to_goal" in set(gt_rows[0]) if gt_rows else False, f"{path} missing dist_to_goal", errors)
    return errors


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--frame", type=Path, default=DEFAULT_FRAME)
    ap.add_argument("--ground-truth", type=Path, default=DEFAULT_GT)
    args = ap.parse_args()

    frame_rows, errors = validate_frame(args.frame)
    if args.ground_truth.exists():
        errors.extend(validate_ground_truth(args.ground_truth, frame_rows))
    else:
        errors.append(f"missing ground truth file: {args.ground_truth}")

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        raise SystemExit(1)
    print(f"validated {args.frame} ({len(frame_rows)} rows), no oracle leakage found")


if __name__ == "__main__":
    main()

