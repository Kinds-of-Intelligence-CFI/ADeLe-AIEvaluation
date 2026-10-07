"""Annotation-run specs: load and validate a TOML file that says what to annotate and with which judge.

A spec names benchmarks (slugs from ``data/instances/INSTANCES.tsv``), an optional subset of instance ids,
generation-qualified rubric refs (``v1/AT`` resolves against the bundled ``data_v1`` rubrics, ``v2/PLp`` against
the active v2 manifest, so ``v1/MSm`` and ``v2/MSm`` never collide), a prompt builder and a judge::

    name = "swebench-clean-v1"
    [tasks]
    benchmarks = ["swe-bench-verified"]
    subset = "experiments/benchmarks/swebench-clean/tasks.csv"   # instance_id (+ optional keep) column
    [rubrics]
    refs = ["v1/AT", "v2/MSm"]
    [prompt]
    builder = "v2-noreason"   # default judge setting since 2026-10-07 (noreason/RESULTS.md); "v2" adds written reasoning
    [judge]
    backend = "subagent"
    model = "claude-opus-5-5"
    effort = "low"
    repeats = 1
    retry = { fallback_writer = 1, unparsed = 1 }

Relative paths resolve against the repository root.
"""

import re
import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

REPO_ROOT = Path(__file__).resolve().parents[3]
BACKENDS = ("subagent", "anthropic-batch", "openai-batch", "litellm", "fake")
BUILDERS = {"v1": "build_annotation_prompt", "v2": "build_annotation_prompt_v2",
            "v2-noreason": "build_annotation_prompt_v2_noreason"}
# Why an attempt can be rejected; each reason has its own retry budget (extra attempts). ``protocol``: the
# subagent judge's transcript broke the protocol (see adele.mass.backends.subagent.transcript_problems).
REASONS = ("fallback_writer", "unparsed", "refusal", "error", "protocol")
SAFE_NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,63}$")
_KEYS = {
    "": {"name", "tasks", "rubrics", "prompt", "judge"},
    "tasks": {"benchmarks", "subset", "instances_dir"},
    "rubrics": {"refs"},
    "prompt": {"builder"},
    "judge": {"backend", "model", "effort", "repeats", "retry", "max_tokens", "folder", "relay"},
    "relay": {"dispatcher", "judge_agent", "model_alias", "batch_size", "cwd", "chunk_lines"},
}


class SpecError(ValueError):
    """A spec that cannot be run as written."""


@dataclass(frozen=True)
class RubricRef:
    """One resolved rubric: ``ref`` is generation-qualified (``v2/PLp``)."""
    ref: str
    generation: str
    code: str
    full_name: str
    content: str
    file_path: str


@dataclass(frozen=True)
class JudgeSpec:
    """Judge settings. ``relay`` holds the subagent-only settings (dispatcher, agents, batch size)."""
    backend: str
    model: str
    effort: Optional[str] = None
    repeats: int = 1
    retry: Dict[str, int] = field(default_factory=dict)
    max_tokens: int = 16000
    folder: str = ""
    relay: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class Spec:
    """A validated spec. ``text`` is the file as written (it is hashed into the run manifest)."""
    name: str
    benchmarks: List[str]
    subset: Optional[Path]
    instances_dir: Path
    refs: List[str]
    builder: str
    judge: JudgeSpec
    path: Path
    text: str


def _check_keys(table: Dict[str, Any], section: str) -> None:
    unknown = set(table) - _KEYS[section]
    if unknown:
        where = f"[{section}]" if section else "top level"
        raise SpecError(f"unknown key(s) {sorted(unknown)} at {where} (allowed: {sorted(_KEYS[section])})")


def _resolve_path(value: str, root: Path) -> Path:
    p = Path(value).expanduser()
    return p if p.is_absolute() else root / p


def judge_from_dict(d: Dict[str, Any], builder: str = "v2") -> JudgeSpec:
    """Validate a ``[judge]`` table and fill defaults (folder, relay settings, retry budgets)."""
    _check_keys(d, "judge")
    backend = d.get("backend")
    if backend not in BACKENDS:
        raise SpecError(f"judge.backend must be one of {list(BACKENDS)}, got {backend!r}")
    model = d.get("model")
    if not isinstance(model, str) or not model:
        raise SpecError("judge.model is required (the model whose answers count, e.g. 'claude-opus-5-5')")
    effort = d.get("effort")
    if effort is not None and not isinstance(effort, str):
        raise SpecError("judge.effort must be a string such as 'low'")
    repeats = d.get("repeats", 1)
    if not isinstance(repeats, int) or repeats < 1:
        raise SpecError("judge.repeats must be a positive integer")
    retry = dict(d.get("retry", {}))
    bad = set(retry) - set(REASONS)
    if bad:
        raise SpecError(f"judge.retry has unknown reason(s) {sorted(bad)} (allowed: {list(REASONS)})")
    if any(not isinstance(v, int) or v < 0 for v in retry.values()):
        raise SpecError("judge.retry values must be non-negative integers")
    retry = {r: retry.get(r, 1) for r in REASONS}
    relay = dict(d.get("relay", {}))
    _check_keys(relay, "relay")
    if backend == "subagent":
        if not effort:
            raise SpecError("judge.effort is required for the subagent backend (it picks the judge agent)")
        v = "v2-" if builder.startswith("v2") else ""
        relay.setdefault("dispatcher", f"judge-dispatcher-{v}{effort}")
        relay.setdefault("judge_agent", f"adele-judge-{v}{effort}")
        relay.setdefault("model_alias", model.split("-")[1] if model.startswith("claude-") else model)
        relay.setdefault("batch_size", 50)
        if not isinstance(relay["batch_size"], int) or relay["batch_size"] < 1:
            raise SpecError("judge.relay.batch_size must be a positive integer")
        if "chunk_lines" in relay and (not isinstance(relay["chunk_lines"], int) or relay["chunk_lines"] < 1):
            raise SpecError("judge.relay.chunk_lines must be a positive integer")
    elif relay:
        raise SpecError("[judge.relay] only applies to the subagent backend")
    short = relay.get("model_alias", model.replace("/", "-"))
    folder = d.get("folder") or (f"{short}-{effort}" if effort else short)
    if not SAFE_NAME.match(folder):
        raise SpecError(f"judge.folder {folder!r} is not a safe folder name")
    return JudgeSpec(backend=backend, model=model, effort=effort, repeats=repeats, retry=retry,
                     max_tokens=int(d.get("max_tokens", 16000)), folder=folder, relay=relay)


