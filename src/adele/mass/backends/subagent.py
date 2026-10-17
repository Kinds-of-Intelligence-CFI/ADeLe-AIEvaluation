"""Claude Code subagent backend: relay batches for ``judge-dispatcher-*`` and writer attribution from transcripts.

``submit`` writes one relay message (the text a Claude Code session passes verbatim to the dispatcher agent) to
``<io>/relays/<handle>.txt``. The dispatcher starts one judge per cell with the two-line instruction
``Prompt file: <io>/prompts/<cell>.txt`` / ``Response file: <io>/responses/<folder>/<cell>.txt``, and the judge
saves its answer there. ``fetch`` reads those files and attributes each one to the model that wrote it, by matching
the file's SHA-256 to a Write call in the judge transcripts Claude Code keeps
(``~/.claude/projects/<project>/<session>/subagents``). A safety classifier can stop the registered judge and
Claude Code may finish the call with another model; such answers are rejected as ``fallback_writer`` later on.
"""

import hashlib
import json
import os
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from adele.mass.backends import Answer, Item

# Opus stops mid-answer and may recover; Sonnet 5.5 ends the call with an API error and no answer.
STOPS = ("stopped by a safety classifier", "safeguards flagged this message")
INSTRUCTION = "Prompt file: {prompt}\nResponse file: {response}"
_PATHS = re.compile(r"Prompt file: (\S+)\s*\n\s*Response file: (\S+)")
_CREATED = "File created successfully at: "
_LINE_NO = re.compile(r"^(\d+)\t", re.M)  # the Read tool numbers each returned line "<n>\t"
READ_MAX_LINE = 2000  # the Read tool cuts longer lines
DEFAULT_CWD = "~/Developer/ADELE"
FORBIDDEN_ATTACHMENTS = {"nested_memory", "instructions"}


@dataclass
class Transcript:
    """The facts of one judge transcript that attribution and the protocol checks need."""
    path: Path
    first: str
    prompt_path: str
    response_path: str
    cwd: Optional[str] = None
    agent_type: Optional[str] = None
    models: Set[str] = field(default_factory=set)
    efforts: Set[str] = field(default_factory=set)
    tools: List[Tuple[str, Dict[str, Any]]] = field(default_factory=list)
    tool_ids: List[Optional[str]] = field(default_factory=list)
    results: Dict[str, Tuple[bool, str]] = field(default_factory=dict)  # tool_use id -> (is_error, text)
    writes: List[Tuple[str, Optional[str], str, str]] = field(default_factory=list)  # ts, model, file, sha256
    created: List[str] = field(default_factory=list)
    attachments: Set[str] = field(default_factory=set)
    stopped: bool = False


def _text(content: Any) -> str:
    if isinstance(content, str):
        return content
    return "".join(b.get("text", "") for b in content or [] if isinstance(b, dict))


def scan_transcripts(directory: Path, io_dir: Path) -> List[Transcript]:
    """Every judge transcript under ``directory`` whose first message points at ``io_dir``'s prompts."""
    marker = f"{io_dir}/prompts/"
    out = []
    for f in sorted(Path(directory).rglob("agent-*.jsonl")):
        with open(f, encoding="utf-8") as fh:
            head = fh.readline()
            if marker not in head:
                continue
            lines = [head] + fh.readlines()
        first_rec = json.loads(lines[0])
        first = _text(first_rec.get("message", {}).get("content"))
        m = _PATHS.search(first)
        if not m:
            continue
        t = Transcript(path=f, first=first, prompt_path=m.group(1), response_path=m.group(2),
                       cwd=first_rec.get("cwd"))
        meta = f.with_suffix(".meta.json")
        if meta.exists():
            t.agent_type = json.loads(meta.read_text()).get("agentType")
        for line in lines:
            r = json.loads(line)
            t.stopped |= any(s in line for s in STOPS)
            if r.get("type") == "attachment":
                t.attachments.add(r.get("attachment", {}).get("type"))
            elif r.get("type") == "user":
                if _CREATED in line:
                    t.created.append(os.path.normpath(line.split(_CREATED)[1].split(" ")[0]))
                content = r.get("message", {}).get("content")
                for b in content if isinstance(content, list) else []:
                    if isinstance(b, dict) and b.get("type") == "tool_result" and b.get("tool_use_id"):
                        t.results[b["tool_use_id"]] = (bool(b.get("is_error")), _text(b.get("content")))
            elif r.get("type") == "assistant":
                model = r["message"].get("model")
                if model and model != "<synthetic>":
                    t.models.add(model)
                if r.get("perTurnEffort"):
                    t.efforts.add(r["perTurnEffort"])
                for b in r["message"].get("content", []):
                    if isinstance(b, dict) and b.get("type") == "tool_use":
                        inp = dict(b.get("input", {}))
                        if "file_path" in inp:  # a judge may write "prompts/../responses/x.txt" for the same file
                            inp["file_path"] = os.path.normpath(inp["file_path"])
                        t.tools.append((b.get("name"), inp))
                        t.tool_ids.append(b.get("id"))
                        if b.get("name") == "Write" and "content" in b.get("input", {}):
                            digest = hashlib.sha256(b["input"]["content"].encode("utf-8")).hexdigest()
                            t.writes.append((r.get("timestamp") or "", model, inp.get("file_path", ""), digest))
        out.append(t)
    return out


