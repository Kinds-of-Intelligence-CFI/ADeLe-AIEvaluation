"""The task sets of ms-benchmarks: the clean sets the PL studies labelled, as `adele mass` subsets.

  subset.csv        benchmark, instance_id, keep: every set below except ProgramBench's 13 long tasks
  subset_long.csv   the 13 ProgramBench tasks whose prompts need the chunked-read judge (programbench-pl/route.py)

Sets (each study's own `keep`, or all tasks where the study has no exclusions):
  swe-bench-verified           swebench-clean (443)
  tau2-airline/retail/banking  tau2-clean (242)
  terminal-bench-4.0.0         tb4-clean (35)
  terminal-bench-science-0.1   tbsci-pl (all 70)
  deepswe-v1.1                 deepswe-clean (90)
  frontierswe-v2               frontierswe-pl (19)
  programbench                 programbench-pl (130: 117 single-read + 13 long)
  rivercross-search            rivercross-v2 amendment 2 grid (54)

    python experiments/benchmarks/ms-benchmarks/make_subset.py
"""

from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
BENCH = HERE.parent
SINGLE = {"swe-bench-verified": "swebench-clean", "terminal-bench-4.0.0": "tb4-clean",
          "terminal-bench-science-0.1": "tbsci-pl", "deepswe-v1.1": "deepswe-clean",
          "frontierswe-v2": "frontierswe-pl"}


def kept(path: Path) -> pd.Series:
    t = pd.read_csv(path, dtype={"instance_id": str})
    return t.loc[t["keep"].astype(bool), "instance_id"] if "keep" in t else t["instance_id"]


def main() -> None:
    parts = [pd.DataFrame({"benchmark": b, "instance_id": kept(BENCH / s / "tasks.csv")}) for b, s in SINGLE.items()]
    tau2 = pd.read_csv(BENCH / "tau2-clean/tasks.csv", dtype={"instance_id": str})
    parts.append(tau2.loc[tau2["keep"].astype(bool), ["benchmark", "instance_id"]])
    parts.append(pd.DataFrame({"benchmark": "programbench",
                               "instance_id": kept(BENCH / "programbench-pl/subset_single.csv")}))
    parts.append(pd.DataFrame({"benchmark": "rivercross-search",
                               "instance_id": pd.read_csv(BENCH / "rivercross-v2/frames/search_frame.csv")["custom_id"]}))
    single = pd.concat(parts, ignore_index=True).assign(keep=True)
    assert not single.duplicated(["benchmark", "instance_id"]).any()
    single.to_csv(HERE / "subset.csv", index=False)
    long = pd.DataFrame({"benchmark": "programbench", "instance_id": kept(BENCH / "programbench-pl/subset_chunked.csv"),
                         "keep": True})
    long.to_csv(HERE / "subset_long.csv", index=False)
    print(single["benchmark"].value_counts().to_dict(), f"| long: {len(long)}",
          f"| total tasks {len(single) + len(long)}")


if __name__ == "__main__":
    main()
