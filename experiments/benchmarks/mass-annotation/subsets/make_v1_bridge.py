"""Gate 2 of the bulk (PLAN.md §3): freeze a stratified sample of the ADeLe v1.0 battery as benchmark
"adele-battery-v1", so our judge can be compared with the published GPT-4o labels on the v1 rubrics.

    ADELE_BATTERY_CSV=/path/to/ADeLe_batterry_v1dot0.csv \\
        python experiments/benchmarks/mass-annotation/subsets/make_v1_bridge.py

The battery is gated on Hugging Face (needs HF_TOKEN with access) and only an LFS pointer is in the repo, so it is read
from ADELE_BATTERY_CSV or downloaded with HF_TOKEN. Writes:
- data/instances/instances_adele-battery-v1.parquet (task texts; data/ is gitignored) and its INSTANCES.tsv entry;
- data/instances/v1_bridge_reference.csv (the published levels of the sampled items; stays in data/);
- subsets/v1_bridge.csv (benchmark, instance_id, source benchmark: ids only, committed).
"""

from pathlib import Path

import pandas as pd

from adele.data.battery import DEMAND_COLS, load_battery
from adele.instances import register

HERE = Path(__file__).resolve().parent
INSTANCES = HERE.parents[3] / "data" / "instances"
SLUG = "adele-battery-v1"
PER_SOURCE = 3   # 20 source benchmarks x 3 = 60 items (PLAN.md §3, gate 2)
SEED = 20261007


def sample(battery: pd.DataFrame, per_source: int = PER_SOURCE, seed: int = SEED) -> pd.DataFrame:
    """``per_source`` items from each source benchmark, drawn with a fixed seed; sorted by id."""
    picked = battery.groupby("benchmark").sample(n=per_source, random_state=seed)
    return picked.sort_values("custom_id").reset_index(drop=True)


def main() -> None:
    picked = sample(load_battery())
    frame = pd.DataFrame({"benchmark": SLUG, "instance_id": picked["custom_id"].astype(str),
                          "prompt": picked["prompt"].astype(str)})
    path = INSTANCES / f"instances_{SLUG}.parquet"
    frame.to_parquet(path, index=False)
    register(path, SLUG)
    ref = picked[["custom_id", "benchmark"] + [c for c in DEMAND_COLS if c in picked.columns]]
    ref.rename(columns={"custom_id": "instance_id", "benchmark": "source"}).to_csv(
        INSTANCES / "v1_bridge_reference.csv", index=False)
    pd.DataFrame({"benchmark": SLUG, "instance_id": frame["instance_id"], "source": picked["benchmark"]}).to_csv(
        HERE / "v1_bridge.csv", index=False)
    print(f"{len(frame)} items from {picked['benchmark'].nunique()} source benchmarks -> {path.name}")


if __name__ == "__main__":
    main()
