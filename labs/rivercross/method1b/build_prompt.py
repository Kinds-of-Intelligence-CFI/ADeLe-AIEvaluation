"""Build a DIMENSION-AGNOSTIC ADeLe demand-annotation prompt.

The protocol text is general across dimensions: strict assignment by elimination
against whatever conditions the rubric itself states - no dimension-specific
gating in the prompt. Every dimension-specific notion (horizon, search size,
memory load, ...) comes from the inlined rubric only. Swap --code / --frame to
target another dimension or item set.

Usage:
    python build_prompt.py [--code PLp] [--name Planning] [--frame judge_frame_v2.csv]
"""
from pathlib import Path
import argparse
import csv

HERE = Path(__file__).resolve().parent
REPO = HERE
while REPO != REPO.parent and not (REPO / "src" / "adele").is_dir():
    REPO = REPO.parent
RUBRIC_ROOTS = [
    REPO / "src/adele/rubrics/data_v2/Paolo_Pablo",
    REPO / "src/adele/rubrics/data_v2/Marko",
    REPO / "rubrics",  # v1.0 canonical
]

PREAMBLE = """\
You are an ADeLe demand-level annotator. For each of the {n} tasks below, assign a \
single demand level (an integer 0-5) for ONE dimension: {code} - {name}. The level is \
a property of the TASK - how much of the {name} ability the task requires in order to \
be completed successfully - and is independent of how skilled any particular solver is.

Score using ONLY the rubric provided below. Assign levels by ELIMINATION against the \
rubric's stated conditions, NOT by an overall impression of how hard or tricky a task \
feels:
1. From the rubric, identify the specific factors that distinguish its levels.
2. For each task, read off the values of those factors from the task description.
3. Checking from the TOP level downward, a level may be assigned only when the task \
meets that level's defining conditions; assign the HIGHEST level whose conditions are \
all satisfied.
4. Surface cues the rubric does not tie to a higher level (trickiness, dense detail, \
length, number of objects) do NOT by themselves raise the level beyond what the \
rubric's conditions allow.
"""

# Default closing instruction (method 1b: demand-to-go). Override with --framing.
DEFAULT_FRAMING = (
    "Each task describes a situation already in progress; score the demand still required "
    "to COMPLETE it from that situation (the remaining {name} demand), not the demand of "
    "solving it from the very start."
)

OUTPUT_SPEC = """\
=== OUTPUT ===
Return ONLY a CSV inside a single code block. Header exactly:
custom_id,level,reason
then EXACTLY {n} data rows (one per task, in the given order); level = integer 0-5; \
reason <=15 words naming the rubric conditions that decided the level. Output nothing \
before or after the code block."""


def resolve_rubric(code: str) -> Path:
    for root in RUBRIC_ROOTS:
        cand = root / f"{code}.txt"
        if cand.exists():
            return cand
    raise FileNotFoundError(f"no rubric {code}.txt under {[str(r) for r in RUBRIC_ROOTS]}")


def derive_name(rubric_text: str, code: str) -> str:
    first = rubric_text.splitlines()[0].strip()
    return first[2:].strip() if first.startswith("# ") else code


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--code", default="PLp")
    ap.add_argument("--name", default=None)
    ap.add_argument("--frame", default="judge_frame_v2.csv")
    ap.add_argument("--framing", default=None,
                    help="closing instruction (method-specific); default = demand-to-go (1b)")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()

    rubric_path = resolve_rubric(a.code)
    rubric = rubric_path.read_text().strip()
    name = a.name or derive_name(rubric, a.code)
    frame = Path(a.frame) if Path(a.frame).exists() else HERE / a.frame
    with frame.open() as fh:
        rows = list(csv.DictReader(fh))
    n = len(rows)
    items = "\n".join(f"{r['custom_id']} ||| {r['prompt']}" for r in rows)
    framing = (a.framing or DEFAULT_FRAMING).format(name=name)

    text = (
        PREAMBLE.format(n=n, code=a.code, name=name)
        + "\n" + framing + "\n"
        + f"\n=== {a.code} RUBRIC ===\n"
        + rubric
        + f"\n\n=== {n} TASKS (custom_id ||| situation) ===\n"
        + items
        + "\n"
        + OUTPUT_SPEC.format(n=n)
        + "\n"
    )
    out = Path(a.out) if a.out else (frame.parent / f"prompt_{a.code}.txt")
    out.write_text(text)
    print(f"wrote {out} ({len(text)} chars, {n} tasks, dim={a.code}/{name}, rubric={rubric_path.relative_to(REPO)})")


if __name__ == "__main__":
    main()
