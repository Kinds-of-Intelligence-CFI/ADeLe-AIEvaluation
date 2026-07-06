"""Build rivercross annotation prompts from a template, rubric, and frame."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


HERE = Path(__file__).resolve().parent
RIVERCROSS = HERE.parent
REPO = RIVERCROSS
while REPO != REPO.parent and not (REPO / "src" / "adele").is_dir():
    REPO = REPO.parent

RUBRIC_ROOTS = [
    REPO / "src/adele/rubrics/data_v2/Paolo_Pablo",
    REPO / "src/adele/rubrics/data_v2/Marko",
    REPO / "src/adele/rubrics/data_v1",
]


def resolve_rubric(code_or_path: str) -> Path:
    path = Path(code_or_path)
    if path.exists():
        return path
    for root in RUBRIC_ROOTS:
        candidate = root / f"{code_or_path}.txt"
        if candidate.exists():
            return candidate
    raise FileNotFoundError(f"could not resolve rubric {code_or_path!r}")


def resolve_template(name_or_path: str) -> Path:
    path = Path(name_or_path)
    if path.exists():
        return path
    candidate = HERE / "templates" / f"{name_or_path}.txt"
    if candidate.exists():
        return candidate
    raise FileNotFoundError(f"could not resolve template {name_or_path!r}")


def derive_name(rubric: str, code: str) -> str:
    first = rubric.splitlines()[0].strip()
    return first[2:].strip() if first.startswith("# ") else code


def render(template: str, values: dict[str, str]) -> str:
    out = template
    for key, value in values.items():
        out = out.replace("{{" + key + "}}", value)
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--rubric", required=True, help="rubric code, e.g. PLp, or path")
    ap.add_argument("--code", default=None, help="output dimension code; defaults to --rubric")
    ap.add_argument("--name", default=None, help="dimension name; defaults to rubric header")
    ap.add_argument("--template", default="demand_to_go_annotation")
    ap.add_argument("--frame", type=Path, default=RIVERCROSS / "frames" / "1b_state_visible.csv")
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args()

    rubric_path = resolve_rubric(args.rubric)
    rubric = "\n".join(
        line for line in rubric_path.read_text(encoding="utf-8").splitlines()
        if not line.lstrip().startswith("#!")
    ).strip()
    code = args.code or (args.rubric if "/" not in args.rubric else rubric_path.stem)
    name = args.name or derive_name(rubric, code)
    template = resolve_template(args.template).read_text(encoding="utf-8")

    with args.frame.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    items = "\n".join(f"{row['custom_id']} ||| {row['prompt']}" for row in rows)
    text = render(template, {
        "N": str(len(rows)),
        "CODE": code,
        "NAME": name,
        "RUBRIC": rubric,
        "ITEMS": items,
    })

    out = args.out or HERE / "generated" / f"prompt_{code}_1b_state_visible.txt"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8")
    print(
        f"wrote {out.relative_to(RIVERCROSS)} "
        f"({len(text)} chars, {len(rows)} tasks, rubric={rubric_path.relative_to(REPO)})"
    )


if __name__ == "__main__":
    main()

