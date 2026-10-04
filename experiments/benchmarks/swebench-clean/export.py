"""Build the shareable release of the SWE-bench Verified clean set: release/ (a Hugging Face dataset layout).

  release/README.md        the data card (Hugging Face front matter + documentation), written by this script
  release/tasks.csv        all 500 Verified tasks: solve counts, exclusion reasons, keep flag
  release/labels.csv       one row per (clean task, rubric): level and full provenance
  release/labels_wide.csv  one row per clean task: solve rate, time-to-fix bucket, one column per rubric
  release/rubrics.csv      one row per rubric text used: code, generation, name, file, sha256, and the runs that used it
  release/MANIFEST.tsv     sha256 of every file above

Labels (PLp, PLe, PLs; ../release.py `current_labels`): all from relabel-v2 (examples review of 2026-10-04, d4ec2ec),
with PLp re-judged in relabel-v3 for cells at PLp 3-5 after the synthesis example moved to Level 4 (d6cc9ca). The
merge is one-sided: only cells at 3-5 were re-judged (relabel-v3/RESULTS.md). Inputs are committed files only
(tasks.csv and the labels.csv and manifest.json of those mass runs), so the release can be rebuilt at any commit. Only
answers written by claude-opus-5-5 are exported. The card's numbers on labels are computed here from the released
labels, as in analysis/analyse.py (swebench-pl's `rho` on the clean tasks). No task text.

    uv run --extra annotate python experiments/benchmarks/swebench-clean/export.py
"""

import hashlib
import importlib.util
import subprocess
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BENCH = HERE.parent
OUT = HERE / "release"
DIMS = ["PLp", "PLe", "PLs"]


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


release = load("release", BENCH / "release.py")
swe = load("swepl_analyse", BENCH / "swebench-pl/analysis/analyse.py")


def sha256(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def git(*args: str) -> str:
    return subprocess.run(["git", "-C", str(ROOT), *args], capture_output=True, text=True, check=True).stdout.strip()


def main() -> None:
    from datasets import load_dataset

    OUT.mkdir(exist_ok=True)
    tasks = pd.read_csv(HERE / "tasks.csv")
    keep = tasks[tasks["keep"]].set_index("instance_id")

    labels = release.release_labels(HERE, "swe-bench-verified", DIMS)
    missing = len(keep) * len(DIMS) - len(labels)
    assert missing == 0, f"{missing} clean-task labels missing"
    labels.to_csv(OUT / "labels.csv", index=False)

    meta = load_dataset("princeton-nlp/SWE-bench_Verified", split="test", revision=swe.HF_REVISION).to_pandas()
    meta = meta.set_index("instance_id")
    wide = (keep[["solved_by", "of_entries", "solve_rate"]].join(meta["difficulty"].rename("time_to_fix"))
            .join(release.wide(labels, DIMS)))
    wide["time_to_fix_bucket"] = wide["time_to_fix"].map(swe.BUCKETS)
    wide.reset_index().to_csv(OUT / "labels_wide.csv", index=False)
    tasks.to_csv(OUT / "tasks.csv", index=False)
    release.rubrics(labels, DIMS).to_csv(OUT / "rubrics.csv", index=False)

    plp, hard = wide["v2/PLp"], wide["solved_by"] <= 6
    q1 = swe.rho(plp, wide["solve_rate"], "negative")
    q2 = swe.rho(plp, wide["time_to_fix_bucket"], "positive")
    fill = {"{n_kept}": str(len(keep)), "{n_labels}": str(len(labels)), "{commit}": git("rev-parse", "--short", "HEAD"),
            "{n_hard}": str(int(hard.sum())), "{rho_solve}": f"{q1['rho']:+.2f}", "{rho_ttf}": f"{q2['rho']:+.2f}",
            "{plp_hard}": f"{plp[hard].mean():.2f}", "{plp_rest}": f"{plp[~hard].mean():.2f}"}
    card = (HERE / "DATACARD.md").read_text(encoding="utf-8")
    for k, v in fill.items():
        card = card.replace(k, v)
    assert "{" not in card.split("---", 2)[2], "unfilled placeholder in DATACARD.md"
    (OUT / "README.md").write_text(card, encoding="utf-8")
    files = ["README.md", "tasks.csv", "labels.csv", "labels_wide.csv", "rubrics.csv"]
    (OUT / "MANIFEST.tsv").write_text("file\tsha256\n" + "".join(
        f"{f}\t{sha256((OUT / f).read_bytes())}\n" for f in files))
    print(f"release/: {len(keep)} tasks, {len(labels)} labels; PLp vs solve rate {fill['{rho_solve}']}, "
          f"vs time-to-fix {fill['{rho_ttf}']}; PLp hard {fill['{plp_hard}']}, rest {fill['{plp_rest}']}")


if __name__ == "__main__":
    main()
