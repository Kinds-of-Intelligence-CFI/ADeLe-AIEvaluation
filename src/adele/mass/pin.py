"""Freeze a spec into an immutable run: cells, prompt hashes and a manifest of every input's hash.

A run directory (committed) holds ``manifest.json``, ``cells.csv`` and ``ledger.csv``. Prompt texts go to
``$ADELE_JUDGE_IO/<run>/prompts/<cell_id>.txt`` (outside the repo; default ``~/Developer/ADELE/judge-io``).
Pinning the same spec at the same inputs gives the same cells; pinning into an existing run refuses unless
everything frozen is identical, in which case it only rewrites missing prompt files (e.g. on another machine).
"""

import csv
import hashlib
import io
import json
import os
import subprocess
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd

from adele.mass.spec import BUILDERS, REPO_ROOT, JudgeSpec, Spec, SpecError, build_prompt, resolve_rubrics

RUNS_ROOT = REPO_ROOT / "experiments" / "benchmarks" / "mass-annotation" / "runs"
CELL_COLUMNS = ["cell_id", "benchmark", "instance_id", "rubric_ref", "generation", "code", "repeat", "prompt_sha256"]
PROMPTS_FILE = REPO_ROOT / "src" / "adele" / "annotation" / "prompts.py"


def sha256(data: bytes | str) -> str:
    return hashlib.sha256(data.encode("utf-8") if isinstance(data, str) else data).hexdigest()


def judge_io_root() -> Path:
    """Where prompts and raw answers live: ``$ADELE_JUDGE_IO`` or ``~/Developer/ADELE/judge-io``."""
    return Path(os.environ.get("ADELE_JUDGE_IO", "~/Developer/ADELE/judge-io")).expanduser()


def cell_id(benchmark: str, instance_id: str, rubric_ref: str, repeat: int) -> str:
    """Stable id, safe for file names and batch custom_ids (``^[A-Za-z0-9_-]{1,64}$``), e.g. ``v2PLp-1f0c…``."""
    gen, _, code = rubric_ref.partition("/")
    h = sha256("\x1f".join([benchmark, instance_id, rubric_ref, str(repeat)]))[:16]
    return f"{gen}{code}-{h}"


@dataclass
class Run:
    """A pinned run as loaded from its directory."""
    dir: Path
    manifest: Dict[str, Any]
    cells: pd.DataFrame

    @property
    def name(self) -> str:
        return self.manifest["run"]

    @property
    def judge(self) -> JudgeSpec:
        return JudgeSpec(**self.manifest["frozen"]["judge"])

    @property
    def io_dir(self) -> Path:
        return judge_io_root() / self.name

    def prompt_path(self, cell: str) -> Path:
        return self.io_dir / "prompts" / f"{cell}.txt"

    def response_path(self, cell: str, attempt: int) -> Path:
        """Answers of attempt 1 go to ``responses/<folder>/``, retries to ``responses/<folder>-a<n>/``."""
        folder = self.judge.folder if attempt == 1 else f"{self.judge.folder}-a{attempt}"
        return self.io_dir / "responses" / folder / f"{cell}.txt"

    def prompt(self, cell: str) -> str:
        """The prompt text, checked against the pinned hash. Read as bytes: text mode would turn the task
        texts' ``\\r\\n`` into ``\\n`` and break the hash."""
        path = self.prompt_path(cell)
        if not path.exists():
            raise FileNotFoundError(f"{path} missing: run `adele mass pin <spec>` on this machine to write prompts")
        data = path.read_bytes()
        if sha256(data) != self.cells.loc[cell, "prompt_sha256"]:
            raise ValueError(f"{path} does not match its pinned sha256")
        return data.decode("utf-8")


