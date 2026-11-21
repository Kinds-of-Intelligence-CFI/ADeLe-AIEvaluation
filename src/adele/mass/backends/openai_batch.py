"""OpenAI Batch API backend (``/v1/chat/completions``). The batch id is the handle and lives in the ledger, so a
batch is never lost to an interruption. ``writer_model`` is the ``model`` field of each response body.

Requests follow ``adele.annotation.prompts.build_batch_request``: temperature 0 except for reasoning models
(o-series, gpt-5*), which only take the default; the spec's effort, when set, is sent as ``reasoning_effort``.
``batches.create`` runs without SDK retries (a lost response must not leave a second, unrecorded batch). Requests
of an expired or cancelled batch that never ran go back to pending.
"""

import json
from typing import Any, Dict, List

from adele.mass.backends import Answer, Item, accepts_temperature, custom_id, parse_custom_id

TERMINAL = ("completed", "failed", "expired", "cancelled")


def build_request(run: Any, cell: str, attempt: int) -> Dict[str, Any]:
    """One Batch API JSONL line for an item."""
    judge = run.judge
    body: Dict[str, Any] = {"model": judge.model, "max_completion_tokens": judge.max_tokens,
                            "messages": [{"role": "user", "content": run.prompt(cell)}]}
    if judge.effort:
        body["reasoning_effort"] = judge.effort
    elif accepts_temperature(judge.model):
        body["temperature"] = 0
    return {"custom_id": custom_id(cell, attempt), "method": "POST", "url": "/v1/chat/completions", "body": body}


class OpenAIBatchBackend:
    name = "openai-batch"
    writes_files = True

    def __init__(self, client: Any = None):
        if client is None:
            import openai
            client = openai.OpenAI()
        self.client = client

    def submit(self, run: Any, items: List[Item]) -> str:
        jsonl = "".join(json.dumps(build_request(run, c, a)) + "\n" for c, a in items).encode("utf-8")
        f = self.client.files.create(file=(f"{run.name}.jsonl", jsonl), purpose="batch")
        batch = self.client.with_options(max_retries=0).batches.create(
            input_file_id=f.id, endpoint="/v1/chat/completions", completion_window="24h")
        return batch.id

    def poll(self, run: Any, handles: List[str]) -> Dict[str, str]:
        return {h: "done" if self.client.batches.retrieve(h).status in TERMINAL else "running" for h in handles}

    def _lines(self, file_id: Any) -> List[Dict[str, Any]]:
        if not file_id:
            return []
        return [json.loads(x) for x in self.client.files.content(file_id).text.splitlines() if x.strip()]

    def fetch(self, run: Any, handle: str, items: List[Item]) -> List[Answer]:
        batch = self.client.batches.retrieve(handle)
        got: Dict[Item, Answer] = {}
        for line in self._lines(batch.output_file_id) + self._lines(getattr(batch, "error_file_id", None)):
            cell, attempt = parse_custom_id(line["custom_id"])
            resp = line.get("response") or {}
            body = resp.get("body") or {}
            if (line.get("error") or {}).get("code") in ("batch_expired", "batch_cancelled"):
                got[(cell, attempt)] = Answer(cell, attempt, None, reason="not_sent")
                continue
            if resp.get("status_code") != 200 or not body.get("choices"):
                got[(cell, attempt)] = Answer(cell, attempt, None, reason="error")
                continue
            choice = body["choices"][0]
            usage = body.get("usage") or {}
            tokens = {"tokens_in": usage.get("prompt_tokens"), "tokens_out": usage.get("completion_tokens")}
            if choice.get("message", {}).get("refusal"):
                got[(cell, attempt)] = Answer(cell, attempt, None, body.get("model"), reason="refusal", **tokens)
                continue
            got[(cell, attempt)] = Answer(cell, attempt, choice["message"].get("content") or "", body.get("model"),
                                          **tokens)
        missing = "not_sent" if batch.status in ("expired", "cancelled") else "error"
        return [got.get((c, a), Answer(c, a, None, reason=missing)) for c, a in items]
