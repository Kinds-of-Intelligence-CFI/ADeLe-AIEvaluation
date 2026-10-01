"""Build the shareable release of the Terminal-Bench 4.0.0 clean set (release/, Hugging Face layout) and a short
descriptive summary (results/clean.json).

The PL labels already exist: PLp (text O) from plp-o-relabel run o-tb4, PLe and PLs from pl-relabel-v2 run v2-tb4.
All are Opus 5.5 at effort low with the v2 prompt. Only answers written by claude-opus-5-5 are exported; a clean task
without such an answer is listed as unlabelled. No task text (Terminal-Bench tasks carry a no-training canary).

The summary is descriptive, not a pre-registered test: these labels and outcomes were already analysed on the full
benchmark in tau2-tb4-pl and pl-relabel-v2.

    uv run --extra annotate --with scipy python experiments/benchmarks/tb4-clean/export.py
"""

import hashlib
import json
import subprocess
from pathlib import Path

import pandas as pd
from scipy.stats import spearmanr

from adele.agentic import load_active_catalog

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BENCH = HERE.parent
OUT = HERE / "release"
MODEL = "claude-opus-5-5"
SOURCES = [("PLp", "plp-o-relabel/labels/o-tb4", "plp-o-relabel"),
           ("PLe", "pl-relabel-v2/labels/v2-tb4", "pl-relabel-v2"),
           ("PLs", "pl-relabel-v2/labels/v2-tb4", "pl-relabel-v2")]
DIMS = ["PLp", "PLe", "PLs"]


def sha256(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def git(*args: str) -> str:
    return subprocess.run(["git", "-C", str(ROOT), *args], capture_output=True, text=True, check=True).stdout.strip()


def main() -> None:
    OUT.mkdir(exist_ok=True)
    tasks = pd.read_csv(HERE / "tasks.csv")
    keep = tasks[tasks["keep"]].set_index("instance_id")
    cat = load_active_catalog()

    rows = []
    for dim, run, study in SOURCES:
        lab = pd.read_csv(BENCH / run / "labels_long.csv", dtype={"instance_id": str})
        lab = lab[(lab["demand"] == dim) & lab["valid"] & lab["writer_model"].astype(str).str.startswith(MODEL)]
        for r in lab[lab["instance_id"].isin(keep.index)].itertuples(index=False):
            rows.append({"instance_id": r.instance_id, "rubric": f"v2/{dim}", "level": int(r.level),
                         "judge_model": r.writer_model, "judge_effort": "low", "judge_harness": "claude-code-subagent",
                         "prompt_builder": "adele.annotation.prompts.build_annotation_prompt_v2",
                         "prompt_sha256": r.prompt_sha256, "response_sha256": r.response_sha256,
                         "study": study, "run": Path(run).name})
    labels = pd.DataFrame(rows).sort_values(["instance_id", "rubric"])
    labels.to_csv(OUT / "labels.csv", index=False)
    wide = keep[["category", "expert_hours", "n_configs", "n_trials", "solved_trials", "solve_rate"]].join(
        labels.pivot(index="instance_id", columns="rubric", values="level"))
    wide.reset_index().to_csv(OUT / "labels_wide.csv", index=False)
    tasks.to_csv(OUT / "tasks.csv", index=False)
    pd.DataFrame([{"rubric": f"v2/{d}", "code": d, "generation": "v2", "name": cat[d].full_name,
                   "file": str(Path(cat[d].file_path).relative_to(ROOT)),
                   "sha256": sha256(Path(cat[d].file_path).read_bytes())} for d in DIMS]).to_csv(
        OUT / "rubrics.csv", index=False)

    unlabelled = sorted(set(keep.index) - set(labels["instance_id"]))
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
            "{rho_solve}": f"{summary['spearman']['PLp_vs_solve_rate']['rho']:+.2f}",
            "{p_solve}": f"{summary['spearman']['PLp_vs_solve_rate']['p']:.2g}",
            "{rho_hours}": f"{summary['spearman']['PLp_vs_expert_hours']['rho']:+.2f}",
            "{p_hours}": f"{summary['spearman']['PLp_vs_expert_hours']['p']:.2g}"}
    for k, v in fill.items():
        card = card.replace(k, v)
    (OUT / "README.md").write_text(card, encoding="utf-8")
    files = ["README.md", "tasks.csv", "labels.csv", "labels_wide.csv", "rubrics.csv"]
    (OUT / "MANIFEST.tsv").write_text("file\tsha256\n" + "".join(
        f"{f}\t{sha256((OUT / f).read_bytes())}\n" for f in files))
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
