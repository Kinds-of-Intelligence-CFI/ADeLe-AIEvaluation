#!/usr/bin/env python3
"""Extract ONLY per-sample scores from Inspect eval logs — nothing else.

Purpose. We (the ADeLe project, Kinds of Intelligence Centre) study how
per-instance task demands predict model success. For that we need only the
success/failure flag per (benchmark sample, model) — never the prompts,
completions, reasoning traces, or any other log content. This script lets an
organization that holds Inspect ``.eval`` logs hand us exactly that and
nothing more.

What it reads:  every ``.eval`` file under the directory you point it at.
What it writes: one CSV with SIX columns —
    benchmark, model, sample_id, epoch, score, log_sha256_12
where ``score`` is the sample's scorer value ("C"/"I"/"P"/"N" or a number)
and ``log_sha256_12`` is a truncated hash of the source file so rows are
traceable without revealing content. The code never accesses sample content
fields — audit the ~40 lines of main(): only ``sample.id``, ``sample.epoch``
and each score's ``value`` are read.

Requirements: Python >= 3.10 and inspect-ai (already installed wherever the
logs were produced). No other dependencies; no network access.

Usage:
    python extract_scores_standalone.py /path/to/logs scores.csv
    # then review scores.csv (it is small and human-readable) and send it.

The script prints the row count, per-benchmark totals, and the output file's
SHA-256, so what you reviewed is verifiably what you send.
"""

import csv
import hashlib
import sys
from pathlib import Path


def file_hash(path: Path, n: int = 12) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()[:n]


def main(logs_dir: str, out_csv: str) -> int:
    try:
        from inspect_ai.log import read_eval_log
    except ImportError:
        print("error: inspect-ai is required (pip install inspect-ai)", file=sys.stderr)
        return 2

    log_files = sorted(Path(logs_dir).rglob("*.eval"))
    if not log_files:
        print(f"error: no .eval files under {logs_dir}", file=sys.stderr)
        return 2

    rows, per_benchmark = [], {}
    for lf in log_files:
        try:
            log = read_eval_log(str(lf))
        except Exception as exc:  # unreadable log: report, never crash the batch
            print(f"  skipped {lf.name}: {exc}", file=sys.stderr)
            continue
        task = getattr(log.eval, "task", "unknown")
        model = str(getattr(log.eval, "model", "unknown"))
        digest = file_hash(lf)
        for sample in log.samples or []:
            for scorer_name, score in (sample.scores or {}).items():
                rows.append({
                    "benchmark": task,
                    "model": model,
                    "sample_id": sample.id,
                    "epoch": getattr(sample, "epoch", 1),
                    "score": getattr(score, "value", ""),
                    "log_sha256_12": digest,
                })
                per_benchmark[task] = per_benchmark.get(task, 0) + 1
                break  # first scorer only — the headline metric

    with open(out_csv, "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=[
            "benchmark", "model", "sample_id", "epoch", "score", "log_sha256_12",
        ])
        writer.writeheader()
        writer.writerows(rows)

    print(f"wrote {len(rows)} score rows from {len(log_files)} logs to {out_csv}")
    for task, n in sorted(per_benchmark.items()):
        print(f"  {task}: {n}")
    print(f"sha256({out_csv}) = {hashlib.sha256(Path(out_csv).read_bytes()).hexdigest()}")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(__doc__)
        print("usage: python extract_scores_standalone.py <logs_dir> <out.csv>")
        raise SystemExit(2)
    raise SystemExit(main(sys.argv[1], sys.argv[2]))
