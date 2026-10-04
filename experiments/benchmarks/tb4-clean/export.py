"""Build the shareable release of the Terminal-Bench 4.0.0 clean set (release/, Hugging Face layout) and a short
descriptive summary (results/clean.json).

Labels (PLp, PLe, PLs; ../release.py `current_labels`): all from relabel-v2 (examples review of 2026-10-04, d4ec2ec),
with PLp re-judged in relabel-v3 for cells at PLp 3-5 after the synthesis example moved to Level 4 (d6cc9ca). The
merge is one-sided: only cells at 3-5 were re-judged (relabel-v3/RESULTS.md). All are Opus 5.5 at effort low with the
v2 prompt. Only answers written by claude-opus-5-5 are exported; a clean task without such an answer is listed as
unlabelled. No task text (Terminal-Bench tasks carry a no-training canary).

The summary is descriptive, not a pre-registered test: earlier labels and these outcomes were already analysed on the
full benchmark in tau2-tb4-pl and pl-relabel-v2.

    uv run --extra annotate --with scipy python experiments/benchmarks/tb4-clean/export.py
"""

import hashlib
import importlib.util
import json
import subprocess
from pathlib import Path

import pandas as pd
from scipy.stats import spearmanr

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BENCH = HERE.parent
OUT = HERE / "release"
DIMS = ["PLp", "PLe", "PLs"]
_spec = importlib.util.spec_from_file_location("release", BENCH / "release.py")
release = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(release)


def sha256(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def git(*args: str) -> str:
    return subprocess.run(["git", "-C", str(ROOT), *args], capture_output=True, text=True, check=True).stdout.strip()


def main() -> None:
    OUT.mkdir(exist_ok=True)
    tasks = pd.read_csv(HERE / "tasks.csv")
    keep = tasks[tasks["keep"]].set_index("instance_id")
    labels = release.release_labels(HERE, "terminal-bench-4.0.0", DIMS)
    labels.to_csv(OUT / "labels.csv", index=False)
    wide = keep[["category", "expert_hours", "n_configs", "n_trials", "solved_trials", "solve_rate"]].join(
        release.wide(labels, DIMS))
    wide.reset_index().to_csv(OUT / "labels_wide.csv", index=False)
    tasks.to_csv(OUT / "tasks.csv", index=False)
    release.rubrics(labels, DIMS).to_csv(OUT / "rubrics.csv", index=False)

    have = set(zip(labels["instance_id"], labels["rubric"]))
    unlabelled = [f"{t} ({d})" for t in keep.index for d in DIMS if (t, f"v2/{d}") not in have]
    full = wide.dropna(subset=[f"v2/{d}" for d in DIMS])
    summary = {"n_clean": int(len(keep)), "n_fully_labelled": int(len(full)), "unlabelled": unlabelled,
               "levels": {d: {int(k): int(v) for k, v in full[f"v2/{d}"].value_counts().sort_index().items()}
                          for d in DIMS}, "spearman": {}}
    for d in DIMS:
        for y in ("solve_rate", "expert_hours"):
            r, p = spearmanr(full[f"v2/{d}"], full[y])
            summary["spearman"][f"{d}_vs_{y}"] = {"rho": round(float(r), 3), "p": float(f"{p:.3g}"), "n": int(len(full))}
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results/clean.json").write_text(json.dumps(summary, indent=2) + "\n")

    card = (HERE / "DATACARD.md").read_text(encoding="utf-8")
    fill = {"{n_kept}": str(len(keep)), "{n_full}": str(len(full)), "{n_labels}": str(len(labels)),
            "{commit}": git("rev-parse", "--short", "HEAD"),
            "{unlabelled}": ", ".join(f"`{u}`" for u in unlabelled) or "none",
            "{rho_solve}": f"{summary['spearman']['PLp_vs_solve_rate']['rho']:+.2f}",
            "{p_solve}": f"{summary['spearman']['PLp_vs_solve_rate']['p']:.2g}",
            "{rho_hours}": f"{summary['spearman']['PLp_vs_expert_hours']['rho']:+.2f}",
            "{p_hours}": f"{summary['spearman']['PLp_vs_expert_hours']['p']:.2g}"}
    for k, v in fill.items():
        card = card.replace(k, v)
    assert "{" not in card.split("---", 2)[2], "unfilled placeholder in DATACARD.md"
    (OUT / "README.md").write_text(card, encoding="utf-8")
    files = ["README.md", "tasks.csv", "labels.csv", "labels_wide.csv", "rubrics.csv"]
    (OUT / "MANIFEST.tsv").write_text("file\tsha256\n" + "".join(
        f"{f}\t{sha256((OUT / f).read_bytes())}\n" for f in files))
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
