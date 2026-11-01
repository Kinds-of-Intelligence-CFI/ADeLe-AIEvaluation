"""Write the judge prompts, sample and run manifests for the tau2-tb4-pl study.

Two runs, both judged by Opus at low effort (swebench-pl's adele-judge-low.md) on PLp, PLe, PLs:
  tau2pl-r1  the verifiably solvable tau2 tasks of airline, retail and banking_knowledge (232)
  tb4pl-r1   all 66 Terminal-Bench 4.0.0 tasks (the 34 verifiably solvable: the analysis set)
Prompts use swebench-pl's builder, rubric files and judge agent, checked against its run
swepl-r1-low. The task text is the frozen instance, without Terminal-Bench's canary comment lines.
sample.csv freezes each task's outcome data before any label (PREREGISTRATION.md, Outcomes).
Task text goes to the gitignored data/annotations/<run>/prompts/ and, for the judges, to
JUDGE_IO/<run>/prompts/. sample.csv, the indexes (hashes) and run.json are committed.

    python experiments/benchmarks/panel/build.py            # data/results/panel.parquet
    python experiments/benchmarks/tau2-tb4-pl/make_prompts.py
"""

import hashlib
import json
import os
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from adele.agentic import load_active_catalog
from adele.annotation.prompts import build_annotation_prompt

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PANEL = HERE.parent / "panel"
SWEPL = HERE.parent / "swebench-pl"
DIMS = ["PLp", "PLe", "PLs"]
TAU2 = ["airline", "retail", "banking_knowledge"]
TB4 = "terminal-bench-4.0.0"
JUDGE_AGENT = SWEPL / "adele-judge-low.md"
JUDGES = {
    "opus-low": "Claude Code subagent 'adele-judge-low' (tools: Read, Write; omitClaudeMd; "
                "effort low), model alias 'opus'",
}
# Sent verbatim to each judge subagent, one (task, dimension) per call.
JUDGE_INSTRUCTION = """Prompt file: {prompt_file}
Response file: {response_file}"""
# As in swebench-pl: judge files two levels above the repo, where no folder between the judging
# session's folder and the files has a CLAUDE.md.
JUDGE_IO = ROOT.parents[1] / "judge-io"
# Terminal-Bench instructions open with HTML comments that carry the benchmark's training-corpus
# canary; they are not part of the task.
CANARY_LINE = re.compile(r"<!--[^\n]*(harbor-canary|TRAINING CORPORA)[^\n]*-->[ \t]*\n?")


