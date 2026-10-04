"""Build the shareable release of FrontierSWE v2 with demand labels: release/ (see ../release.py for the layout).

Labels: PLp, PLe from run frontierswe-pl (19 clean tasks); PLp from run frontierswe-pl-dropped (the 15 dropped tasks,
amendment 1); PLs from run pls-relabel (19 clean tasks; the PLs text of 2026-10-04); MSm, MSc from run ms-benchmarks
(19 clean tasks). No task text (the task repository has no licence).

    python experiments/benchmarks/frontierswe-pl/analysis/analyse.py      # results/analysis.json, quoted in the card
    python experiments/benchmarks/frontierswe-pl/analysis/dropped.py      # results/dropped.json, quoted in the card
    python experiments/benchmarks/frontierswe-pl/export.py
"""

import importlib.util
import json
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("release", HERE.parent / "release.py")
release = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(release)


def fmt(r: dict) -> str:
    return f"{r['rho']:+.2f} (p = {r['p_two_sided']:.2g}, n = {r['n']})"


def main() -> None:
    res = json.loads((HERE / "results/analysis.json").read_text())
    dropped = json.loads((HERE / "results/dropped.json").read_text())
    tasks = pd.read_csv(HERE / "tasks.csv")
    plp4 = sum(c for g in dropped["levels"].values() for lvl, c in g.items() if int(lvl) >= 4)
    release.build(HERE, "frontierswe-v2",
                  {"frontierswe-pl": ("frontierswe-pl", ["PLp", "PLe"]), "frontierswe-pl-dropped": "frontierswe-pl",
                   "pls-relabel": ("pls-relabel", ["PLs"]), "ms-benchmarks": "ms-benchmarks"},
                  ["PLp", "PLe", "PLs", "MSm", "MSc"],
                  {"{n_clean}": str(int(tasks["keep"].sum())), "{n_dropped}": str(int((~tasks["keep"]).sum())),
                   "{n_plp4}": str(plp4), "{rho_clean}": fmt(res["spearman"]["clean"]["PLp_vs_solve_rate_0.9"]),
                   "{rho_all}": fmt(dropped["PLp_vs_mean_reward_all"])})


if __name__ == "__main__":
    main()