def load_run(path: str | Path) -> Run:
    """Load a run from a directory, or by name under the default runs root."""
    p = Path(path)
    if not (p / "manifest.json").exists():
        p = RUNS_ROOT / str(path)
    if not (p / "manifest.json").exists():
        raise FileNotFoundError(f"no run at {path} (nor under {RUNS_ROOT})")
    manifest = json.loads((p / "manifest.json").read_text())
    cells = pd.read_csv(p / "cells.csv", dtype=str, keep_default_na=False)
    cells["repeat"] = cells["repeat"].astype(int)
    return Run(dir=p, manifest=manifest, cells=cells.set_index("cell_id", drop=False))


def _git(*args: str) -> Optional[str]:
    try:
        return subprocess.run(["git", "-C", str(REPO_ROOT), *args], capture_output=True, text=True,
                              check=True).stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def _rel(path: Path) -> str:
    """Repo-relative if inside the repo, else ~/-relative if under home (no personal paths in committed runs)."""
    p = Path(path).resolve()
    for base, prefix in ((REPO_ROOT, ""), (Path.home().resolve(), "~/")):
        try:
            return prefix + str(p.relative_to(base))
        except ValueError:
            pass
    return str(path)


def load_instances(spec: Spec) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """The selected instances (benchmark, instance_id, prompt) and their provenance for the manifest.

    Each benchmark's frame must still match the sha256 recorded in ``INSTANCES.tsv``.
    """
    from adele.instances import MANIFEST_NAME, _frame_sha256

    index_path = spec.instances_dir / MANIFEST_NAME
    if not index_path.exists():
        raise SpecError(f"{index_path} not found: freeze instances first (`adele instances prepare`)")
    index = pd.read_csv(index_path, sep="\t").set_index("benchmark")
    frames, info = [], {}
    for b in spec.benchmarks:
        if b not in index.index:
            raise SpecError(f"benchmark {b!r} is not in {index_path} (known: {sorted(index.index)})")
        f = spec.instances_dir / index.loc[b, "file"]
        df = pd.read_parquet(f) if f.suffix == ".parquet" else pd.read_csv(f, dtype={"instance_id": str})
        df["instance_id"] = df["instance_id"].astype(str)
        if _frame_sha256(df) != index.loc[b, "sha256"]:
            raise SpecError(f"{f} no longer matches its sha256 in {MANIFEST_NAME}")
        frames.append(df[["benchmark", "instance_id", "prompt"]])
        info[b] = {"file": f.name, "file_sha256": sha256(f.read_bytes()), "frame_sha256": index.loc[b, "sha256"]}
    inst = pd.concat(frames, ignore_index=True)
    subset_info = None
    if spec.subset is not None:
        sub = pd.read_csv(spec.subset, dtype={"instance_id": str})
        if "instance_id" not in sub.columns:
            raise SpecError(f"{spec.subset} has no instance_id column")
        if "keep" in sub.columns:
            keep = sub["keep"].map(lambda v: str(v).strip().lower() in ("true", "1"))
            sub = sub[keep]
        keys = ["benchmark", "instance_id"] if "benchmark" in sub.columns else ["instance_id"]
        wanted = set(map(tuple, sub[keys].astype(str).values))
        have = set(map(tuple, inst[keys].values))
        missing = wanted - have
        if missing:
            raise SpecError(f"{len(missing)} subset ids are not in the benchmarks' instances, e.g. "
                            f"{sorted(missing)[:3]}")
        inst = inst[[k in wanted for k in map(tuple, inst[keys].values)]]
        subset_info = {"file": _rel(spec.subset), "sha256": sha256(spec.subset.read_bytes()), "n_ids": len(wanted)}
    for b in spec.benchmarks:
        info[b]["n_selected"] = int((inst["benchmark"] == b).sum())
    inst = inst.sort_values(["benchmark", "instance_id"]).reset_index(drop=True)
    return inst, {"benchmarks": info, "subset": subset_info}


