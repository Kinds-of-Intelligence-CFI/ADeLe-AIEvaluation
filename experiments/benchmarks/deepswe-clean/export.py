"""Build the shareable release of DeepSWE v1.1 with demand labels: release/ (see ../release.py for the layout).

Labels (PLp, PLe, PLs, MSm, MSc on the 90 clean tasks): all from relabel-v2 (examples review of 2026-10-04, d4ec2ec),
with PLp re-judged in relabel-v3 for cells at PLp 3-5 after the synthesis example moved to Level 4 (d6cc9ca). The
merge is one-sided: only cells at 3-5 were re-judged (relabel-v3/RESULTS.md). The card's correlations are computed
here from the released labels, with the study's statistic (swebench-pl's `rho`) on the clean set. No task text (the
DeepSWE site carries a no-training canary); no trial data (no terms, deep-swe #94).

    python experiments/benchmarks/deepswe-clean/export.py
"""

import importlib.util
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
DIMS = ["PLp", "PLe", "PLs", "MSm", "MSc"]


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


release = load("release", HERE.parent / "release.py")
rho = load("swepl_analyse", HERE.parent / "swebench-pl/analysis/analyse.py").rho


def main() -> None:
    tasks = pd.read_csv(HERE / "tasks.csv", dtype={"instance_id": str}).set_index("instance_id")
    lab = release.release_labels(HERE, "deepswe-v1.1", DIMS)
    df = tasks[tasks["keep"]].join(release.wide(lab, DIMS))
    fill = {"{n_clean}": str(len(df))}
    for d in ("PLp", "PLe", "PLs"):
        h = df.dropna(subset=[f"v2/{d}"])
        r = rho(h[f"v2/{d}"], h["solve_rate"], "negative")
        fill[f"{{rho_{d.lower()}}}"] = f"{r['rho']:+.2f} (p = {r['p_two_sided']:.2g}, n = {r['n']})"
    release.build(HERE, lab, DIMS, fill)


if __name__ == "__main__":
    main()
