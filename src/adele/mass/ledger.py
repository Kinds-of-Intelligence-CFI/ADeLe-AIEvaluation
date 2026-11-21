"""The ledger: one row per (cell, attempt), the single source of truth for a run's progress.

Statuses: ``pending`` (not yet sent), ``submitted`` (sent; ``handle`` names the relay or batch), ``answered``
(an answer file exists; ``writer_model`` known), ``parsed`` (a valid label by the requested model) and
``rejected`` (``reason`` is one of ``fallback_writer``, ``unparsed``, ``refusal``, ``error``, ``protocol``). A
rejected cell is retried while the number of its rejections for that reason is within the spec's budget for it;
after that it has no label. A submitted attempt that never reached a judge returns to pending without being used
up, at most ``MAX_RETURNS`` times (``returns``); after that it counts as an ``error``. ``protocol`` is ``ok``, the
protocol problems of the judge transcript, or empty when not checked (API backends). The file is rewritten
atomically on every save, and every mutating command holds :func:`run_lock`, so any command can stop and any
session resume.
"""

import csv
import fcntl
import os
from collections import Counter
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, Iterator, List, Tuple

import pandas as pd

COLUMNS = ["cell_id", "attempt", "status", "backend", "handle", "writer_model", "level", "reason",
           "response_sha256", "tokens_in", "tokens_out", "returns", "protocol", "created_at", "updated_at"]
STATUSES = ("pending", "submitted", "answered", "parsed", "rejected")
MAX_RETURNS = 3
Key = Tuple[str, int]


class RunLocked(RuntimeError):
    """Another command holds the run's lock."""


@contextmanager
def run_lock(run_dir: Path) -> Iterator[None]:
    """Exclusive lock on a run (``<run>/.lock``): two commands never change one ledger at once."""
    with open(Path(run_dir) / ".lock", "w") as f:
        try:
            fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise RunLocked(f"run {Path(run_dir).name} is locked by another adele mass command") from None
        try:
            yield
        finally:
            fcntl.flock(f, fcntl.LOCK_UN)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class Ledger:
    """Rows keyed by (cell_id, attempt), kept in pin order."""

    def __init__(self, path: Path, rows: Dict[Key, Dict[str, str]]):
        self.path = Path(path)
        self.rows = rows

    @classmethod
    def create(cls, run_dir: Path, cell_ids: Iterable[str], backend: str) -> "Ledger":
        path = Path(run_dir) / "ledger.csv"
        if path.exists():
            raise FileExistsError(f"{path} already exists")
        now = _now()
        rows = {(c, 1): {**dict.fromkeys(COLUMNS, ""), "cell_id": c, "attempt": "1", "status": "pending",
                         "backend": backend, "created_at": now, "updated_at": now} for c in cell_ids}
        ledger = cls(path, rows)
        ledger.save()
        return ledger

    @classmethod
    def load(cls, run_dir: Path) -> "Ledger":
        path = Path(run_dir) / "ledger.csv"
        with open(path, newline="", encoding="utf-8") as f:
            rows = {(r["cell_id"], int(r["attempt"])): r for r in csv.DictReader(f)}
        return cls(path, rows)

    def save(self) -> None:
        order: Dict[str, int] = {}
        for cell, _ in self.rows:
            order.setdefault(cell, len(order))
        tmp = self.path.with_suffix(".csv.tmp")
        with open(tmp, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=COLUMNS, lineterminator="\n")
            w.writeheader()
            for (cell, attempt), r in sorted(self.rows.items(), key=lambda kv: (order[kv[0][0]], kv[0][1])):
                w.writerow(r)
        os.replace(tmp, self.path)

    def set(self, cell: str, attempt: int, **fields) -> None:
        """Insert or update the row of one attempt."""
        bad = set(fields) - set(COLUMNS)
        if bad:
            raise KeyError(f"unknown ledger fields {sorted(bad)}")
        if fields.get("status", "pending") not in STATUSES:
            raise ValueError(f"bad status {fields['status']!r}")
        key = (cell, attempt)
        if key not in self.rows:
            if (cell, 1) not in self.rows:
                raise KeyError(f"{cell} is not a cell of this run")
            self.rows[key] = {**dict.fromkeys(COLUMNS, ""), "cell_id": cell, "attempt": str(attempt),
                              "backend": self.rows[(cell, 1)]["backend"], "created_at": _now()}
        self.rows[key].update({k: "" if v is None else str(v) for k, v in fields.items()}, updated_at=_now())

    def release(self, cell: str, attempt: int) -> bool:
        """Return a submitted attempt that never reached a judge to pending, without using it up. After
        ``MAX_RETURNS`` returns it is rejected as ``error`` instead (returns False), so a cell cannot loop."""
        n = int(self.rows[(cell, attempt)].get("returns") or 0) + 1
        if n > MAX_RETURNS:
            self.set(cell, attempt, status="rejected", reason="error", returns=n)
            return False
        self.set(cell, attempt, status="pending", handle="", returns=n)
        return True

    def latest(self) -> Dict[str, Dict[str, str]]:
        """The row of each cell's latest attempt."""
        out: Dict[str, Dict[str, str]] = {}
        for (cell, attempt), r in self.rows.items():
            if cell not in out or attempt > int(out[cell]["attempt"]):
                out[cell] = r
        return out

    def states(self, retry: Dict[str, int]) -> Dict[str, str]:
        """Each cell's state: ``done``, ``no_label`` (retry budget spent), ``in_flight`` or ``todo``."""
        rejections: Dict[str, Counter] = {}
        for (c, _), r in self.rows.items():
            if r["status"] == "rejected":
                rejections.setdefault(c, Counter())[r["reason"]] += 1
        out = {}
        for c, r in self.latest().items():
            if r["status"] == "parsed":
                out[c] = "done"
            elif r["status"] in ("submitted", "answered"):
                out[c] = "in_flight"
            elif r["status"] == "rejected":
                n = rejections[c][r["reason"]]
                out[c] = "todo" if n <= retry.get(r["reason"], 0) else "no_label"
            else:
                out[c] = "todo"
        return out

    def to_submit(self, retry: Dict[str, int]) -> List[Key]:
        """(cell, attempt) pairs to send next: pending attempts, and new attempts for retryable rejections."""
        states = self.states(retry)
        out = []
        for cell, r in self.latest().items():
            if states[cell] == "todo":
                out.append((cell, int(r["attempt"]) + (r["status"] == "rejected")))
        return out

    def with_status(self, status: str) -> List[Dict[str, str]]:
        return [r for r in self.rows.values() if r["status"] == status]

    def summary(self, cells: pd.DataFrame, retry: Dict[str, int]) -> pd.DataFrame:
        """Cell counts by benchmark x rubric: done, no_label, in_flight, todo."""
        states = pd.Series(self.states(retry), name="state")
        df = cells[["cell_id", "benchmark", "rubric_ref"]].reset_index(drop=True).join(states, on="cell_id")
        table = pd.crosstab([df["benchmark"], df["rubric_ref"]], df["state"])
        for col in ("done", "no_label", "in_flight", "todo"):
            if col not in table.columns:
                table[col] = 0
        return table[["done", "no_label", "in_flight", "todo"]]
