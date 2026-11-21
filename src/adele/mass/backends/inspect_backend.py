"""Any model Inspect supports (Anthropic, OpenAI, Google, Mistral, Together, OpenRouter, vLLM, ...), through the
provider's batch API where Inspect has one.

``judge.model`` is an Inspect model name, e.g. ``anthropic/claude-opus-5-5`` or ``openai/gpt-5.5``. ``judge.batch``
(default true) turns Inspect's batching on. ``judge.effort`` goes to Inspect's ``effort`` for Anthropic models and to
``reasoning_effort`` for the others.

``submit`` only names the group (``<io>/api/<handle>.items.json``), so the runner records the handle in the ledger
before any call is made. ``poll`` runs one Inspect eval over the items still missing from ``<io>/api/<handle>.jsonl``
(one sample per item: the frozen prompt, ``generate()``, no scorer) and appends one record per sample; Inspect's own
log goes to ``<io>/inspect/``. An interrupted group resumes with only its missing items. ``fetch`` reads the records.
"""

import json
from datetime import datetime, timezone
from typing import Any, Dict, List

from adele.mass.backends import Answer, Item, accepts_temperature, custom_id, parse_custom_id


def generate_config(judge: Any) -> Dict[str, Any]:
    """Inspect generation settings for a judge spec."""
    config: Dict[str, Any] = {"max_tokens": judge.max_tokens, "max_retries": 5, "batch": judge.batch}
    if judge.effort:
        config["effort" if judge.model.startswith("anthropic/") else "reasoning_effort"] = judge.effort
    elif accepts_temperature(judge.model.split("/", 1)[-1]):
        config["temperature"] = 0.0
    return config


def sample_record(sample: Any) -> Dict[str, Any]:
    """One ledger record from one Inspect sample: text, refusal or error."""
    rec: Dict[str, Any] = {"custom_id": str(sample.id)}
    if sample.error is not None:
        rec["error"] = str(sample.error.message)
        return rec
    out = sample.output
    usage = out.usage
    rec.update(text=out.completion or "", model=out.model, tokens_in=getattr(usage, "input_tokens", None),
               tokens_out=getattr(usage, "output_tokens", None))
    if out.stop_reason == "content_filter":
        rec["refusal"] = True
    return rec


class InspectBackend:
    name = "inspect"
    writes_files = True

    def __init__(self, model: Any = None):
        self.model = model  # an Inspect Model for tests; by default the spec's judge.model
        self._n = 0

    def submit(self, run: Any, items: List[Item]) -> str:
        self._n += 1
        handle = f"inspect-{datetime.now(timezone.utc):%Y%m%dT%H%M%S}-{self._n:02d}"
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
        from inspect_ai import Task
        from inspect_ai import eval as inspect_eval
        from inspect_ai.dataset import MemoryDataset, Sample
        from inspect_ai.solver import generate

        for h in handles:
            items = [tuple(x) for x in json.loads((run.io_dir / "api" / f"{h}.items.json").read_text())]
            done = {r["custom_id"] for r in self._records(run, h)}
            todo = [(c, a) for c, a in items if custom_id(c, a) not in done]
            if not todo:
                continue
            task = Task(dataset=MemoryDataset([Sample(id=custom_id(c, a), input=run.prompt(c)) for c, a in todo]),
                        solver=generate(), name=f"adele-{run.name}")
            log, = inspect_eval(task, model=self.model or run.judge.model, log_dir=str(run.io_dir / "inspect"),
                                display="none", fail_on_error=False, **generate_config(run.judge))
            with open(run.io_dir / "api" / f"{h}.jsonl", "a", encoding="utf-8") as out:
                for sample in log.samples or []:
                    out.write(json.dumps(sample_record(sample)) + "\n")
        return {h: "done" for h in handles}

    def fetch(self, run: Any, handle: str, items: List[Item]) -> List[Answer]:
        got: Dict[Item, Answer] = {}
        for r in self._records(run, handle):
            cell, attempt = parse_custom_id(r["custom_id"])
            if "error" in r:
                got[(cell, attempt)] = Answer(cell, attempt, None, reason="error")
            elif r.get("refusal"):
                got[(cell, attempt)] = Answer(cell, attempt, None, r["model"], reason="refusal")
            else:
                got[(cell, attempt)] = Answer(cell, attempt, r["text"], r["model"], tokens_in=r["tokens_in"],
                                              tokens_out=r["tokens_out"])
        return [got.get((c, a), Answer(c, a, None, reason="error")) for c, a in items]