def attribute_writer(transcripts: List[Transcript], path: Path, digest: str) -> Optional[str]:
    """The model whose Write call produced this exact file; else the single model of the one transcript whose
    harness confirmed creating it while its Write record is missing (a Write record with other content means
    the file changed afterwards); else None."""
    p = str(path)
    hits = [(ts, model) for t in transcripts for ts, model, fp, h in t.writes if fp == p and h == digest]
    if hits:
        return max(hits, key=lambda x: x[0])[1]
    confirmed = [t for t in transcripts if p in t.created and len(t.models) == 1
                 and not any(fp == p for _, _, fp, _ in t.writes)]
    return next(iter(confirmed[0].models)) if len(confirmed) == 1 else None


def expected_cwd(run: Any, cwd: Optional[str] = None) -> str:
    """The directory the judges must run in: ``cwd``, else the spec's ``relay.cwd``, else ``~/Developer/ADELE``."""
    return str(Path(cwd or run.judge.relay.get("cwd") or DEFAULT_CWD).expanduser())


def transcript_problems(run: Any, t: Transcript, cwd: str) -> List[str]:
    """Protocol problems of one judge transcript (empty when it followed the protocol): the first message is
    exactly the two-line instruction for a cell of the run; the working directory is ``cwd``; the judge read
    its prompt file then wrote its response file and did nothing else (``SubagentHandback`` aside); no
    CLAUDE.md or memory was attached; effort and agent are the spec's. With ``relay.chunk_lines`` (prompts too
    long for one Read) the judge may Read its prompt several times, but the Read results must together return
    every line of the prompt file, and no line may be longer than the Read tool returns whole."""
    judge, problems = run.judge, []
    cell = Path(t.prompt_path).stem
    if cell not in run.cells.index or t.prompt_path != str(run.prompt_path(cell)):
        problems.append("prompt file is not a cell of this run")
    elif Path(t.response_path).name != f"{cell}.txt" or Path(t.response_path).parent.parent != run.io_dir / "responses":
        problems.append("response file does not belong to the cell")
    if t.first != INSTRUCTION.format(prompt=t.prompt_path, response=t.response_path):
        problems.append("first message is not exactly the two-line instruction")
    if t.cwd != cwd:
        problems.append(f"cwd {t.cwd!r} != {cwd!r}")
    chunked = bool(judge.relay.get("chunk_lines"))
    tools = [(n, i.get("file_path")) for n, i in t.tools if n != "SubagentHandback"]
    reads = next((k for k, x in enumerate(tools) if x != ("Read", t.prompt_path)), len(tools))
    if t.response_path in t.created and reads and reads == len(tools):
        tools.append(("Write", t.response_path))  # the Write record is missing; the harness confirmed it
    if not ((reads >= 1 if chunked else reads == 1) and tools[reads:] == [("Write", t.response_path)]):
        problems.append(f"tool calls {[n for n, _ in tools]} are not Read(prompt) then Write(response)"
                        + (" (Read may repeat)" if chunked else ""))
    elif chunked:
        problems += _unread(t)
    bad = t.attachments & FORBIDDEN_ATTACHMENTS
    if bad:
        problems.append(f"attachments {sorted(bad)} (CLAUDE.md or memory) present")
    if judge.effort and t.efforts - {judge.effort}:
        problems.append(f"effort {sorted(t.efforts)} != {judge.effort!r}")
    if t.agent_type and t.agent_type != judge.relay.get("judge_agent"):
        problems.append(f"agent {t.agent_type!r} != {judge.relay.get('judge_agent')!r}")
    return problems


