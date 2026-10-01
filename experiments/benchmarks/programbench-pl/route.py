"""Split the clean ProgramBench tasks between two judge runs by the size of their judge prompts (Pablo, option A).

The Claude Code judge reads its prompt with one Read call, which returns at most 2,000 lines and ~25,000 tokens.
Full documentation makes some prompts larger. A task goes to the chunked run (`programbench-pl-long`: same judge,
reading in parts of 200 lines, `chunk_lines` in its spec; the protocol check requires every line to come back) when any of its judge
prompts exceeds `MAX_CHARS` characters or `MAX_LINES` lines; all others go to `programbench-pl` (one Read).
Prompts are built exactly as the runner builds them (`adele.mass.pin.plan_cells` on the main spec with the whole
clean set as subset, no side effects).

Writes subset_single.csv and subset_chunked.csv (instance_id, keep) for the two specs, and prompt_sizes.csv.

    python experiments/benchmarks/programbench-pl/route.py
"""

import tempfile
from pathlib import Path

import pandas as pd

from adele.mass.pin import plan_cells
from adele.mass.spec import load_spec

HERE = Path(__file__).resolve().parent
SPEC = HERE.parent / "mass-annotation/specs/programbench-pl.toml"
MAX_CHARS, MAX_LINES = 50_000, 1_500


def main() -> None:
    text = SPEC.read_text().replace("programbench-pl/subset_single.csv", "programbench-pl/tasks.csv")
    with tempfile.NamedTemporaryFile("w", suffix=".toml") as f:
        f.write(text)
        f.flush()
        cells, prompts, _ = plan_cells(load_spec(Path(f.name)))
    rows = [{"instance_id": c["instance_id"], "chars": len(prompts[c["cell_id"]]),
             "lines": len(prompts[c["cell_id"]].split("\n")),
             "max_line": max(map(len, prompts[c["cell_id"]].split("\n")))} for c in cells]
    size = pd.DataFrame(rows).groupby("instance_id").max()
    size["route"] = ((size["chars"] > MAX_CHARS) | (size["lines"] > MAX_LINES)).map({True: "chunked", False: "single"})
    size.reset_index().to_csv(HERE / "prompt_sizes.csv", index=False)
    for route in ("single", "chunked"):
        pd.DataFrame({"instance_id": size.index, "keep": size["route"] == route}).to_csv(
            HERE / f"subset_{route}.csv", index=False)
    print(size["route"].value_counts().to_dict(), "| chunked:", sorted(size.index[size["route"] == "chunked"]))


if __name__ == "__main__":
    main()
