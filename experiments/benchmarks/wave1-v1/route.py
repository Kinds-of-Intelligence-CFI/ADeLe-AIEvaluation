"""Split the wave-1 tasks (mass-annotation/subsets/wave1.csv) of each input group between the single-read and
chunked-read runs, by the programbench-pl rule: a task is long when any of its 17 v1 judge prompts exceeds 50,000 chars
or 1,500 lines. Also lists tasks with a prompt line over 2,000 chars (the Read tool cuts such lines).
Writes subset_<group>.csv, subset_<group>_long.csv and prompt_sizes.csv (ids and sizes only, no task text).

    uv run python experiments/benchmarks/wave1-v1/route.py
"""

import tempfile
import tomllib
from pathlib import Path

import pandas as pd

from adele.mass.pin import plan_cells
from adele.mass.spec import load_spec

HERE = Path(__file__).resolve().parent
BENCH = HERE.parent
SPECS = BENCH / "mass-annotation/specs"
WAVE1 = BENCH / "mass-annotation/subsets/wave1.csv"
GROUPS = ["swe", "tau2", "code", "other"]
MAX_CHARS, MAX_LINES, MAX_LINE = 50_000, 1_500, 2_000


def sizes(group: str, wave1: pd.DataFrame) -> pd.DataFrame:
    spec_path = SPECS / f"w1v1-{group}.toml"
    tasks = wave1[wave1["benchmark"].isin(tomllib.loads(spec_path.read_text())["tasks"]["benchmarks"])]
    with tempfile.TemporaryDirectory() as tmp:
        sub = Path(tmp) / "all.csv"
        tasks.to_csv(sub, index=False)
        spec = Path(tmp) / "spec.toml"
        spec.write_text(spec_path.read_text().replace(f"experiments/benchmarks/wave1-v1/subset_{group}.csv", str(sub)))
        cells, prompts, _ = plan_cells(load_spec(spec))
    rows = [{"benchmark": c["benchmark"], "instance_id": c["instance_id"], "chars": len(p := prompts[c["cell_id"]]),
             "lines": len(p.split("\n")), "max_line": max(map(len, p.split("\n")))} for c in cells]
    size = pd.DataFrame(rows).groupby(["benchmark", "instance_id"]).max().reset_index()
    assert len(size) == len(tasks), f"{group}: {len(size)} tasks planned, {len(tasks)} in wave 1"
    size["long"] = (size["chars"] > MAX_CHARS) | (size["lines"] > MAX_LINES)
    size.insert(0, "group", group)
    return size


def main() -> None:
    wave1 = pd.read_csv(WAVE1)
    size = pd.concat([sizes(g, wave1) for g in GROUPS])
    assert len(size) == len(wave1), f"{len(size)} tasks routed, {len(wave1)} in wave 1"
    size.to_csv(HERE / "prompt_sizes.csv", index=False)
    for g, part in size.groupby("group"):
        part[~part["long"]][["benchmark", "instance_id"]].to_csv(HERE / f"subset_{g}.csv", index=False)
        if part["long"].any():
            part[part["long"]][["benchmark", "instance_id"]].to_csv(HERE / f"subset_{g}_long.csv", index=False)
    print(size.groupby(["group", "long"]).size().to_string())
    wide = size[size["max_line"] > MAX_LINE]
    print(f"tasks with a line over {MAX_LINE:,} chars:", len(wide))
    print(wide[["benchmark", "instance_id", "max_line", "long"]].to_string(index=False))


if __name__ == "__main__":
    main()
