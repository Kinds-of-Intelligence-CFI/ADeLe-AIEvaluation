"""Move cells through the ledger with any backend: submit the next items, then poll, fetch and record answers.

Every step saves the ledger before returning, so a run interrupted anywhere resumes where it stopped: submitted
items keep their handle and are fetched later, never sent again.
"""

from collections import Counter
from typing import Any, Callable, Dict, List, Optional, Tuple

from adele.mass.backends import Answer, Item, JudgeBackend
from adele.mass.ledger import Ledger
from adele.mass.pin import Run, sha256


def submit_next(run: Run, ledger: Ledger, backend: JudgeBackend, *, batch_size: int,
                max_cells: Optional[int] = None, max_batches: Optional[int] = None,
                on_sent: Optional[Callable[[str, List[Item]], None]] = None) -> List[Tuple[str, List[Item]]]:
    """Send up to ``max_cells`` items in groups of at most ``batch_size`` (one attempt per group).

    Every prompt is checked against its pinned hash before anything is recorded. Each group is saved to the
    ledger, then passed to ``on_sent``, before the next is sent. Returns the (handle, items) of each group sent.
    """
    todo = ledger.to_submit(run.judge.retry)[:max_cells]
    by_attempt: Dict[int, List[Item]] = {}
    for item in todo:
        by_attempt.setdefault(item[1], []).append(item)
    groups = [g[i:i + batch_size] for _, g in sorted(by_attempt.items()) for i in range(0, len(g), batch_size)]
    groups = groups[:max_batches]
    for items in groups:
        for cell, _ in items:
            run.prompt(cell)
    sent = []
    for items in groups:
        handle = backend.submit(run, items)
        for cell, attempt in items:
            ledger.set(cell, attempt, status="submitted", handle=handle, backend=backend.name, reason="")
        ledger.save()
        sent.append((handle, items))
        if on_sent is not None:
            on_sent(handle, items)
    return sent


def release(run: Run, ledger: Ledger, handles: Optional[List[str]] = None) -> Tuple[List[Item], List[Item]]:
    """Return the submitted items of ``handles`` (all when None) to pending without using up their attempt.

    For relays or batches that never reached a judge. Items whose answer file exists are kept (they were
    judged; collect them). Returns (released, kept).
    """
    released, kept = [], []
    for r in ledger.with_status("submitted"):
        if handles is not None and r["handle"] not in handles:
            continue
        item = (r["cell_id"], int(r["attempt"]))
        if run.response_path(*item).exists():
            kept.append(item)
        else:
            ledger.release(*item)
            released.append(item)
    ledger.save()
    return released, kept


def record(run: Run, ledger: Ledger, backend: JudgeBackend, a: Answer) -> None:
    """Write an API answer to its response file (outside the repo) and move the attempt to answered or rejected."""
    if a.text is None:
        if a.reason == "not_sent":  # never reached a judge: the attempt is not used up (within MAX_RETURNS)
            ledger.release(a.cell_id, a.attempt)
        else:
            ledger.set(a.cell_id, a.attempt, status="rejected", reason=a.reason or "error",
                       writer_model=a.writer_model, tokens_in=a.tokens_in, tokens_out=a.tokens_out)
        return
    path = run.response_path(a.cell_id, a.attempt)
    if backend.writes_files:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(a.text.encode("utf-8"))
    ledger.set(a.cell_id, a.attempt, status="answered", writer_model=a.writer_model,
               response_sha256=sha256(path.read_bytes()), tokens_in=a.tokens_in, tokens_out=a.tokens_out,
               protocol=a.protocol)


def sync(run: Run, ledger: Ledger, backend: JudgeBackend) -> Counter:
    """Poll every outstanding handle; fetch and record the finished ones. Returns counts of the new statuses."""
    by_handle: Dict[str, List[Item]] = {}
    for r in ledger.with_status("submitted"):
        by_handle.setdefault(r["handle"], []).append((r["cell_id"], int(r["attempt"])))
    counts: Counter = Counter()
    if not by_handle:
        return counts
    states = backend.poll(run, sorted(by_handle))
    for handle, items in by_handle.items():
        if states.get(handle) != "done":
            counts["still_running"] += len(items)
            continue
        for a in backend.fetch(run, handle, items):
            record(run, ledger, backend, a)
            counts[ledger.rows[(a.cell_id, a.attempt)]["status"]] += 1
        ledger.save()
    return counts


def preview(run: Run, item: Item) -> Dict[str, Any]:
    """The request an API backend would send for one item (for ``--dry-run``)."""
    backend = run.judge.backend
    if backend == "anthropic-batch":
        from adele.mass.backends.anthropic_batch import build_request
    elif backend == "openai-batch":
        from adele.mass.backends.openai_batch import build_request
    else:
        return {"backend": backend, "model": run.judge.model, "effort": run.judge.effort}
    req = build_request(run, *item)
    body = req.get("params") or req["body"]
    body["messages"] = [{"role": "user", "content": f"<prompt {item[0]}: {len(run.prompt(item[0]))} chars>"}]
    return req
