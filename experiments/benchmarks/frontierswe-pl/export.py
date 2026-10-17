"""Build the shareable release of FrontierSWE v2 with demand labels: release/ (see ../release.py for the layout).

Labels (PLp, PLe, PLs, MSm, MSc on the 19 clean tasks): all from relabel-v2 (examples review of 2026-10-04, d4ec2ec),
with PLp re-judged in relabel-v3 for cells at PLp 3-5 after the synthesis example moved to Level 4 (d6cc9ca). The
merge is one-sided: only cells at 3-5 were re-judged (relabel-v3/RESULTS.md). The 15 dropped tasks have no current
labels; their PLp labels under an earlier text (amendment 1, run frontierswe-pl-dropped) are not released. The card's
PLp levels and correlation are computed here from the released labels, with the study's statistic (swebench-pl's
`rho`) on the clean set. No task text (the task repository has no licence).

    python experiments/benchmarks/frontierswe-pl/export.py
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
    lab = release.release_labels(HERE, "frontierswe-v2", DIMS)
    df = tasks[tasks["keep"]].join(release.wide(lab, DIMS))
    h = df.dropna(subset=["v2/PLp"])
    levels = h["v2/PLp"].astype(int).value_counts().sort_index()
    if h["v2/PLp"].nunique() > 1:
        r = rho(h["v2/PLp"], h["solve_rate_0.9"], "negative")
        rho_clean = f"ρ = {r['rho']:+.2f} (p = {r['p_two_sided']:.2g}, n = {r['n']})"
    else:
        rho_clean = "one level: not testable"
    release.build(HERE, lab, DIMS,
                  {"{n_clean}": str(len(df)), "{n_dropped}": str(int((~tasks["keep"]).sum())),
                   "{plp_levels}": ", ".join(f"Level {k} on {v} of {len(h)}" for k, v in levels.items()),
                   "{rho_clean}": rho_clean})


if __name__ == "__main__":
    main()
