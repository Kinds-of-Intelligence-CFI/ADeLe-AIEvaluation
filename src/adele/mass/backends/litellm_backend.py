"""Direct calls through litellm (any provider; small runs and local models).

``submit`` only names the group (``<io>/api/<handle>.items.json``), so the runner records the handle in the ledger
before any call is made. ``poll`` makes the calls still missing from ``<io>/api/<handle>.jsonl``, appending each
record as soon as it completes; an interrupted group resumes with only its missing calls. ``fetch`` reads the
records. ``writer_model`` is each response's ``model`` field.
"""

import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from typing import Any, Dict, List

from adele.mass.backends import Answer, Item, accepts_temperature, custom_id, parse_custom_id


class LiteLLMBackend:
    name = "litellm"
    writes_files = True

    def __init__(self, completion: Any = None, max_workers: int = 8):
        if completion is None:
            import litellm
            completion = litellm.completion
        self.completion = completion
        self.max_workers = max_workers
        self._n = 0

    def _call(self, run: Any, cell: str, attempt: int) -> Dict[str, Any]:
        judge = run.judge
        kwargs: Dict[str, Any] = {"model": judge.model, "max_tokens": judge.max_tokens, "num_retries": 5,
                                  "messages": [{"role": "user", "content": run.prompt(cell)}]}
        if judge.effort:
            kwargs["reasoning_effort"] = judge.effort
        elif accepts_temperature(judge.model):
            kwargs["temperature"] = 0.0
        rec: Dict[str, Any] = {"custom_id": custom_id(cell, attempt)}
        try:
            resp = self.completion(**kwargs)
            usage = getattr(resp, "usage", None)
            rec.update(text=resp.choices[0].message.content or "", model=getattr(resp, "model", None),
                       tokens_in=getattr(usage, "prompt_tokens", None),
                       tokens_out=getattr(usage, "completion_tokens", None))
        except Exception as exc:  # recorded as an error attempt, retried per the spec's budget
            rec.update(error=f"{type(exc).__name__}: {exc}")
        return rec

    def submit(self, run: Any, items: List[Item]) -> str:
        self._n += 1
        handle = f"litellm-{datetime.now(timezone.utc):%Y%m%dT%H%M%S}-{self._n:02d}"
        d = run.io_dir / "api"
        d.mkdir(parents=True, exist_ok=True)
        (d / f"{handle}.items.json").write_text(json.dumps([list(it) for it in items]), encoding="utf-8")
        return handle

    def _records(self, run: Any, handle: str) -> List[Dict[str, Any]]:
        path = run.io_dir / "api" / f"{handle}.jsonl"
        if not path.exists():
            return []
        return [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]

    def poll(self, run: Any, handles: List[str]) -> Dict[str, str]:
        for h in handles:
            items = [tuple(x) for x in json.loads((run.io_dir / "api" / f"{h}.items.json").read_text())]
            done = {r["custom_id"] for r in self._records(run, h)}
            todo = [(c, a) for c, a in items if custom_id(c, a) not in done]
            if not todo:
                continue
            with open(run.io_dir / "api" / f"{h}.jsonl", "a", encoding="utf-8") as out, \
                    ThreadPoolExecutor(max_workers=self.max_workers) as pool:
                for fut in as_completed([pool.submit(self._call, run, c, a) for c, a in todo]):
                    out.write(json.dumps(fut.result()) + "\n")
                    out.flush()
        return {h: "done" for h in handles}

    def fetch(self, run: Any, handle: str, items: List[Item]) -> List[Answer]:
        got: Dict[Item, Answer] = {}
        for r in self._records(run, handle):
            cell, attempt = parse_custom_id(r["custom_id"])
            if "error" in r:
                got[(cell, attempt)] = Answer(cell, attempt, None, reason="error")
            else:
                got[(cell, attempt)] = Answer(cell, attempt, r["text"], r["model"], tokens_in=r["tokens_in"],
                                              tokens_out=r["tokens_out"])
        return [got.get((c, a), Answer(c, a, None, reason="error")) for c, a in items]
