"""ProgramBench per-task outcomes for every registered leaderboard run.

Sources (public, no login):
  github.com/ProgramBench/submissions at REGISTRY_COMMIT: the authoritative leaderboard
    registry. Per run: submission.yaml (model, provider, agent), pointer.yaml (public fork +
    scored commit), _stats/score.json ({instance_id: {"<branch>/<test>": passed}}, already
    filtered by the ProgramBench version used at packaging), cost/calls/tokens.json, and the
    registry-wide ignored_tests.json.
  github.com/ProgramBench/<run> at the pointer commit: per task, the light <iid>.eval.json
    (only its tail is read: error_code, test_branch_errors, warnings) and <iid>.traj.json
    (only its head is read: agent exit_status, mini version, prompt templates). HTTP range
    requests keep this to ~50 KB per run x task instead of ~10 GB of full files.
  github.com/facebookresearch/ProgramBench v1.2.5 tests.json, to re-apply the current
    ignore list (score_v125) on top of score.json.

The HF org ``programbench`` holds the same runs (one dataset per run) with the heavy
eval.log.json files (~55 GB in total); they are not needed for scores and are not downloaded.

Scoring (as the leaderboard): score = passed / kept tests for the task; resolved = score == 1;
near_resolved = score >= 0.95; tasks a run did not submit count as score 0 (denominator 200).

Writes, to experiments/benchmarks/panel/sources/programbench/ (ids, numbers, metadata only):
  leaderboard.csv      one row per run
  runs.csv             one row per run x task (all 200 tasks per run; plain CSV, ~1.2 MB, tracked)
  task_summary.csv     one row per task across runs

Run: python experiments/benchmarks/programbench-data/fetch_outcomes.py
"""

import hashlib
import json
import re
import subprocess
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pandas as pd
import yaml

REGISTRY_URL = "https://github.com/ProgramBench/submissions.git"
REGISTRY_COMMIT = "c19e570f64719c8326ccdcc7af803447cb89d1a6"  # 2026-09-30, 25 runs
PB_URL = "https://github.com/facebookresearch/ProgramBench.git"
PB_COMMIT = "27f02157c785f8da3647aa6dbbe6b9137f99f10e"  # v1.2.5
MSWEA_YAML = ("https://raw.githubusercontent.com/SWE-agent/mini-swe-agent/e187bcb2ff5825d85761a6f9c1f98c9fa6cfbc79/"
              "src/minisweagent/config/benchmarks/programbench.yaml")  # v2.4.5
ROOT = Path(__file__).resolve().parents[3]
CACHE = ROOT / "data" / "downloads" / "programbench"
OUT = Path(__file__).resolve().parents[1] / "panel" / "sources" / "programbench"
GIT_ENV = {"GIT_LFS_SKIP_SMUDGE": "1", "PATH": "/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin"}
N_TASKS = 200


def sparse_clone(url: str, commit: str, dest: Path, patterns: list[str]) -> Path:
    if not (dest / ".git").exists():
        def git(*a):
            subprocess.run(["git", "-C", str(dest), *a], check=True, env=GIT_ENV)
        dest.mkdir(parents=True, exist_ok=True)
        git("init", "-q")
        git("remote", "add", "origin", url)
        git("sparse-checkout", "set", "--no-cone", *patterns)
        git("fetch", "-q", "--depth", "1", "--filter=blob:none", "origin", commit)
        git("checkout", "-q", commit)
    head = subprocess.run(["git", "-C", str(dest), "rev-parse", "HEAD"], capture_output=True, text=True).stdout
    assert head.strip() == commit, (dest, head)
    return dest


def get(url: str, rng: str | None = None, tries: int = 6) -> str | None:
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"Range": f"bytes={rng}"} if rng else {})
            return urllib.request.urlopen(req, timeout=120).read().decode("utf-8", "replace")
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            if i == tries - 1:
                raise
        except Exception:
            if i == tries - 1:
                raise
        time.sleep(5 * 2 ** i)


def string_field(s: str, key: str) -> str | None:
    i = s.find(f'"{key}": ')
    if i < 0:
        return None
    try:
        return json.JSONDecoder().raw_decode(s, i + len(key) + 4)[0]
    except json.JSONDecodeError:
        return None


