"""Build the shareable release of ProgramBench with demand labels: release/ (see ../release.py for the layout).

Labels: PLp, PLe from runs programbench-pl and programbench-pl-long; PLs from runs pls-relabel and pls-relabel-long
(the PLs text of 2026-10-04); MSm, MSc from runs ms-benchmarks and ms-benchmarks-long (the 130 clean tasks). No task
text (third-party documentation under many licences).

    python experiments/benchmarks/programbench-pl/analysis/analyse.py      # results/analysis.json, quoted in the card
    python experiments/benchmarks/programbench-pl/export.py
"""

import importlib.util
import json
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
DIMS = ["PLp", "PLe", "PLs", "MSm", "MSc"]
_spec = importlib.util.spec_from_file_location("release", HERE.parent / "release.py")
release = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(release)


def main() -> None:
    res = json.loads((HERE / "results/analysis.json").read_text())
    r = res["spearman"]["clean"]["PLp_vs_solve_rate_0.9"]
    tasks = pd.read_csv(HERE / "tasks.csv", dtype={"instance_id": str})
    runs = {"programbench-pl": ("programbench-pl", ["PLp", "PLe"]),
            "programbench-pl-long": ("programbench-pl", ["PLp", "PLe"]),
            "pls-relabel": ("pls-relabel", ["PLs"]), "pls-relabel-long": ("pls-relabel", ["PLs"]),
            "ms-benchmarks": "ms-benchmarks", "ms-benchmarks-long": "ms-benchmarks"}
    lab, _ = release.labels("programbench", runs, DIMS)
    have = set(zip(lab["instance_id"], lab["rubric"]))
    missing = {}
    for t in tasks.loc[tasks["keep"].astype(bool), "instance_id"]:
        miss = [d for d in DIMS if (t, f"v2/{d}") not in have]
        if miss:
            missing[t] = "all rubrics" if len(miss) == len(DIMS) else ", ".join(miss)
    release.build(HERE, "programbench", runs, DIMS,
                  {"{n_clean}": str(int(tasks["keep"].sum())),
                   "{rho_plp}": f"{r['rho']:+.2f} (p = {r['p_two_sided']:.2g}, n = {r['n']})",
                   "{unlabelled}": "; ".join(f"`{t}` ({m})" for t, m in missing.items()) or "none"})


if __name__ == "__main__":
    main()
