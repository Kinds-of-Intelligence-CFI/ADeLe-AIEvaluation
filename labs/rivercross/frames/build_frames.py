"""Build standardized rivercross annotation frames for method 1b.

This is a refactor-only wrapper around the existing PLp state-visible frame. It
copies annotator-visible prompts into `frames/` and keeps solver cost-to-go in a
separate `frames/ground_truth/` file so oracle data cannot leak into prompts.
"""

from __future__ import annotations

import csv
from pathlib import Path


HERE = Path(__file__).resolve().parent
RIVERCROSS = HERE.parent
LEGACY_1B = RIVERCROSS / "method1b"
OUT_FRAME = HERE / "1b_state_visible.csv"
OUT_GT = HERE / "ground_truth" / "1b_state_visible_cost_to_go.csv"


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_rows(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)


def main() -> None:
    frame_rows = read_rows(LEGACY_1B / "judge_frame_v2.csv")
    frame_ids = {row["custom_id"] for row in frame_rows}
    gt_rows = [
        row
        for row in read_rows(LEGACY_1B / "ground_truth.csv")
        if row["custom_id"] in frame_ids
    ]

    missing_gt = frame_ids - {row["custom_id"] for row in gt_rows}
    if missing_gt:
        raise SystemExit(f"missing ground truth for {len(missing_gt)} frame ids")

    write_rows(OUT_FRAME, frame_rows, ["custom_id", "prompt"])
    write_rows(OUT_GT, gt_rows, ["custom_id", "instance", "dist_to_goal"])
    print(f"wrote {OUT_FRAME.relative_to(RIVERCROSS)} ({len(frame_rows)} rows)")
    print(f"wrote {OUT_GT.relative_to(RIVERCROSS)} ({len(gt_rows)} rows)")


if __name__ == "__main__":
    main()

