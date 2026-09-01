"""Build the v4 verbosity-control frame for the MMs contrast pilot.

Motivation: in the frozen v3 contrast set, object mentions in the history text
scale with object_location_updates, so a judge that merely counts history
verbosity is observationally similar to one that tracks state updates
(Spearman(delta, history_prompt_tokens) ~ 0.9). This control decouples the two.

Design:
- Take the 6 "low" history-only items (1 object-location update, no reversals)
  and rewrite each move line verbosely: every line also names the objects that
  did NOT move, without revealing which bank anything is on. The underlying
  trace, and hence every ground-truth memory feature, is unchanged; only the
  token/object-mention count grows to exceed the "high" items.
- The v4 annotation frame contains these 6 verbose-low items plus the 12
  unmodified v3 medium/high items as same-batch calibration anchors. The v3
  standard-low items are excluded so a judge cannot recognise the duplicated
  trace and copy its label.
- Decision rule (within one v4 run): verbose-low has the most prompt tokens of
  any group, so a token-counting judge must score it at or above "high"; a
  state-update-tracking judge must score it at "low" levels (~1), below
  "medium". State-visible views of all underlying states are identical to v3,
  so the frozen v3 state-visible labels are reused rather than re-collected.
"""

from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path


HERE = Path(__file__).resolve().parent
IN_HISTORY = HERE / "1b_memory_contrast_history_only.csv"
IN_PAIRS = HERE / "ground_truth" / "1b_memory_contrast_pairs.csv"
OUT_FRAME = HERE / "1b_memory_verbosity_history_only.csv"
OUT_PAIRS = HERE / "ground_truth" / "1b_memory_verbosity_pairs.csv"

MOVE_LINE_RE = re.compile(r"^(\d+)\. farmer (alone|with .+?) crossed to the (left|right) bank\.$")
INITIAL_RE = re.compile(r"Initial state: farmer, (.+?) start on the left bank")


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_rows(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)


def parse_items(prompt: str) -> list[str]:
    match = INITIAL_RE.search(prompt)
    if not match:
        raise ValueError("cannot find initial-state item list in prompt")
    return re.findall(r"item\d+", match.group(1))


def oxford(items: list[str], conjunction: str = "and") -> str:
    if len(items) == 1:
        return items[0]
    if len(items) == 2:
        return f"{items[0]} {conjunction} {items[1]}"
    return ", ".join(items[:-1]) + f", {conjunction} {items[-1]}"


def verbose_move_line(number: str, cargo: str, side: str, all_items: list[str]) -> str:
    if cargo == "alone":
        moved: list[str] = []
        head = f"{number}. farmer alone crossed to the {side} bank"
    else:
        moved = re.findall(r"item\d+", cargo)
        head = f"{number}. farmer together with {oxford(moved)} crossed over to the {side} bank"
    stayed = [item for item in all_items if item not in moved]
    if not stayed:
        return (
            f"{head}, and every one of the items was aboard the boat for this "
            f"crossing, so no item was left waiting on either bank."
        )
    tail = (
        f", while {oxford(stayed)} did not board the boat and did not change "
        f"banks during this crossing, each remaining exactly where it already was."
    )
    return head + tail


def verbose_prompt(prompt: str) -> str:
    all_items = parse_items(prompt)
    out_lines: list[str] = []
    for line in prompt.splitlines():
        match = MOVE_LINE_RE.match(line.strip())
        if match:
            number, cargo, side = match.groups()
            out_lines.append(verbose_move_line(number, cargo, side, all_items))
        else:
            out_lines.append(line)
    return "\n".join(out_lines)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out-frame", type=Path, default=OUT_FRAME)
    ap.add_argument("--out-pairs", type=Path, default=OUT_PAIRS)
    args = ap.parse_args()

    history = {row["custom_id"]: row["prompt"] for row in read_rows(IN_HISTORY)}
    pairs = read_rows(IN_PAIRS)
    pair_fields = list(pairs[0].keys())

    frame_rows: list[dict[str, str]] = []
    pair_rows: list[dict[str, str]] = []
    token_counts: dict[str, list[int]] = {"low": [], "medium": [], "high": [], "verbose-low": []}

    for pair in pairs:
        level = pair["contrast_level"]
        source_prompt = history[pair["custom_id_history_only"]]
        token_counts[level].append(len(source_prompt.split()))
        if level in ("medium", "high"):
            frame_rows.append(
                {"custom_id": pair["custom_id_history_only"], "prompt": source_prompt}
            )
        if level != "low":
            continue
        memv_pair_id = pair["pair_id"].replace("memc-", "memv-").replace("-low-", "-vlow-")
        memv_custom_id = f"{memv_pair_id}__history_only"
        rewritten = verbose_prompt(source_prompt)
        token_counts["verbose-low"].append(len(rewritten.split()))
        frame_rows.append({"custom_id": memv_custom_id, "prompt": rewritten})
        memv_pair = dict(pair)
        memv_pair.update(
            pair_id=memv_pair_id,
            underlying_state_id=pair["underlying_state_id"],
            contrast_level="verbose-low",
            custom_id_history_only=memv_custom_id,
        )
        pair_rows.append(memv_pair)

    frame_rows.sort(key=lambda row: row["custom_id"])
    write_rows(args.out_frame, frame_rows, ["custom_id", "prompt"])
    write_rows(args.out_pairs, pair_rows, pair_fields)

    print(f"wrote {args.out_frame.name} ({len(frame_rows)} rows)")
    print(f"wrote {args.out_pairs.name} ({len(pair_rows)} rows)")
    for level, counts in token_counts.items():
        if counts:
            print(
                f"history prompt tokens [{level}]: "
                f"min={min(counts)}, mean={sum(counts) / len(counts):.1f}, max={max(counts)}"
            )
    if max(token_counts["verbose-low"]) <= max(token_counts["high"]):
        raise SystemExit(
            "verbose-low prompts must exceed high prompts in token count; "
            "make the verbose template longer"
        )


if __name__ == "__main__":
    main()