def eval_tail(base: str, iid: str) -> dict:
    url = f"{base}/{iid}/{iid}.eval.json"
    s = get(url, "-20000")
    if s is None:
        return {"eval_json": False}
    i = s.rfind('"error_code":')
    try:
        d = json.loads("{" + s[i:]) if i >= 0 else None
    except json.JSONDecodeError:
        d = None
    if d is None:  # error_details longer than the tail: read the whole file
        full = json.loads(get(url))
        d = {k: v for k, v in full.items() if k != "test_results"}
    return {"eval_json": True, "error_code": d["error_code"],
            "test_branches_run": len(d["test_branches"]), "test_branch_errors": len(d["test_branch_errors"]),
            "test_branch_error_codes": ";".join(sorted({e["error_code"] for v in d["test_branch_errors"].values()
                                                        for e in (v if isinstance(v, list) else [v])})),
            "eval_warnings": len(d["warnings"])}


def traj_head(base: str, iid: str) -> dict:
    url = f"{base}/{iid}/{iid}.traj.json"
    s = get(url, "0-40000")
    if s is None:
        return {"traj_json": False}
    status = string_field(s, "exit_status")
    if status is None:
        tail = get(url, "-20000") or ""
        hits = re.findall(r'"exit_status": "([^"]*)"', tail)
        status = hits[-1] if hits else None
    sha = lambda t: hashlib.sha256(t.encode()).hexdigest()[:12] if t else None
    return {"traj_json": True, "exit_status": status, "mini_version": string_field(s, "mini_version"),
            "system_template_sha12": sha(string_field(s, "system_template")),
            "instance_template_sha12": sha(string_field(s, "instance_template")),
            "traj_model_name": string_field(s, "model_name")}


def fork_extracts(run_id: str, source: str, commit: str, iids: list[str]) -> dict:
    """Per-task eval/traj extracts for one run, cached under data/downloads/."""
    path = CACHE / "fork_extracts" / f"{run_id}.json"
    if path.exists():
        cached = json.loads(path.read_text())
        if cached["commit"] == commit:
            return cached["tasks"]
    base = source.replace("https://github.com/", "https://raw.githubusercontent.com/") + "/" + commit
    with ThreadPoolExecutor(8) as pool:
        tasks = dict(zip(iids, pool.map(lambda i: {**eval_tail(base, i), **traj_head(base, i)}, iids)))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"commit": commit, "tasks": tasks}))
    return tasks


def current_filters(pb: Path) -> dict[str, tuple[set, set]]:
    out = {}
    for f in pb.glob("src/programbench/data/tasks/*/tests.json"):
        br = json.loads(f.read_text())["branches"]
        active = {b for b, v in br.items() if not v["ignored"]}
        ignored = {f"{b}/{t['name']}" for b, v in br.items() for t in v.get("ignored_tests") or []}
        out[f.parent.name] = (active, ignored)
    return out


