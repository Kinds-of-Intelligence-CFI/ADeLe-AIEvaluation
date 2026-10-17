"""Build the shareable release of the tau2 clean set: release/ (a Hugging Face dataset layout).

  release/README.md        the data card (Hugging Face front matter + documentation), written by this script
  release/tasks.csv        all 257 non-telecom tau2 tasks with frozen-text results: solve rates, exclusion reason, keep
  release/labels.csv       one row per (clean task, rubric): level and full provenance
  release/labels_wide.csv  one row per clean task: solve rates, text hash, one column per rubric
  release/rubrics.csv      one row per rubric text used: code, generation, name, file, sha256, and the runs that used it
  release/MANIFEST.tsv     sha256 of every file above

Labels (PLp, PLe, PLs; ../release.py `current_labels`): all from relabel-v2 (examples review of 2026-10-04, d4ec2ec),
with PLp re-judged in relabel-v3 for cells at PLp 3-5 after the synthesis example moved to Level 4 (d6cc9ca). The
merge is one-sided: only cells at 3-5 were re-judged (relabel-v3/RESULTS.md). Inputs are committed files only
(tasks.csv, panel/tasks.csv, and the labels.csv and manifest.json of those mass runs), so the release can be rebuilt at
any commit. Only answers written by claude-opus-5-5 are exported. The card's PLp correlation is computed here from the
released labels, as in analysis/analyse.py (tau2-tb4-pl's `combined`: Spearman per domain, combined by Fisher z).
No task text. Tasks are keyed by (benchmark, instance_id): tau2 ids repeat across domains.

    python experiments/benchmarks/tau2-clean/export.py
"""

import hashlib
import importlib.util
import subprocess
import sys
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BENCH = HERE.parent
OUT = HERE / "release"
DIMS = ["PLp", "PLe", "PLs"]
KEY = ["benchmark", "instance_id"]
DOMAINS = ["tau2-airline", "tau2-retail", "tau2-banking_knowledge"]


def load(name: str, path: Path):
    sys.path.insert(0, str(path.parent))
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


release = load("release", BENCH / "release.py")
combined = load("t2_analyse", BENCH / "tau2-tb4-pl/analysis/analyse.py").combined


def sha256(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def git(*args: str) -> str:
    return subprocess.run(["git", "-C", str(ROOT), *args], capture_output=True, text=True, check=True).stdout.strip()


def main() -> None:
    OUT.mkdir(exist_ok=True)
    tasks = pd.read_csv(HERE / "tasks.csv", dtype={"instance_id": str})
    keep = tasks[tasks["keep"]].set_index(KEY)

    labels = release.current_labels(DOMAINS, DIMS)
    labels = labels[labels.set_index(KEY).index.isin(keep.index)]
    missing = len(keep) * len(DIMS) - len(labels)
    assert missing == 0, f"{missing} clean-task labels missing"
    labels.to_csv(OUT / "labels.csv", index=False)

    panel = pd.read_csv(BENCH / "panel/tasks.csv", dtype={"instance_id": str}).set_index(KEY)
    cols = ["file_id", "runs_counted", "solve_rate", "n_configs", "solve_rate_all", "n_configs_all",
            "solve_rate_mixed", "n_configs_mixed", "solve_rate_all_mixed", "n_configs_all_mixed"]
    wide = keep[cols].join(panel["prompt_sha12"]).join(release.wide(labels, DIMS, KEY))
    wide.reset_index().to_csv(OUT / "labels_wide.csv", index=False)
    tasks.to_csv(OUT / "tasks.csv", index=False)
    release.rubrics(labels, DIMS).to_csv(OUT / "rubrics.csv", index=False)

    plp = combined(wide.reset_index(), "v2/PLp", "solve_rate", "negative")["combined"]
    fill = {"{n_kept}": str(len(keep)), "{n_labels}": str(len(labels)), "{commit}": git("rev-parse", "--short", "HEAD"),
            "{rho_plp}": f"{plp['rho']:+.2f}", "{p_plp}": f"{plp['p_two_sided']:.2g}"}
    card = (HERE / "DATACARD.md").read_text(encoding="utf-8")
    for k, v in fill.items():
        card = card.replace(k, v)
    assert "{" not in card.split("---", 2)[2], "unfilled placeholder in DATACARD.md"
    (OUT / "README.md").write_text(card, encoding="utf-8")
    files = ["README.md", "tasks.csv", "labels.csv", "labels_wide.csv", "rubrics.csv"]
    (OUT / "MANIFEST.tsv").write_text("file\tsha256\n" + "".join(
        f"{f}\t{sha256((OUT / f).read_bytes())}\n" for f in files))
    print(f"release/: {len(keep)} tasks, {len(labels)} labels; PLp within domain {fill['{rho_plp}']} "
          f"(p = {fill['{p_plp}']})")


if __name__ == "__main__":
    main()
