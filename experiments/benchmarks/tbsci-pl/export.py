"""Build the shareable release of the Terminal-Bench Science 0.1 PL labels: release/ (a Hugging Face dataset layout).

  release/README.md        the data card (Hugging Face front matter + documentation), written by this script
  release/tasks.csv        all 70 tasks: domain, field, expert hours, trials, solve rate, flags, open issue numbers
  release/open_issues.csv  the open [TASK FIX] issues the open_issue flag rests on, with the fetch date
  release/labels.csv       one row per (task, rubric): level and full provenance
  release/labels_wide.csv  one row per task: outcomes and flags, one column per rubric
  release/rubrics.csv      one row per rubric text used: code, generation, name, file, sha256, and the runs that used it
  release/MANIFEST.tsv     sha256 of every file above

Labels (PLp, PLe, PLs; ../release.py `current_labels`): all from relabel-v2 (examples review of 2026-10-04, d4ec2ec),
with PLp re-judged in relabel-v3 for cells at PLp 3-5 after the synthesis example moved to Level 4 (d6cc9ca). The
merge is one-sided: only cells at 3-5 were re-judged (relabel-v3/RESULTS.md). Inputs are committed files only
(tasks.csv, open_issues.csv, the labels.csv and manifest.json of those mass runs, results/analysis.json for task
counts). Only answers written by claude-opus-5-5 are exported; a task without one is listed as unlabelled in the card.
The card's correlations are computed here from the released labels, as in analysis/analyse.py (swebench-pl's `rho`).
No task text (Terminal-Bench Science tasks carry a no-training canary).

    python experiments/benchmarks/tbsci-pl/analysis/analyse.py      # results/analysis.json (task counts)
    python experiments/benchmarks/tbsci-pl/export.py
"""

import hashlib
import importlib.util
import json
import shutil
import subprocess
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = HERE / "release"
DIMS = ["PLp", "PLe", "PLs"]
OUTCOMES = {"solve_rate": "negative", "expert_hours": "positive"}


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


release = load("release", HERE.parent / "release.py")
rho = load("swepl_analyse", HERE.parent / "swebench-pl/analysis/analyse.py").rho


def sha256(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def git(*args: str) -> str:
    return subprocess.run(["git", "-C", str(ROOT), *args], capture_output=True, text=True, check=True).stdout.strip()


def main() -> None:
    OUT.mkdir(exist_ok=True)
    tasks = pd.read_csv(HERE / "tasks.csv").set_index("instance_id")
    labels = release.release_labels(HERE, "terminal-bench-science-0.1", DIMS)
    labels.to_csv(OUT / "labels.csv", index=False)
    wide = tasks.join(release.wide(labels, DIMS))
    wide.reset_index().to_csv(OUT / "labels_wide.csv", index=False)
    tasks.reset_index().to_csv(OUT / "tasks.csv", index=False)
    shutil.copyfile(HERE / "open_issues.csv", OUT / "open_issues.csv")
    release.rubrics(labels, DIMS).to_csv(OUT / "rubrics.csv", index=False)

    res = json.loads((HERE / "results/analysis.json").read_text())
    have = set(zip(labels["instance_id"], labels["rubric"]))
    unlabelled = [f"{t} ({d})" for t in tasks.index for d in DIMS if (t, f"v2/{d}") not in have]
    issues = pd.read_csv(HERE / "open_issues.csv")
    fill = {"{n_tasks}": str(len(tasks)), "{n_labels}": str(len(labels)),
            "{commit}": git("rev-parse", "--short", "HEAD"),
            "{unlabelled}": ", ".join(f"`{u}`" for u in unlabelled) or "none",
            "{n_solved_any}": str(res["n"]["solved_any"]), "{n_clean}": str(res["n"]["solved_any_no_open_issue"]),
            "{n_open_issue}": str(int(tasks["open_issue"].sum())), "{n_never}": str(int((~tasks["solved_any"]).sum())),
            "{issues_date}": str(issues["fetched_on"].iloc[0])}
    sets = {"all": wide, "solved_any_no_open_issue": wide[wide["solved_any"] & ~wide["open_issue"]]}
    for k, g in sets.items():
        for y, direction in OUTCOMES.items():
            h = g.dropna(subset=["v2/PLp", y])
            ok = h["v2/PLp"].nunique() > 1 and h[y].nunique() > 1
            r = rho(h["v2/PLp"], h[y], direction) if ok else None
            fill[f"{{rho_{k}_{y}}}"] = f"{r['rho']:+.2f} (p = {r['p_two_sided']:.2g})" if r else "not testable"
    card = (HERE / "DATACARD.md").read_text(encoding="utf-8")
    for k, v in fill.items():
        card = card.replace(k, v)
    assert "{" not in card.split("---", 2)[2], "unfilled placeholder in DATACARD.md"
    (OUT / "README.md").write_text(card, encoding="utf-8")
    files = ["README.md", "tasks.csv", "open_issues.csv", "labels.csv", "labels_wide.csv", "rubrics.csv"]
    (OUT / "MANIFEST.tsv").write_text("file\tsha256\n" + "".join(
        f"{f}\t{sha256((OUT / f).read_bytes())}\n" for f in files))
    print(f"release/: {len(tasks)} tasks, {len(labels)} labels, unlabelled: {unlabelled or 'none'}")


if __name__ == "__main__":
    main()
