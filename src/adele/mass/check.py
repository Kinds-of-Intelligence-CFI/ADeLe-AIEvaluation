"""Audit a run: coverage by benchmark x rubric, answer-file integrity, and for subagent runs the protocol of every
judge transcript (:func:`adele.mass.backends.subagent.transcript_problems`) and the judge agent files.

The check fails on: answer files changed or missing since they were recorded, agent files changed since the pin,
any transcript that broke the protocol, and any answer file judged more than once. A protocol breach in an attempt
the ledger already rejected (its answer is not used) is listed under ``rejected_failures`` and does not fail it.
"""

from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from adele.mass.backends.subagent import expected_cwd, scan_transcripts, transcript_problems
from adele.mass.ledger import Ledger
from adele.mass.pin import Run, agent_drift, sha256


def protocol_report(run: Run, transcripts_dir: Path, cwd: Optional[str] = None,
                    rejected: Optional[Set[str]] = None) -> Dict[str, Any]:
    """Check every judge transcript of this run found under ``transcripts_dir``. ``rejected``: response paths of
    attempts the ledger rejected; their breaches go to ``rejected_failures``."""
    want_cwd = expected_cwd(run, cwd)
    failures: List[Dict[str, Any]] = []
    rejected_failures: List[Dict[str, Any]] = []
    calls: Counter = Counter()
    stops, models = [], Counter()
    transcripts = scan_transcripts(transcripts_dir, run.io_dir)
    for t in transcripts:
        cell = Path(t.prompt_path).stem
        problems = transcript_problems(run, t, want_cwd)
        calls[t.response_path] += 1
        models.update(t.models)  # judge transcripts in which each model answered
        if t.stopped:
            stops.append(cell)
        if problems:
            (rejected_failures if t.response_path in (rejected or set()) else failures).append(
                {"transcript": str(t.path), "cell": cell, "problems": problems})
    return {"transcripts": len(transcripts), "failures": failures, "rejected_failures": rejected_failures,
            "classifier_stops": sorted(stops),
            "called_more_than_once": sorted(p for p, n in calls.items() if n > 1),  # response paths
            "models": dict(models)}


def check(run: Run, transcripts_dir: Optional[Path] = None, cwd: Optional[str] = None) -> Dict[str, Any]:
    """Coverage, ledger consistency (answer files present and unchanged) and, for subagent runs, the protocol."""
    ledger = Ledger.load(run.dir)
    coverage = ledger.summary(run.cells, run.judge.retry)
    changed, missing = [], []
    for r in ledger.rows.values():
        if r["response_sha256"]:
            path = run.response_path(r["cell_id"], int(r["attempt"]))
            if not path.exists():
                missing.append(str(path))
            elif sha256(path.read_bytes()) != r["response_sha256"]:
                changed.append(str(path))
    reasons = Counter(r["reason"] for r in ledger.with_status("rejected"))
    report: Dict[str, Any] = {"coverage": coverage, "totals": coverage.sum().to_dict(),
                              "rejections": dict(reasons), "changed_answers": changed, "missing_answers": missing,
                              "agent_drift": agent_drift(run), "protocol": None}
    if run.judge.backend == "subagent" and transcripts_dir is not None:
        rejected = {str(run.response_path(r["cell_id"], int(r["attempt"]))) for r in ledger.with_status("rejected")}
        report["protocol"] = protocol_report(run, Path(transcripts_dir).expanduser(), cwd, rejected)
    p = report["protocol"]
    report["ok"] = not (changed or missing or report["agent_drift"]
                        or (p and (p["failures"] or p["called_more_than_once"])))
    return report
