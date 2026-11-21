"""A deterministic in-memory backend for tests: no files, no network.

By default every item gets a parseable answer by the requested model with a level derived from the cell id.
``script`` overrides attempts: ``{(cell_id, attempt): "wrong_writer" | "unparsed" | "refusal" | "error"}``.
"""

import hashlib
from typing import Any, Dict, List, Optional

from adele.mass.backends import Answer, Item


class FakeBackend:
    name = "fake"
    writes_files = True

    def __init__(self, script: Optional[Dict[Item, str]] = None, other_model: str = "claude-opus-4-8"):
        self.script = dict(script or {})
        self.other_model = other_model
        self.batches: Dict[str, List[Item]] = {}
        self.calls: List[Item] = []

    def submit(self, run: Any, items: List[Item]) -> str:
        handle = f"fake-{len(self.batches) + 1}"
        for cell, _ in items:
            run.prompt(cell)  # like a real backend, fails if the prompt is missing or altered
        self.batches[handle] = list(items)
        self.calls.extend(items)
        return handle

    def poll(self, run: Any, handles: List[str]) -> Dict[str, str]:
        return {h: "done" for h in handles}

    def fetch(self, run: Any, handle: str, items: List[Item]) -> List[Answer]:
        out = []
        for cell, attempt in items:
            kind = self.script.get((cell, attempt), "ok")
            level = int(hashlib.sha256(cell.encode()).hexdigest(), 16) % 6
            model = run.judge.model
            if kind == "refusal":
                out.append(Answer(cell, attempt, None, model, reason="refusal"))
            elif kind == "error":
                out.append(Answer(cell, attempt, None, None, reason="error"))
            else:
                text = "I cannot say." if kind == "unparsed" else \
                    f"Assessment.\n\nThe level of X demanded by this task is: {level}"
                writer = self.other_model if kind == "wrong_writer" else model
                out.append(Answer(cell, attempt, text, writer, tokens_in=100, tokens_out=20))
        return out
