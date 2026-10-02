"""Build the shareable release of DeepSWE v1.1 with demand labels: release/ (see ../release.py for the layout).

Labels: PLp, PLe, PLs from run deepswe-clean; MSm, MSc from run ms-benchmarks (both on the 90 clean tasks). No task
text (the DeepSWE site carries a no-training canary); no trial data (no terms, deep-swe #94).

    python experiments/benchmarks/deepswe-clean/analysis/analyse.py      # results/analysis.json, quoted in the card
    python experiments/benchmarks/deepswe-clean/export.py
"""

import importlib.util
import json
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("release", HERE.parent / "release.py")
release = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(release)


def main() -> None:
    res = json.loads((HERE / "results/analysis.json").read_text())
    r = res["spearman"]["clean"]["PLp_vs_solve_rate"]
    tasks = pd.read_csv(HERE / "tasks.csv")
    release.build(HERE, "deepswe-v1.1", {"deepswe-clean": "deepswe-clean", "ms-benchmarks": "ms-benchmarks"},
                  ["PLp", "PLe", "PLs", "MSm", "MSc"],
                  {"{n_clean}": str(int(tasks["keep"].sum())),
                   "{rho_plp}": f"{r['rho']:+.2f} (p = {r['p_two_sided']:.2g}, n = {r['n']})"})


if __name__ == "__main__":
    main()