def plan_cells(spec: Spec) -> Tuple[List[Dict[str, Any]], Dict[str, str], Dict[str, Any]]:
    """Every cell of the spec, the prompt text per cell id, and the frozen provenance (no side effects)."""
    rubrics = resolve_rubrics(spec.refs)
    if any(r.generation == "v2" for r in rubrics):
        from adele.agentic import verify_manifest
        codes = {r.code for r in rubrics if r.generation == "v2"}
        drift = [p for p in verify_manifest() if p.split(":")[0] in codes]
        if drift:
            raise SpecError(f"v2 rubric manifest drift: {drift}")
    inst, inst_info = load_instances(spec)
    cells, prompts = [], {}
    for row in inst.itertuples(index=False):
        for r in rubrics:
            text = build_prompt(spec.builder, r, row.prompt)
            for rep in range(1, spec.judge.repeats + 1):
                cid = cell_id(row.benchmark, row.instance_id, r.ref, rep)
                if cid in prompts:
                    raise SpecError(f"cell id collision: {cid}")
                prompts[cid] = text
                cells.append({"cell_id": cid, "benchmark": row.benchmark, "instance_id": row.instance_id,
                              "rubric_ref": r.ref, "generation": r.generation, "code": r.code, "repeat": rep,
                              "prompt_sha256": sha256(text)})
    frozen = {
        "spec": {"sha256": sha256(spec.text), "content": spec.text},
        "tasks": inst_info,
        "rubrics": {r.ref: {"file": _rel(Path(r.file_path)), "sha256": sha256(Path(r.file_path).read_bytes()),
                            "full_name": r.full_name} for r in rubrics},
        "prompt": {"builder": spec.builder, "function": f"adele.annotation.prompts.{BUILDERS[spec.builder]}",
                   "source_file": _rel(PROMPTS_FILE), "source_sha256": sha256(PROMPTS_FILE.read_bytes())},
        "judge": asdict(spec.judge),
    }
    return cells, prompts, frozen


# USD per million tokens (input, output), standard API rates as of 2026-09-25; batch APIs charge half.
PRICES = {"claude-opus-5-5": (4.0, 20.0), "claude-sonnet-5-5": (2.0, 10.0), "claude-haiku-4-5": (1.0, 5.0)}
# Claude Code subscription cost of one Opus-low judge call, orchestration included (PLAN.md section 5).
WEEKLY_POINTS_PER_CALL = 0.005


def estimate(spec: Spec, tokens_out: int = 1500, usd_in: Optional[float] = None,
             usd_out: Optional[float] = None) -> Dict[str, Any]:
    """Size and rough cost of a spec, with no side effects. Input tokens are prompt characters / 4; output
    tokens (thinking included) are a per-call guess. Costs are None for models without a known price."""
    cells, prompts, _ = plan_cells(spec)
    df = pd.DataFrame(cells)
    tok_in = float(sum(len(prompts[c]) for c in df["cell_id"]) / 4.0)
    tok_out = float(tokens_out * len(df))
    p_in, p_out = (usd_in, usd_out) if usd_in is not None and usd_out is not None else \
        PRICES.get(spec.judge.model, (None, None))
    usd = None if p_in is None else tok_in / 1e6 * p_in + tok_out / 1e6 * p_out
    return {"cells": len(df), "by_benchmark": df.groupby("benchmark").size().to_dict(),
            "rubrics": len(spec.refs), "tokens_in": tok_in, "tokens_out": tok_out,
            "usd": {"litellm (standard)": usd, "anthropic-batch / openai-batch (50%)": None if usd is None else usd / 2},
            "subagent_weekly_points": len(df) * WEEKLY_POINTS_PER_CALL,
            "max_prompt_chars": int(max(len(p) for p in prompts.values()))}


def _cells_csv(cells: List[Dict[str, Any]]) -> str:
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=CELL_COLUMNS, lineterminator="\n")
    w.writeheader()
    w.writerows(cells)
    return buf.getvalue()


