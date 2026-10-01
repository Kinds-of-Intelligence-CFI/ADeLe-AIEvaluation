"""Judge backends: one small interface for Claude Code subagents, batch APIs, litellm and a test fake.

A backend sends a group of (cell, attempt) items under one handle (a relay id or a batch id), says when a handle
is finished, and returns one :class:`Answer` per item. The runner records handles and answers in the ledger.
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Protocol, Tuple

Item = Tuple[str, int]  # (cell_id, attempt)


@dataclass
class Answer:
    """What a backend returns for one item.

    ``text`` is None when there is no answer; ``reason`` then says why (``refusal``, ``error``, or
    ``not_sent``: the item never reached the judge, so the attempt is not used up). ``protocol`` is set by the
    subagent backend: ``ok`` or the transcript's protocol problems.
    """
    cell_id: str
    attempt: int
    text: Optional[str]
    writer_model: Optional[str] = None
    reason: Optional[str] = None
    tokens_in: Optional[int] = None
    tokens_out: Optional[int] = None
    protocol: Optional[str] = None


class JudgeBackend(Protocol):
    """``writes_files``: True when the runner must save answer texts (API backends); a subagent judge saves its own."""
    name: str
    writes_files: bool

    def submit(self, run: Any, items: List[Item]) -> str: ...

    def poll(self, run: Any, handles: List[str]) -> Dict[str, str]: ...  # handle -> "running" | "done"

    def fetch(self, run: Any, handle: str, items: List[Item]) -> List[Answer]: ...


def accepts_temperature(model: str) -> bool:
    """OpenAI reasoning models (o1/o3/o4, gpt-5*) reject a non-default temperature."""
    from adele.annotation.prompts import is_reasoning_model

    return not is_reasoning_model(model) and not model.split("/", 1)[-1].startswith("gpt-5")


def custom_id(cell: str, attempt: int) -> str:
    """Batch request id for one attempt (cell ids are at most 22 chars, so this stays under 64)."""
    return f"{cell}-a{attempt}"


def parse_custom_id(cid: str) -> Item:
    cell, _, attempt = cid.rpartition("-a")
    return cell, int(attempt)


def get_backend(name: str, **kwargs: Any) -> JudgeBackend:
    """Instantiate a backend by its spec name. SDKs are imported only when a backend first needs them."""
    if name == "subagent":
        from adele.mass.backends.subagent import SubagentBackend
        return SubagentBackend(**kwargs)
    if name == "anthropic-batch":
        from adele.mass.backends.anthropic_batch import AnthropicBatchBackend
        return AnthropicBatchBackend(**kwargs)
    if name == "openai-batch":
        from adele.mass.backends.openai_batch import OpenAIBatchBackend
        return OpenAIBatchBackend(**kwargs)
    if name == "litellm":
        from adele.mass.backends.litellm_backend import LiteLLMBackend
        return LiteLLMBackend(**kwargs)
    if name == "fake":
        from adele.mass.backends.fake import FakeBackend
        return FakeBackend(**kwargs)
    raise ValueError(f"unknown backend {name!r}")
