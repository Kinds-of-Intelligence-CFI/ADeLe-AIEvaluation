"""Anthropic Message Batches backend. The batch id is the handle, so an interrupted run resumes from the ledger.

Each request is one user message holding the pinned prompt. Effort goes in ``output_config``; thinking is left
at the model default (adaptive on Claude Opus 5.5, where it cannot be disabled). No server-side fallback model is
requested: an answer by another model would be rejected anyway. ``writer_model`` is each response's ``model``.
``batches.create`` runs without SDK retries: a retried create whose first response was lost would start a second,
unrecorded batch. Expired or canceled requests never reached the model, so they go back to pending.
"""

from typing import Any, Dict, List

from adele.mass.backends import Answer, Item, custom_id, parse_custom_id


def build_request(run: Any, cell: str, attempt: int) -> Dict[str, Any]:
    """One Message Batches request for an item."""
    judge = run.judge
    params: Dict[str, Any] = {"model": judge.model, "max_tokens": judge.max_tokens,
                              "messages": [{"role": "user", "content": run.prompt(cell)}]}
    if judge.effort:
        params["output_config"] = {"effort": judge.effort}
    return {"custom_id": custom_id(cell, attempt), "params": params}


class AnthropicBatchBackend:
    name = "anthropic-batch"
    writes_files = True

    def __init__(self, client: Any = None):
        if client is None:
            import anthropic
            client = anthropic.Anthropic()
        self.client = client

    def submit(self, run: Any, items: List[Item]) -> str:
        requests = [build_request(run, c, a) for c, a in items]
        batch = self.client.with_options(max_retries=0).messages.batches.create(requests=requests)
        return batch.id

    def poll(self, run: Any, handles: List[str]) -> Dict[str, str]:
        return {h: "done" if self.client.messages.batches.retrieve(h).processing_status == "ended" else "running"
                for h in handles}

    def fetch(self, run: Any, handle: str, items: List[Item]) -> List[Answer]:
        got: Dict[Item, Answer] = {}
        for res in self.client.messages.batches.results(handle):
            cell, attempt = parse_custom_id(res.custom_id)
            if res.result.type != "succeeded":
                reason = "not_sent" if res.result.type in ("expired", "canceled") else "error"
                got[(cell, attempt)] = Answer(cell, attempt, None, reason=reason)
                continue
            msg = res.result.message
            usage = getattr(msg, "usage", None)
            tokens = {"tokens_in": getattr(usage, "input_tokens", None),
                      "tokens_out": getattr(usage, "output_tokens", None)}
            if msg.stop_reason == "refusal":
                got[(cell, attempt)] = Answer(cell, attempt, None, msg.model, reason="refusal", **tokens)
                continue
            text = "".join(b.text for b in msg.content if b.type == "text")
            got[(cell, attempt)] = Answer(cell, attempt, text, msg.model, **tokens)
        return [got.get((c, a), Answer(c, a, None, reason="error")) for c, a in items]