def sha256(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def git(*args: str) -> str:
    return subprocess.run(["git", "-C", str(ROOT), *args], capture_output=True,
                          text=True, check=True).stdout.strip()


def strip_canary(text: str) -> str:
    out = CANARY_LINE.sub("", text).lstrip("\n")
    assert "harbor-canary" not in out and "TRAINING CORPORA" not in out
    return out


def outcomes(panel: pd.DataFrame, benchmark: str, ids: list[str], analysis_ids: list[str]) -> pd.DataFrame:
    """Solve rates on the frozen text (panel rules 1 and 3): over the configurations that ran
    every analysis-set task with scored trials, and over every configuration (suffix _all)."""
    use = panel[(panel["benchmark"] == benchmark) & panel["text_matches_frozen"] & (panel["n_trials"] > 0)]
    use = use.assign(solved=use["success"] * use["n_trials"])
    cover = use[use["instance_id"].isin(analysis_ids)].groupby("config")["instance_id"].nunique()
    common = cover[cover == len(analysis_ids)].index

    def rate(df: pd.DataFrame) -> pd.DataFrame:
        g = df[df["instance_id"].isin(ids)].groupby("instance_id")
        return pd.DataFrame({"solve_rate": (g["solved"].sum() / g["n_trials"].sum()).round(4),
                             "n_configs": g["config"].nunique()})

    return pd.concat([rate(use[use["config"].isin(common)]), rate(use).add_suffix("_all")], axis=1)


def build_sample() -> tuple[pd.DataFrame, dict[str, str]]:
    tasks = pd.read_csv(PANEL / "tasks.csv", dtype={"instance_id": str})
    panel = pd.read_parquet(ROOT / "data/results/panel.parquet")
    frames, text = [], {}
    for bench in [f"tau2-{d}" for d in TAU2] + [TB4]:
        t = tasks[tasks["benchmark"] == bench].set_index("instance_id")
        if bench == TB4:
            inst = pd.read_parquet(ROOT / f"data/instances/instances_{bench}.parquet")
            ids = sorted(t.index)
            meta = pd.read_csv(ROOT / f"data/instances/meta_{bench}.csv").set_index("instance_id")
        else:
            inst = pd.read_csv(ROOT / f"data/instances/instances_{bench}.csv", dtype={"instance_id": str})
            ids = sorted(t.index[t["verifiably_solvable"]])
        inst = inst.set_index("instance_id").loc[ids]
        assert (inst["prompt_sha12"] == t.loc[ids, "prompt_sha12"]).all(), f"{bench}: frozen text differs from panel"
        analysis = sorted(t.index[t["verifiably_solvable"]])
        s = outcomes(panel, bench, ids, analysis).loc[ids]
        assert (s["solve_rate_all"] - t.loc[ids, "solve_rate"]).abs().max() < 1e-3
        s.insert(0, "benchmark", bench)
        s["analysis_set"] = s.index.isin(analysis)
        s["file_id"] = s.index if bench == TB4 else f"{bench.removeprefix('tau2-')}-" + s.index
        s["run"] = "tb4pl-r1" if bench == TB4 else "tau2pl-r1"
        if bench == TB4:
            s["expert_hours"] = t.loc[ids, "expert_hours"]
            s["category"] = t.loc[ids, "category"]
            s["epoch_defect"] = meta.loc[ids, "epoch_defect"].fillna("")
        for iid, fid in zip(ids, s["file_id"]):
            text[fid] = strip_canary(inst.loc[iid, "prompt"]) if bench == TB4 else inst.loc[iid, "prompt"]
        frames.append(s.rename_axis("instance_id").reset_index())
    sample = pd.concat(frames, ignore_index=True)
    cols = ["benchmark", "instance_id", "file_id", "run", "analysis_set", "solve_rate", "n_configs",
            "solve_rate_all", "n_configs_all", "expert_hours", "category", "epoch_defect"]
    return sample[cols], text


def write_run(run_id: str, sample: pd.DataFrame, rubrics, text: dict[str, str], info: dict) -> pd.DataFrame:
    data_dir, io, labels = ROOT / "data/annotations" / run_id, JUDGE_IO / run_id, HERE / "labels" / run_id
    for d in (data_dir / "prompts", io / "prompts", labels):
        d.mkdir(parents=True, exist_ok=True)
    for judge in JUDGES:
        (io / "responses" / judge).mkdir(parents=True, exist_ok=True)

    index = []
    for r in sample.itertuples(index=False):
        for dim in DIMS:
            rb = rubrics[dim]
            prompt = build_annotation_prompt(demand_name=rb.full_name, rubric_content=rb.content,
                                             task_instance=text[r.file_id])
            for d in (data_dir, io):
                (d / "prompts" / f"{r.file_id}@{dim}.txt").write_text(prompt, encoding="utf-8")
            index.append({"benchmark": r.benchmark, "instance_id": r.instance_id, "file_id": r.file_id,
                          "demand": dim, "family": "v2",
                          "rubric_sha256": sha256(Path(rb.file_path).read_bytes()),
                          "prompt_sha256": sha256(prompt.encode("utf-8"))})
    index = pd.DataFrame(index)
    index.to_csv(labels / "prompts_index.csv", index=False)

    run = {
        "run_id": run_id,
        "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "repo_commit": git("rev-parse", "HEAD"),
        "repo_dirty_tracked_files": git("status", "--porcelain", "--untracked-files=no").splitlines(),
        **info,
        "sample": {"file": "sample.csv", "rows": f"run == {run_id!r}"},
        "design": {"n_tasks": len(sample), "dims": DIMS, "n_prompts": len(index), "judges": JUDGES},
        "rubrics": {d: {"name": rubrics[d].full_name,
                        "file": str(Path(rubrics[d].file_path).relative_to(ROOT)),
                        "sha256": sha256(Path(rubrics[d].file_path).read_bytes())} for d in DIMS},
        "prompt": {
            "builder": "adele.annotation.prompts.build_annotation_prompt",
            "builder_file_sha256": sha256((ROOT / "src/adele/annotation/prompts.py").read_bytes()),
        },
        "judge_agent": {"file": str(JUDGE_AGENT.relative_to(ROOT)), "sha256": sha256(JUDGE_AGENT.read_bytes())},
        "judge_instruction": JUDGE_INSTRUCTION,
        "judge_instruction_sha256": sha256(JUDGE_INSTRUCTION.encode("utf-8")),
        "judge_io": os.path.relpath(io, ROOT),
        "sampling": "harness defaults; snapshot cannot be pinned for subagents; effort is set in the agent file",
    }
    for d in (labels, data_dir):
        (d / "run.json").write_text(json.dumps(run, indent=2) + "\n")
    print(f"{run_id}: {len(sample)} tasks, {len(index)} prompts → {io / 'prompts'}")
    return index


def check_same_setup(run_id: str) -> None:
    """Rubric files, builder, judge agent and judge message as in swebench-pl's swepl-r1-low."""
    ref = json.loads((SWEPL / "labels/swepl-r1-low/run.json").read_text())
    run = json.loads((HERE / f"labels/{run_id}/run.json").read_text())
    for key in ("rubrics", "prompt", "judge_agent", "judge_instruction_sha256"):
        assert run[key] == ref[key], f"{run_id}: {key} differs from swepl-r1-low"


def main() -> None:
    sample, text = build_sample()
    sample.to_csv(HERE / "sample.csv", index=False)
    manifest = pd.read_csv(ROOT / "data/instances/INSTANCES.tsv", sep="\t").set_index("benchmark")
    rubrics = load_active_catalog()
    outcome_note = ("data/results/panel.parquet (experiments/benchmarks/panel/build.py); solve rate = share of "
                    "scored trials with reward 1 on the frozen text, over the configurations that ran every "
                    "analysis-set task of the benchmark (tau2: per domain) with scored trials; "
                    "solve_rate_all over every configuration")
    runs = {
        "tau2pl-r1": {
            "benchmark": "tau2 (airline, retail, banking_knowledge)",
            "instances": {
                "source": "sierra-research/tau2-bench data/tau2/domains/<domain>/tasks.json (loader taubench)",
                "task_text": "the user scenario rendered by adele.agentic.benchmarks._taubench_prompt",
                "frozen_file_sha256": {f"tau2-{d}": manifest.loc[f"tau2-{d}", "sha256"] for d in TAU2},
            },
            "outcomes": {"source": outcome_note, "tasks": "verifiably solvable (panel rule 4)"},
        },
        "tb4pl-r1": {
            "benchmark": TB4,
            "instances": {
                "source": "harborframework/terminal-bench (HF) tag v4.0.0, tasks/*/instruction.md (loader terminalbench4)",
                "task_text": "instruction.md without the HTML comment lines carrying the canary",
                "frozen_file_sha256": manifest.loc[TB4, "sha256"],
            },
            "outcomes": {"source": outcome_note + "; expert_hours = task.toml expert_time_estimate_hours",
                         "tasks": "all 66; analysis set = the 34 verifiably solvable (panel rule 4)"},
        },
    }
    for run_id, info in runs.items():
        write_run(run_id, sample[sample["run"] == run_id], rubrics, text, info)
        check_same_setup(run_id)
    print(sample.groupby("benchmark").agg(tasks=("instance_id", "size"), analysis_set=("analysis_set", "sum"),
                                          configs=("n_configs", "min"), configs_all=("n_configs_all", "max")))


if __name__ == "__main__":
    main()
