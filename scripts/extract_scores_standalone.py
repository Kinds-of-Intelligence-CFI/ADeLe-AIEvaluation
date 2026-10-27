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

Aggregate-only mode (fallback, if even per-sample flags cannot be shared):
    python extract_scores_standalone.py /path/to/logs agg.csv --aggregate annotations.csv
    # annotations.csv is the demand file WE provide: benchmark, sample_id, plus one
    # 0-5 column per demand dimension. The output then contains NO sample ids at
    # all — only, per (benchmark, model, dimension, level): n_samples, n_solved.
    # These are the sufficient statistics for fitting ability curves; individual
    # task outcomes stay entirely on your side.

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


def aggregate(rows, annotations_csv: str, out_csv: str) -> int:
    """Collapse per-sample rows against a demand-annotation CSV into counts.

    Output columns: benchmark, model, dimension, level, n_samples, n_solved.
    No sample ids leave this function.
    """
    ann = {}
    dims = []
    with open(annotations_csv, newline="") as fh:
        reader = csv.DictReader(fh)
        dims = [c for c in reader.fieldnames if c not in ("benchmark", "sample_id")]
        for r in reader:
            ann[(r["benchmark"], str(r["sample_id"]))] = r
    counts = {}
    matched = 0
    for row in rows:
        key = (row["benchmark"], str(row["sample_id"]))
        if key not in ann:
            continue
        solved = {"C": 1.0, "I": 0.0, "P": 0.5}.get(str(row["score"]).strip().upper())
        if solved is None:
            try:
                solved = min(max(float(row["score"]), 0.0), 1.0)
            except (TypeError, ValueError):
                continue
        matched += 1
        for d in dims:
            level = ann[key].get(d, "")
            if level == "":
                continue
            k = (row["benchmark"], row["model"], d, level)
            n, wins = counts.get(k, (0, 0.0))
            counts[k] = (n + 1, wins + solved)
    with open(out_csv, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["benchmark", "model", "dimension", "level", "n_samples", "n_solved"])
        for (b, m, d, lvl), (n, wins) in sorted(counts.items()):
            w.writerow([b, m, d, lvl, n, round(wins, 3)])
    print(f"aggregated {matched} scored samples against {len(ann)} annotations "
          f"-> {len(counts)} (benchmark, model, dimension, level) cells in {out_csv}")
    print(f"sha256({out_csv}) = {hashlib.sha256(Path(out_csv).read_bytes()).hexdigest()}")
    return 0


def main(logs_dir: str, out_csv: str, annotations_csv=None) -> int:
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

    if annotations_csv:
        return aggregate(rows, annotations_csv, out_csv)

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
    args = sys.argv[1:]
    ann = None
    if "--aggregate" in args:
        i = args.index("--aggregate")
        ann = args[i + 1] if i + 1 < len(args) else None
        args = args[:i] + args[i + 2:]
    if len(args) != 2 or ("--aggregate" in sys.argv and not ann):
        print(__doc__)
        print("usage: python extract_scores_standalone.py <logs_dir> <out.csv> "
              "[--aggregate annotations.csv]")
        raise SystemExit(2)
    raise SystemExit(main(args[0], args[1], ann))