def agents_dir() -> Path:
    """Where the Claude Code judge agents live: ``$ADELE_AGENTS_DIR`` or ``~/Developer/ADELE/.claude/agents``."""
    return Path(os.environ.get("ADELE_AGENTS_DIR", "~/Developer/ADELE/.claude/agents")).expanduser()


def agent_drift(run: Run) -> List[str]:
    """Dispatcher or judge agent files whose sha256 differs from the one recorded at pin (subagent runs)."""
    if run.judge.backend != "subagent":
        return []
    pinned = run.manifest.get("judge_agents") or {}
    now = _agent_files(run.judge)
    return sorted(name for name in now if (pinned.get(name) or {}).get("sha256") != now[name]["sha256"])


def _agent_files(judge: JudgeSpec) -> Dict[str, Any]:
    agents = agents_dir()
    out = {}
    for key in ("dispatcher", "judge_agent"):
        f = agents / f"{judge.relay[key]}.md"
        out[judge.relay[key]] = {"file": _rel(f), "sha256": sha256(f.read_bytes()) if f.exists() else None}
    return out


def _write_prompts(run_io: Path, prompts: Dict[str, str]) -> int:
    d = run_io / "prompts"
    d.mkdir(parents=True, exist_ok=True)
    written = 0
    for cid, text in prompts.items():
        p = d / f"{cid}.txt"
        if p.exists():
            if sha256(p.read_bytes()) != sha256(text):
                raise SpecError(f"{p} exists with different content; refusing to overwrite")
            continue
        p.write_bytes(text.encode("utf-8"))
        written += 1
    return written


def pin(spec: Spec, runs_root: Optional[Path] = None) -> Tuple[Run, int]:
    """Create the run (or confirm an identical one); returns the run and the number of prompt files written."""
    from adele.mass.ledger import Ledger, run_lock

    run_dir = Path(runs_root or RUNS_ROOT) / spec.name
    cells, prompts, frozen = plan_cells(spec)
    run_dir.mkdir(parents=True, exist_ok=True)
    with run_lock(run_dir):
        return _pin_locked(spec, run_dir, cells, prompts, frozen)


def _pin_locked(spec: Spec, run_dir: Path, cells: List[Dict[str, Any]], prompts: Dict[str, str],
                frozen: Dict[str, Any]) -> Tuple[Run, int]:
    from adele.mass.ledger import Ledger

    cells_text = _cells_csv(cells)
    frozen["cells"] = {"n": len(cells), "sha256": sha256(cells_text)}
    if (run_dir / "manifest.json").exists():
        old = json.loads((run_dir / "manifest.json").read_text())
        if old["frozen"] != json.loads(json.dumps(frozen)):
            diff = sorted(k for k in frozen if old["frozen"].get(k) != json.loads(json.dumps(frozen[k])))
            raise SpecError(f"{run_dir} exists and was pinned from different inputs ({', '.join(diff)} differ); "
                            "give the spec a new name")
        run = load_run(run_dir)
        return run, _write_prompts(run.io_dir, prompts)
    manifest = {
        "run": spec.name,
        "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "spec_file": _rel(spec.path),
        "git": {"commit": _git("rev-parse", "HEAD"),
                "dirty_tracked_files": (_git("status", "--porcelain", "--untracked-files=no") or "").splitlines()},
        "judge_agents": _agent_files(spec.judge) if spec.judge.backend == "subagent" else None,
        "frozen": frozen,
    }
    # The manifest is written last: a folder without one is not a run, and a crash before it leaves
    # nothing that a later pin cannot overwrite.
    (run_dir / "ledger.csv").unlink(missing_ok=True)
    (run_dir / "cells.csv").write_text(cells_text, encoding="utf-8")
    Ledger.create(run_dir, [c["cell_id"] for c in cells], spec.judge.backend)
    (run_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    run = load_run(run_dir)
    return run, _write_prompts(run.io_dir, prompts)

