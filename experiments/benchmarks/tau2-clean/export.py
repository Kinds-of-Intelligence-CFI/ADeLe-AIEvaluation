"""Build the shareable release of the tau2 clean set: release/ (a Hugging Face dataset layout).

  release/README.md        the data card (Hugging Face front matter + documentation), written by this script
  release/tasks.csv        all 257 non-telecom tau2 tasks with frozen-text results: solve rates, exclusion reason, keep
  release/labels.csv       one row per (clean task, rubric): level and full provenance
  release/labels_wide.csv  one row per clean task: solve rates, text hash, one column per rubric
  release/rubrics.csv      every rubric used: code, generation, name, file, sha256
  release/MANIFEST.tsv     sha256 of every file above

Inputs are committed study files only (tasks.csv, the labels_long.csv of each PLp and PLe source run, the labels.csv of
mass run tau2-clean-new-pl for PLp and PLe, the labels.csv and manifest.json of mass run pls-relabel, which gives every
PLs label with the PLs text of 2026-10-04, results/clean.json), so the release can be rebuilt at any commit. Only
answers written by claude-opus-5-5 are exported. No task text. Tasks are keyed by (benchmark, instance_id): tau2 ids
repeat across domains.

    python experiments/benchmarks/tau2-clean/analysis/analyse.py      # results/clean.json, quoted in the card
    python experiments/benchmarks/tau2-clean/export.py
"""

import hashlib
import json
import subprocess
from pathlib import Path

import pandas as pd

from adele.agentic import load_active_catalog

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BENCH = HERE.parent
OUT = HERE / "release"
MODEL = "claude-opus-5-5"
DIMS = ["PLp", "PLe", "PLs"]
KEY = ["benchmark", "instance_id"]
# (rubric, run folder, study). Order matters: the first source with a label wins.
SOURCES = [("PLp", "plp-o-relabel/labels/o-tau2", "plp-o-relabel"),
           ("PLe", "pl-relabel-v2/labels/v2-tau2", "pl-relabel-v2")]
MASS_RUN = BENCH / "mass-annotation/runs/tau2-clean-new-pl"  # PLp and PLe of the new banking tasks
PLS_RUN = BENCH / "mass-annotation/runs/pls-relabel"  # every PLs label


