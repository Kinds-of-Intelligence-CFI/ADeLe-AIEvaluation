"""Build the shareable release of the Terminal-Bench Science 0.1 PL labels: release/ (a Hugging Face dataset layout).

  release/README.md        the data card (Hugging Face front matter + documentation), written by this script
  release/tasks.csv        all 70 tasks: domain, field, expert hours, trials, solve rate, flags, open issue numbers
  release/open_issues.csv  the open [TASK FIX] issues the open_issue flag rests on, with the fetch date
  release/labels.csv       one row per (task, rubric): level and full provenance
  release/labels_wide.csv  one row per task: outcomes and flags, one column per rubric
  release/rubrics.csv      every rubric used: code, generation, name, file, sha256
  release/MANIFEST.tsv     sha256 of every file above

Inputs are committed files only (tasks.csv, open_issues.csv, the mass run tbsci-pl, results/analysis.json). Only
answers written by claude-opus-5-5 are exported; a task without one is listed as unlabelled in the card. No task text
(Terminal-Bench Science tasks carry a no-training canary).

    python experiments/benchmarks/tbsci-pl/analysis/analyse.py      # results/analysis.json, quoted in the card
    python experiments/benchmarks/tbsci-pl/export.py
"""

import hashlib
import json
import shutil
import subprocess
from pathlib import Path

import pandas as pd

from adele.agentic import load_active_catalog

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = HERE / "release"
MODEL = "claude-opus-5-5"
DIMS = ["PLp", "PLe", "PLs"]
RUN = HERE.parent / "mass-annotation/runs/tbsci-pl"


def sha256(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def git(*args: str) -> str:
    return subprocess.run(["git", "-C", str(ROOT), *args], capture_output=True, text=True, check=True).stdout.strip()


def main() -> None:
    OUT.mkdir(exist_ok=True)
    tasks = pd.read_csv(HERE / "tasks.csv").set_index("instance_id")
    cat = load_active_catalog()

    lab = pd.read_csv(RUN / "labels.csv", dtype={"instance_id": str})
    lab = lab[lab["valid"].astype(bool) & lab["writer_model"].astype(str).str.startswith(MODEL)
              & lab["rubric_ref"].isin([f"v2/{d}" for d in DIMS])]
    builder = json.loads((RUN / "manifest.json").read_text())["frozen"]["prompt"]["function"]
    labels = pd.DataFrame({"instance_id": lab["instance_id"], "rubric": lab["rubric_ref"],
                           "level": lab["level"].astype(int), "judge_model": lab["writer_model"],
                           "judge_effort": lab["effort"],
                           "judge_harness": lab["backend"].replace({"subagent": "claude-code-subagent"}),
                           "prompt_builder": builder, "prompt_sha256": lab["prompt_sha256"],
                           "response_sha256": lab["response_sha256"], "study": "tbsci-pl", "run": lab["run"]})
    labels = labels.sort_values(["instance_id", "rubric"])
    labels.to_csv(OUT / "labels.csv", index=False)
    wide = tasks.join(labels.pivot(index="instance_id", columns="rubric", values="level"))
    wide.reset_index().to_csv(OUT / "labels_wide.csv", index=False)
    tasks.reset_index().to_csv(OUT / "tasks.csv", index=False)
    shutil.copyfile(HERE / "open_issues.csv", OUT / "open_issues.csv")
    pd.DataFrame([{"rubric": f"v2/{d}", "code": d, "generation": "v2", "name": cat[d].full_name,
                   "file": str(Path(cat[d].file_path).relative_to(ROOT)),
                   "sha256": sha256(Path(cat[d].file_path).read_bytes())} for d in DIMS]).to_csv(
        OUT / "rubrics.csv", index=False)

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
    for k in ("all", "solved_any_no_open_issue"):
        for y in ("solve_rate", "expert_hours"):
            r = res["spearman"][k][f"PLp_vs_{y}"]
            fill[f"{{rho_{k}_{y}}}"] = f"{r['rho']:+.2f} (p = {r['p_two_sided']:.2g})" if "rho" in r else "not testable"
    card = (HERE / "DATACARD.md").read_text(encoding="utf-8")
    for k, v in fill.items():
        card = card.replace(k, v)
    (OUT / "README.md").write_text(card, encoding="utf-8")
    files = ["README.md", "tasks.csv", "open_issues.csv", "labels.csv", "labels_wide.csv", "rubrics.csv"]
    (OUT / "MANIFEST.tsv").write_text("file\tsha256\n" + "".join(
        f"{f}\t{sha256((OUT / f).read_bytes())}\n" for f in files))
    print(f"release/: {len(tasks)} tasks, {len(labels)} labels, unlabelled: {unlabelled or 'none'}")


if __name__ == "__main__":
    main()