def _unread(t: Transcript) -> List[str]:
    """Chunked reads: prompt lines that no successful Read of the prompt returned, and lines too long to return."""
    text = Path(t.prompt_path).read_text(encoding="utf-8")
    lines = text.split("\n")
    if lines and lines[-1] == "":
        lines.pop()
    seen: Set[int] = set()
    for (name, inp), tid in zip(t.tools, t.tool_ids):
        if name == "Read" and inp.get("file_path") == t.prompt_path and tid in t.results and not t.results[tid][0]:
            seen.update(int(n) for n in _LINE_NO.findall(t.results[tid][1]))
    out = []
    missing = set(range(1, len(lines) + 1)) - seen
    if missing:
        out.append(f"{len(missing)} of {len(lines)} prompt lines not returned by any Read (first: {min(missing)})")
    long = sum(len(x.rstrip("\r")) > READ_MAX_LINE for x in lines)
    if long:
        out.append(f"{long} prompt lines longer than {READ_MAX_LINE} characters")
    return out


class SubagentBackend:
    """``relays_done`` must be True for ``poll`` to treat relays as finished: only the session that launched
    them knows. ``transcripts`` is the session's ``subagents`` folder, needed by ``fetch``; ``cwd`` overrides
    the judges' expected working directory."""
    name = "subagent"
    writes_files = False

    def __init__(self, transcripts: Optional[Path] = None, relays_done: bool = False, cwd: Optional[str] = None):
        self.transcripts = Path(transcripts).expanduser() if transcripts else None
        self.relays_done = relays_done
        self.cwd = cwd
        self._scanned: Optional[List[Transcript]] = None
        self._n = 0

    def message(self, run: Any, items: List[Item]) -> str:
        """The relay message for judge-dispatcher (Model / I/O folder / Judge folder name / Cells)."""
        folder = run.response_path(items[0][0], items[0][1]).parent.name
        lines = [f"Model: {run.judge.relay['model_alias']}", f"I/O folder: {run.io_dir}",
                 f"Judge folder name: {folder}", f"Cells ({len(items)}):"]
        return "\n".join(lines + [cell for cell, _ in items])

    def submit(self, run: Any, items: List[Item]) -> str:
        if len({a for _, a in items}) != 1:
            raise ValueError("a relay carries cells of one attempt only (one judge folder)")
        for cell, _ in items:
            run.prompt(cell)
        self._n += 1
        handle = f"relay-{datetime.now(timezone.utc):%Y%m%dT%H%M%S}-{self._n:02d}"
        relays = run.io_dir / "relays"
        relays.mkdir(parents=True, exist_ok=True)
        run.response_path(*items[0]).parent.mkdir(parents=True, exist_ok=True)
        (relays / f"{handle}.txt").write_text(self.message(run, items), encoding="utf-8")
        return handle

    def poll(self, run: Any, handles: List[str]) -> Dict[str, str]:
        return {h: "done" if self.relays_done else "running" for h in handles}

    def scanned(self, run: Any) -> List[Transcript]:
        if self.transcripts is None:
            raise ValueError("the subagent backend needs --transcripts (the session's subagents folder)")
        if self._scanned is None:
            self._scanned = scan_transcripts(self.transcripts, run.io_dir)
        return self._scanned

    def fetch(self, run: Any, handle: str, items: List[Item]) -> List[Answer]:
        """Fails loudly, changing nothing, when an answer file cannot be traced to a judge transcript: a wrong
        ``transcripts`` folder must not turn good answers into rejections or unsent cells into relaunches.
        Each answer carries its protocol verdict: ``ok``, or the problems of its transcript(s), including a cell
        judged more than once."""
        transcripts = self.scanned(run)
        if not transcripts:
            raise ValueError(f"no judge transcripts for run {run.name} under {self.transcripts}: "
                             "is this the session that launched the relays?")
        by_response: Dict[str, List[Transcript]] = {}
        for t in transcripts:
            by_response.setdefault(t.response_path, []).append(t)
        cwd = expected_cwd(run, self.cwd)
        out, unattributed = [], []
        for cell, attempt in items:
            path = run.response_path(cell, attempt)
            if path.exists():
                data = path.read_bytes()
                writer = attribute_writer(transcripts, path, hashlib.sha256(data).hexdigest())
                if writer is None:
                    unattributed.append(str(path))
                ts = by_response.get(str(path), [])
                problems = [f"judged {len(ts)} times"] if len(ts) > 1 else \
                    [] if ts else ["no judge transcript was instructed to write this file"]
                for t in ts:
                    problems += transcript_problems(run, t, cwd)
                out.append(Answer(cell, attempt, data.decode("utf-8"), writer,
                                  protocol="; ".join(problems) or "ok"))
            else:
                out.append(Answer(cell, attempt, None, reason="error" if str(path) in by_response else "not_sent"))
        if unattributed:
            raise ValueError(f"{len(unattributed)} answer files match no Write call or harness confirmation in "
                             f"{self.transcripts}, e.g. {unattributed[:3]}")
        return out