def sha256(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def git(*args: str) -> str:
    return subprocess.run(["git", "-C", str(ROOT), *args], capture_output=True, text=True, check=True).stdout.strip()


def ok(df: pd.DataFrame) -> pd.DataFrame:
    return df[df["valid"].astype(bool) & df["writer_model"].astype(str).str.startswith(MODEL)]


def main() -> None:
    OUT.mkdir(exist_ok=True)
    tasks = pd.read_csv(HERE / "tasks.csv", dtype={"instance_id": str})
    keep = tasks[tasks["keep"]].set_index(KEY)
    cat = load_active_catalog()

    rows = []
    for dim, run, study in SOURCES:
        lab = ok(pd.read_csv(BENCH / run / "labels_long.csv", dtype={"instance_id": str}))
        for r in lab[lab["demand"] == dim].itertuples(index=False):
            rows.append({"benchmark": r.benchmark, "instance_id": r.instance_id, "rubric": f"v2/{dim}",
                         "level": int(r.level), "judge_model": r.writer_model, "judge_effort": "low",
                         "judge_harness": "claude-code-subagent",
                         "prompt_builder": "adele.annotation.prompts.build_annotation_prompt_v2",
                         "prompt_sha256": r.prompt_sha256, "response_sha256": r.response_sha256,
                         "study": study, "run": Path(run).name})
    mass = ok(pd.read_csv(MASS_RUN / "labels.csv", dtype={"instance_id": str}))
    builder = json.loads((MASS_RUN / "manifest.json").read_text())["frozen"]["prompt"]["function"]
    for r in mass[mass["rubric_ref"].isin(["v2/PLp", "v2/PLe"])].itertuples(index=False):
        rows.append({"benchmark": r.benchmark, "instance_id": r.instance_id, "rubric": r.rubric_ref,
                     "level": int(r.level), "judge_model": r.writer_model, "judge_effort": r.effort,
                     "judge_harness": "claude-code-subagent" if r.backend == "subagent" else r.backend,
                     "prompt_builder": builder, "prompt_sha256": r.prompt_sha256,
                     "response_sha256": r.response_sha256, "study": "mass-annotation", "run": r.run})
    pls = ok(pd.read_csv(PLS_RUN / "labels.csv", dtype={"instance_id": str}))
    pls = pls[pls["benchmark"].str.startswith("tau2-") & (pls["rubric_ref"] == "v2/PLs")]
    frozen = json.loads((PLS_RUN / "manifest.json").read_text())["frozen"]
    for r in pls.itertuples(index=False):
        rows.append({"benchmark": r.benchmark, "instance_id": r.instance_id, "rubric": r.rubric_ref,
                     "level": int(r.level), "judge_model": r.writer_model, "judge_effort": r.effort,
                     "judge_harness": "claude-code-subagent" if r.backend == "subagent" else r.backend,
                     "prompt_builder": frozen["prompt"]["function"], "prompt_sha256": r.prompt_sha256,
                     "response_sha256": r.response_sha256, "study": "pls-relabel", "run": r.run})
    labels = pd.DataFrame(rows)
    labels = labels[labels.set_index(KEY).index.isin(keep.index)].drop_duplicates(KEY + ["rubric"], keep="first")
    missing = len(keep) * len(DIMS) - len(labels)
    assert missing == 0, f"{missing} clean-task labels missing"
    labels.sort_values(KEY + ["rubric"]).to_csv(OUT / "labels.csv", index=False)

    panel = pd.read_csv(BENCH / "panel/tasks.csv", dtype={"instance_id": str}).set_index(KEY)
    cols = ["file_id", "runs_counted", "solve_rate", "n_configs", "solve_rate_all", "n_configs_all",
            "solve_rate_mixed", "n_configs_mixed", "solve_rate_all_mixed", "n_configs_all_mixed"]
    wide = (keep[cols].join(panel["prompt_sha12"])
            .join(labels.pivot(index=KEY, columns="rubric", values="level")))
    wide.reset_index().to_csv(OUT / "labels_wide.csv", index=False)
    tasks.to_csv(OUT / "tasks.csv", index=False)
    rub = pd.DataFrame([{"rubric": f"v2/{d}", "code": d, "generation": "v2", "name": cat[d].full_name,
                         "file": str(Path(cat[d].file_path).relative_to(ROOT)),
                         "sha256": sha256(Path(cat[d].file_path).read_bytes())} for d in DIMS])
    rub.loc[rub["code"] == "PLs", "sha256"] = frozen["rubrics"]["v2/PLs"]["sha256"]  # pinned by pls-relabel
    rub.to_csv(OUT / "rubrics.csv", index=False)

    res = json.loads((HERE / "results/clean.json").read_text())
    plp = res["within_domain_vs_solve_rate"]["PLp"]["combined"]
    fill = {"{n_kept}": str(len(keep)), "{n_labels}": str(len(labels)), "{commit}": git("rev-parse", "--short", "HEAD"),
            "{n_new}": str(len(labels.loc[labels["run"] == MASS_RUN.name, KEY].drop_duplicates())),
            "{rho_plp}": f"{plp['rho']:+.2f}", "{p_plp}": f"{plp['p_two_sided']:.2g}"}
    card = (HERE / "DATACARD.md").read_text(encoding="utf-8")
    for k, v in fill.items():
        card = card.replace(k, v)
    (OUT / "README.md").write_text(card, encoding="utf-8")
    files = ["README.md", "tasks.csv", "labels.csv", "labels_wide.csv", "rubrics.csv"]
    (OUT / "MANIFEST.tsv").write_text("file\tsha256\n" + "".join(
        f"{f}\t{sha256((OUT / f).read_bytes())}\n" for f in files))
    print(f"release/: {len(keep)} tasks, {len(labels)} labels")


if __name__ == "__main__":
    main()