def load_spec(path: str | Path, root: Optional[Path] = None) -> Spec:
    """Parse and validate a spec file. Rubric refs are checked here, so a bad ref fails before any work."""
    path = Path(path)
    root = Path(root) if root is not None else REPO_ROOT
    text = path.read_text(encoding="utf-8")
    try:
        d = tomllib.loads(text)
    except tomllib.TOMLDecodeError as exc:
        raise SpecError(f"{path}: not valid TOML: {exc}") from exc
    _check_keys(d, "")
    for section in ("tasks", "rubrics", "prompt", "judge"):
        if not isinstance(d.get(section), dict):
            raise SpecError(f"{path}: missing [{section}] table")
        if section != "judge":
            _check_keys(d[section], section)
    name = d.get("name")
    if not isinstance(name, str) or not SAFE_NAME.match(name):
        raise SpecError(f"name must match {SAFE_NAME.pattern} (it names the run folder), got {name!r}")
    benchmarks = d["tasks"].get("benchmarks")
    if not benchmarks or not all(isinstance(b, str) for b in benchmarks) or len(set(benchmarks)) != len(benchmarks):
        raise SpecError("tasks.benchmarks must be a non-empty list of distinct benchmark slugs")
    subset = d["tasks"].get("subset")
    subset = _resolve_path(subset, root) if subset else None
    if subset is not None and not subset.is_file():
        raise SpecError(f"tasks.subset file not found: {subset}")
    instances_dir = _resolve_path(d["tasks"].get("instances_dir", "data/instances"), root)
    builder = d["prompt"].get("builder")
    if builder not in BUILDERS:
        raise SpecError(f"prompt.builder must be one of {list(BUILDERS)}, got {builder!r}")
    refs = d["rubrics"].get("refs")
    if not refs or not all(isinstance(r, str) for r in refs):
        raise SpecError("rubrics.refs must be a non-empty list like ['v1/AT', 'v2/PLp']")
    if len(set(refs)) != len(refs):
        raise SpecError(f"rubrics.refs has duplicates: {sorted({r for r in refs if refs.count(r) > 1})}")
    resolve_rubrics(refs)
    judge = judge_from_dict(d["judge"], builder)
    return Spec(name=name, benchmarks=list(benchmarks), subset=subset, instances_dir=instances_dir, refs=list(refs),
                builder=builder, judge=judge, path=path, text=text)


def resolve_rubrics(refs: List[str]) -> List[RubricRef]:
    """Resolve ``v1/<code>`` against the bundled v1 rubrics and ``v2/<code>`` against the active v2 manifest."""
    from adele.agentic import load_active_catalog
    from adele.rubrics.catalog import RubricsCatalog

    catalogs: Dict[str, Any] = {}
    out = []
    for ref in refs:
        gen, _, code = ref.partition("/")
        if gen not in ("v1", "v2") or not code:
            raise SpecError(f"rubric ref {ref!r} must look like 'v1/<code>' or 'v2/<code>'")
        if code == "UG_choice_num":
            raise SpecError("UG_choice_num is an answer-format classifier, not a 0-5 demand rubric; "
                            "UG is computed from the answer format, not judged")
        if gen not in catalogs:
            catalogs[gen] = RubricsCatalog() if gen == "v1" else load_active_catalog()
        rubric = catalogs[gen].get(code)
        if rubric is None:
            raise SpecError(f"unknown rubric ref {ref!r} (known {gen} codes: {', '.join(catalogs[gen].acronyms)})")
        if not re.fullmatch(r"[A-Za-z0-9]+", code):
            raise SpecError(f"rubric code {code!r} is not alphanumeric")
        out.append(RubricRef(ref=ref, generation=gen, code=code, full_name=rubric.full_name,
                             content=rubric.content, file_path=rubric.file_path))
    return out


def build_prompt(builder: str, rubric: RubricRef, task: str) -> str:
    """The judge prompt for one (rubric, task) with the named builder; the builders themselves are untouched."""
    from adele.annotation import prompts

    if builder == "v1":
        return prompts.build_annotation_prompt(demand_name=rubric.full_name, rubric_content=rubric.content,
                                               task_instance=task)
    if builder == "v2-noreason":
        return prompts.build_annotation_prompt_v2_noreason(rubric.full_name, rubric.content, task)
    return prompts.build_annotation_prompt_v2(rubric.full_name, rubric.content, task)
