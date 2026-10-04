"""Build the shareable release of ProgramBench with demand labels: release/ (see ../release.py for the layout).

Labels (PLp, PLe, PLs, MSm, MSc on the 130 clean tasks): all from relabel-v2 (examples review of 2026-10-04, d4ec2ec;
runs relabel-v2 and relabel-v2-long), with PLp re-judged in relabel-v3 for cells at PLp 3-5 after the synthesis example
moved to Level 4 (d6cc9ca; runs relabel-v3-plp and relabel-v3-plp-long). The merge is one-sided: only cells at 3-5 were
re-judged (relabel-v3/RESULTS.md). The card's correlation is computed here from the released labels, with the study's
statistic (swebench-pl's `rho`) on the clean set. No task text (third-party documentation under many licences).

    python experiments/benchmarks/programbench-pl/export.py
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
    lab = release.release_labels(HERE, "programbench", DIMS)
    df = tasks[tasks["keep"]].join(release.wide(lab, DIMS))
    missing = {}
    for t, row in df.iterrows():
        miss = [d for d in DIMS if pd.isna(row[f"v2/{d}"])]
        if miss:
            missing[t] = "all rubrics" if len(miss) == len(DIMS) else ", ".join(miss)
    h = df.dropna(subset=["v2/PLp"])
    r = rho(h["v2/PLp"], h["solve_rate_0.9"], "negative")
    release.build(HERE, lab, DIMS,
                  {"{n_clean}": str(len(df)),
                   "{rho_plp}": f"{r['rho']:+.2f} (p = {r['p_two_sided']:.2g}, n = {r['n']})",
                   "{unlabelled}": "; ".join(f"`{t}` ({m})" for t, m in missing.items()) or "none"})


if __name__ == "__main__":
    main()