def main() -> None:
    reg = sparse_clone(REGISTRY_URL, REGISTRY_COMMIT, CACHE / "registry",
                       ["ignored_tests.json", "submissions/*/submission.yaml", "submissions/*/pointer.yaml",
                        "submissions/*/_stats/*.json"])
    pb = sparse_clone(PB_URL, PB_COMMIT, CACHE / "programbench-tests-json", ["src/programbench/data/tasks/*/tests.json"])
    filters = current_filters(pb)
    tasks = sorted(t for t in filters if not t.startswith("testorg__"))
    assert len(tasks) == N_TASKS
    reg_ignore = json.loads((reg / "ignored_tests.json").read_text())
    agent = yaml.safe_load(get(MSWEA_YAML))["agent"]
    sha = lambda t: hashlib.sha256(t.encode()).hexdigest()[:12]
    ref_sys, ref_inst = sha(agent["system_template"]), sha(agent["instance_template"])

    board, rows = [], []
    for d in sorted(p for p in (reg / "submissions").iterdir() if p.is_dir()):
        man = yaml.safe_load((d / "submission.yaml").read_text())
        ptr = yaml.safe_load((d / "pointer.yaml").read_text())
        stats = {n: json.loads((d / "_stats" / f"{n}.json").read_text()) if (d / "_stats" / f"{n}.json").exists() else {}
                 for n in ("score", "cost", "calls", "tokens")}
        assert set(stats["score"]) <= set(tasks), d.name
        date, mini = re.match(r"(\d{8})_mini-v([\d.]+)_", d.name).groups()
        effort = re.search(r"\((?:(\w+) reasoning|(\w+))\)", man["system"]["model"])
        ex = fork_extracts(d.name, ptr["source"], ptr["commit"], sorted(stats["score"]))
        for iid in tasks:
            tests = stats["score"].get(iid)
            r = {"run_id": d.name, "instance_id": iid, "attempted": tests is not None}
            if tests is not None:
                kept = {k: v for k, v in tests.items() if k not in set(reg_ignore.get(iid, []))}
                active, ignored = filters[iid]
                v125 = {k: v for k, v in kept.items() if k.split("/", 1)[0] in active and k not in ignored}
                r |= {"n_tests": len(kept), "n_passed": sum(kept.values()),
                      "score": sum(kept.values()) / len(kept) if kept else 0.0,
                      "n_tests_v125": len(v125), "n_passed_v125": sum(v125.values()),
                      "score_v125": sum(v125.values()) / len(v125) if v125 else 0.0,
                      "cost_usd": stats["cost"].get(iid), "api_calls": stats["calls"].get(iid),
                      "output_tokens": stats["tokens"].get(iid),
                      **{k: v for k, v in ex[iid].items() if not k.endswith("template_sha12")}}
            else:
                r |= {"score": 0.0, "score_v125": 0.0}
            r["resolved"] = r["score"] >= 1.0
            r["near_resolved"] = r["score"] >= 0.95
            rows.append(r)
        run = pd.DataFrame([x for x in rows if x["run_id"] == d.name])
        sys_shas = {v.get("system_template_sha12") for v in ex.values()} - {None}
        inst_shas = {v.get("instance_template_sha12") for v in ex.values()} - {None}
        board.append({
            "run_id": d.name, "model": man["system"]["model"], "provider": man["system"]["provider"],
            "agent": man["system"]["agent"], "mini_swe_agent_version": mini,
            "effort": next((g for g in effort.groups() if g), None) if effort else None,
            "run_date": f"{date[:4]}-{date[4:6]}-{date[6:]}", "is_os_model": man["system"].get("is_os_model"),
            "programbench_version": man["eval"].get("programbench_version"),
            "fork": ptr["source"], "fork_commit": ptr["commit"],
            "n_attempted": int(run["attempted"].sum()), "resolved_pct": round(100 * run["resolved"].mean(), 1),
            "near_resolved_pct": round(100 * run["near_resolved"].mean(), 1),
            "mean_score_pct": round(100 * run["score"].mean(), 1),
            "mean_score_v125_pct": round(100 * run["score_v125"].mean(), 1),
            "cost_usd": round(sum(stats["cost"].values()), 2),
            "system_template_sha12": ";".join(sorted(sys_shas)), "instance_template_sha12": ";".join(sorted(inst_shas)),
            "prompt_matches_v2_4_5": sys_shas == {ref_sys} and inst_shas == {ref_inst},
            "traj_model_name": ";".join(sorted({v.get("traj_model_name") for v in ex.values()} - {None})),
        })
        print(d.name, board[-1]["n_attempted"], board[-1]["mean_score_pct"], flush=True)

    df = pd.DataFrame(rows)
    att = df[df["attempted"]]
    summary = pd.DataFrame({
        "n_runs": df.groupby("instance_id").size(),
        "n_attempted": att.groupby("instance_id").size(),
        "mean_score": df.groupby("instance_id")["score"].mean(),
        "mean_score_attempted": att.groupby("instance_id")["score"].mean(),
        "max_score": df.groupby("instance_id")["score"].max(),
        "solve_rate": df.groupby("instance_id")["resolved"].mean(),
        "near_rate": df.groupby("instance_id")["near_resolved"].mean(),
        "n_zero_attempted": att.assign(z=att["score"] == 0).groupby("instance_id")["z"].sum(),
        "n_error_code": att.assign(e=att["error_code"].notna()).groupby("instance_id")["e"].sum(),
        "n_not_submitted_exit": att.assign(e=att["exit_status"] != "Submitted").groupby("instance_id")["e"].sum(),
        "n_tests_min": att.groupby("instance_id")["n_tests"].min(),
        "n_tests_max": att.groupby("instance_id")["n_tests"].max(),
    }).reset_index()
    OUT.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(board).to_csv(OUT / "leaderboard.csv", index=False)
    df.to_csv(OUT / "runs.csv", index=False)
    summary.round(4).to_csv(OUT / "task_summary.csv", index=False)
    print(f"{len(board)} runs x {len(tasks)} tasks -> {OUT}")


if __name__ == "__main__":
    main()
