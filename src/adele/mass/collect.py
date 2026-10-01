"""Turn answered attempts into labels: parse the level, apply the writer rule, write ``labels.csv``.

For subagent runs, an answer whose judge transcript broke the protocol is rejected first (``protocol``: wrong
message, working directory, tools, attachments, effort or agent, or the cell judged more than once). An answer
written by a model other than the requested one is rejected (``fallback_writer``), whatever it says; an answer
without a readable level is rejected (``unparsed``). Rejected cells are retried by later submissions
while their budget lasts. ``labels.csv`` has one row per finished cell (a label, or none after the budget) in
one schema for every backend; ``protocol_ok`` is the protocol verdict of the row's attempt (empty for API
backends, which have no transcript). Raw answers stay in the judge-io folder, never in the repo.
"""

import re
from typing import Any, Dict, Optional

import pandas as pd

from adele.annotation.parsing import extract_demand_level
from adele.mass.backends import JudgeBackend
from adele.mass.ledger import Ledger
from adele.mass.pin import Run, sha256
from adele.mass.runner import sync

LABEL_COLUMNS = ["run", "cell_id", "benchmark", "instance_id", "rubric_ref", "generation", "repeat", "backend",
                 "model_requested", "writer_model", "effort", "prompt_builder", "prompt_sha256", "level", "valid",
                 "response_sha256", "attempt", "protocol_ok"]


def is_requested(writer: str, model: str) -> bool:
    """Whether ``writer`` is the requested model. A dated snapshot suffix (``claude-haiku-4-5-20251001``,
    ``gpt-4o-2024-08-06``) and a litellm provider prefix (``anthropic/``) are allowed; another model
    (``claude-opus-5-5`` for ``claude-opus-5``) is not."""
    model = model.split("/")[-1]
    return bool(re.fullmatch(re.escape(model) + r"(-\d{8}|-\d{4}-\d{2}-\d{2})?", (writer or "").split("/")[-1]))


def judge_answers(run: Run, ledger: Ledger) -> int:
    """Parse every answered attempt into parsed or rejected; returns how many were judged."""
    answered = ledger.with_status("answered")
    for r in answered:
        cell, attempt = r["cell_id"], int(r["attempt"])
        path = run.response_path(cell, attempt)
        data = path.read_bytes()
        if sha256(data) != r["response_sha256"]:
            raise ValueError(f"{path} changed after it was recorded")
        level, ok = extract_demand_level(data.decode("utf-8"))
        if r.get("protocol") not in ("", "ok", None):
            ledger.set(cell, attempt, status="rejected", reason="protocol")
        elif not is_requested(r["writer_model"], run.judge.model):
            ledger.set(cell, attempt, status="rejected", reason="fallback_writer")
        elif not ok:
            ledger.set(cell, attempt, status="rejected", reason="unparsed")
        else:
            ledger.set(cell, attempt, status="parsed", level=int(level))
    ledger.save()
    return len(answered)


def labels(run: Run, ledger: Ledger) -> pd.DataFrame:
    """One row per finished cell: its parsed label, or ``valid=False`` once the retry budget is spent."""
    states = ledger.states(run.judge.retry)
    judge, frozen = run.judge, run.manifest["frozen"]
    rows = []
    for cell, r in ledger.latest().items():
        if states[cell] not in ("done", "no_label"):
            continue
        c = run.cells.loc[cell]
        valid = states[cell] == "done"
        rows.append({"run": run.name, "cell_id": cell, "benchmark": c["benchmark"], "instance_id": c["instance_id"],
                     "rubric_ref": c["rubric_ref"], "generation": c["generation"], "repeat": int(c["repeat"]),
                     "backend": r["backend"], "model_requested": judge.model, "writer_model": r["writer_model"],
                     "effort": judge.effort or "", "prompt_builder": frozen["prompt"]["builder"],
                     "prompt_sha256": c["prompt_sha256"], "level": int(r["level"]) if valid else None,
                     "valid": valid, "response_sha256": r["response_sha256"], "attempt": int(r["attempt"]),
                     "protocol_ok": {"": None, "ok": True}.get(r.get("protocol") or "", False)})
    df = pd.DataFrame(rows, columns=LABEL_COLUMNS)
    df["level"] = df["level"].astype("Int64")
    return df


def collect(run: Run, backend: Optional[JudgeBackend] = None, ledger: Optional[Ledger] = None) -> Dict[str, Any]:
    """Fetch finished handles (if a backend is given), judge the answers and rewrite ``labels.csv``."""
    ledger = ledger or Ledger.load(run.dir)
    fetched = dict(sync(run, ledger, backend)) if backend is not None else {}
    judged = judge_answers(run, ledger)
    df = labels(run, ledger)
    df.to_csv(run.dir / "labels.csv", index=False)
    return {"fetched": fetched, "judged": judged, "labels": int(df["valid"].sum()),
            "no_label": int((~df["valid"]).sum()), "cells": len(run.cells)}
