"""Move a subagent run's state between machines through a PRIVATE Hugging Face dataset, never through git.

    python scripts/cloud/hf_sync.py push <run>   # this machine's ledger, labels, answers, relays, judge transcripts
    python scripts/cloud/hf_sync.py pull <run>   # the dataset's state into this machine (answers never overwritten)

The dataset (default ``adele-ai-evaluations/adele-cloud-runs``, or ``$ADELE_CLOUD_RUNS_REPO``) holds ``<run>/run/``
(ledger.csv, labels.csv), ``<run>/responses/``, ``<run>/relays/`` and ``<run>/transcripts/``. Transcripts carry task
text, so they stay private: ``push`` refuses a public dataset. ``pull`` refuses a ledger that lost or changed an
answer this machine already recorded (one run, one writer at a time), copies answer files without overwriting, and
leaves transcripts in ``data/cloud-runs/<run>/`` (gitignored). Then run ``adele mass check <run>``.
"""

import csv
import os
import shutil
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
RUNS = REPO / "experiments" / "benchmarks" / "mass-annotation" / "runs"
DATASET = os.environ.get("ADELE_CLOUD_RUNS_REPO", "adele-ai-evaluations/adele-cloud-runs")


def env(key: str, default: str) -> str:
    """$key, else its line in the repo's .env (as adele reads it), else ``default``."""
    if key in os.environ:
        return os.environ[key]
    dotenv = REPO / ".env"
    for line in dotenv.read_text().splitlines() if dotenv.exists() else []:
        if line.startswith(key + "="):
            return line.split("=", 1)[1].strip()
    return default


def io_dir(run: str) -> Path:
    return Path(env("ADELE_JUDGE_IO", "~/Developer/ADELE/judge-io")).expanduser() / run


def recorded(ledger: Path) -> dict:
    """(cell_id, attempt) -> response_sha256 for every attempt with an answer on record."""
    with open(ledger, newline="", encoding="utf-8") as fh:
        return {(r["cell_id"], r["attempt"]): r["response_sha256"] for r in csv.DictReader(fh) if r["response_sha256"]}


def push(run: str) -> None:
    from huggingface_hub import HfApi

    api = HfApi()
    if not api.repo_info(DATASET, repo_type="dataset").private:
        sys.exit(f"refusing: {DATASET} is not private")
    io, marker = io_dir(run), f"{io_dir(run)}/prompts/"
    with tempfile.TemporaryDirectory() as tmp:
        stage = Path(tmp)
        (stage / "run").mkdir()
        for name in ("ledger.csv", "labels.csv"):
            if (RUNS / run / name).exists():
                shutil.copy2(RUNS / run / name, stage / "run" / name)
        for sub in ("responses", "relays"):
            if (io / sub).exists():
                shutil.copytree(io / sub, stage / sub)
        n = 0
        for f in Path("~/.claude/projects").expanduser().rglob("agent-*.jsonl"):
            with open(f, encoding="utf-8") as fh:
                if marker not in fh.readline():
                    continue
            dest = stage / "transcripts" / f.parent.parent.name / f.name  # <session>/agent-<id>.jsonl
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(f, dest)
            if f.with_suffix(".meta.json").exists():
                shutil.copy2(f.with_suffix(".meta.json"), dest.with_suffix(".meta.json"))
            n += 1
        api.upload_folder(folder_path=str(stage), path_in_repo=run, repo_id=DATASET, repo_type="dataset",
                          commit_message=f"{run}: sync from {os.uname().nodename}")
    print(f"pushed {run} to {DATASET} ({n} judge transcripts)")


def pull(run: str) -> None:
    from huggingface_hub import snapshot_download

    local = REPO / "data" / "cloud-runs"
    snapshot_download(DATASET, repo_type="dataset", allow_patterns=[f"{run}/*"], local_dir=str(local))
    got = local / run
    if not (got / "run" / "ledger.csv").exists():
        sys.exit(f"{DATASET} has no ledger for {run}")
    mine, theirs = recorded(RUNS / run / "ledger.csv"), recorded(got / "run" / "ledger.csv")
    lost = [k for k, h in mine.items() if theirs.get(k) != h]
    if lost:
        sys.exit(f"refusing: {len(lost)} answers recorded here are missing or different there, e.g. {lost[:3]}")
    dst, new = io_dir(run) / "responses", 0
    for f in (got / "responses").rglob("*.txt") if (got / "responses").exists() else []:
        p = dst / f.relative_to(got / "responses")
        if p.exists():
            if p.read_bytes() != f.read_bytes():
                sys.exit(f"conflict: {p} differs from the dataset's copy")
            continue
        p.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(f, p)
        new += 1
    for name in ("ledger.csv", "labels.csv"):
        if (got / "run" / name).exists():
            shutil.copy2(got / "run" / name, RUNS / run / name)
    print(f"pulled {run}: {len(theirs)} recorded answers ({len(theirs) - len(mine)} new), {new} answer files added; "
          f"transcripts in {got / 'transcripts'}")


if __name__ == "__main__":
    if len(sys.argv) != 3 or sys.argv[1] not in ("push", "pull"):
        sys.exit(__doc__)
    {"push": push, "pull": pull}[sys.argv[1]](sys.argv[2])
