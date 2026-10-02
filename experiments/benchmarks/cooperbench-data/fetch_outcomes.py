"""CooperBench per-pair outcomes for every public run, and a check against the leaderboard.

Unit: (pair, condition, config). pair_id = <repo dir>-<task id>-f<a>-f<b> (a < b), as in
fetch_tasks.py.

Sources (public, no login):
  1. HF CooperBench/trajectories @ TRAJ_REV (MIT). The paper's runs (OpenHands v0.54, two
     phases; Oct-Dec 2025): 5 models x {solo, coop, coop_wo_comm}. Per task pool:
     aggregated_results_<model>_k1.json; per pair: <model>_<repo>_task<id>_merge_report_*.json
     (coop, coop_wo_comm) and dual_test_result_<model>_*.json (solo; files with no model
     prefix are GPT-5, the default model: they agree with gpt5 aggregates on 401/404 pairs).
     Coverage is partial (see NOTES.md). Unprefixed coop_wo_comm merge reports match no model
     well (best: gpt5, 398/455) and are ignored.
  2. The leaderboard site cooperbench.com, built from github.com/cooperbench/website @
     WEBSITE_COMMIT (no licence file): public/static/data/coop/index.json and
     coop_git/index.json hold per-pair coop results for the 5 paper models and 3 Gemini
     configs (newer harness, Feb 2026); src/pages/leaderboard.astro holds the leaderboard
     totals. The live site files are compared with the pinned ones.
  3. HF CooperBench/team-trajectories @ TEAM_REV (Apache-2.0): GPT-5.5 ("gpt-5.5-hao") with
     the codex agent, newer harness (May 2026), all 652 pairs: solo, coop with git,
     team, team without protocol verbs. summary.json per run (cross-checked with eval.json).

Success (the official metric). Solo: both features' hidden tests pass on the agent's patch.
Coop: the two patches are merged with a cascade, and the pair passes if both test suites pass
after the first of: naive git merge (only if it has no conflict), union merge, LLM resolver
(website scripts/generate_coop_index.py; paper section 2.2 and App. E). The leaderboard
counts pairs with no result as failures (denominator 652).

Writes:
  experiments/benchmarks/cooperbench-data/outcomes.csv          HF-derived rows (MIT / Apache-2.0)
  experiments/benchmarks/cooperbench-data/leaderboard_check.csv per config: leaderboard vs reproduced
  data/raw/cooperbench/outcomes_site.csv                        site-derived coop rows (no licence)
  data/downloads/cooperbench/                                   caches

Run: python experiments/benchmarks/cooperbench-data/fetch_outcomes.py
"""

import collections
import json
import re
import tarfile
import urllib.request
from pathlib import Path

import pandas as pd
from huggingface_hub import hf_hub_download, snapshot_download

TRAJ_REPO, TRAJ_REV = "CooperBench/trajectories", "906bc2f62325eb6f8ccb4cf221e63df051cb3c99"
TEAM_REPO, TEAM_REV = "CooperBench/team-trajectories", "dd371629174a226ecd251672af315699b77de05d"
WEBSITE_COMMIT = "97dbb0aba7dd9eedf3edc92e834a9906ef474256"  # 2026-03-26
WEBSITE_RAW = f"https://raw.githubusercontent.com/cooperbench/website/{WEBSITE_COMMIT}/"
LIVE_SITE = "https://cooperbench.com/static/data/{}/index.json"
ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
CACHE = ROOT / "data" / "downloads" / "cooperbench"
RAW = ROOT / "data" / "raw" / "cooperbench"
N_PAIRS = 652

PAPER_MODELS = {  # file key -> (model, agent framework); OpenHands v0.54, paper harness
    "gpt5": ("GPT-5", "openhands-0.54"),
    "claude": ("Claude Sonnet 4.5", "openhands-0.54"),
    "minimax": ("MiniMax-M2", "openhands-0.54"),
    "qwen_coder": ("Qwen3-Coder-30B-A3B-Instruct", "openhands-0.54"),
    "qwen": ("Qwen3-30B-A3B-Instruct-2507", "openhands-0.54"),
}
SITE_MODELS = {  # site key -> (model, agent framework, condition)
    "gemini_flash_sdk": ("gemini-3-flash-preview", "openhands-sdk", "coop"),
    "gemini_flash_miniswe": ("gemini-3-flash-preview", "mini-swe-agent", "coop"),
    "gemini_pro_miniswe": ("gemini-3-pro-preview", "mini-swe-agent", "coop"),
    "gemini_flash_sdk_git": ("gemini-3-flash-preview", "openhands-sdk", "coop_git"),
    "gemini_flash_miniswe_git": ("gemini-3-flash-preview", "mini-swe-agent", "coop_git"),
    "gemini_pro_miniswe_git": ("gemini-3-pro-preview", "mini-swe-agent", "coop_git"),
}
TEAM_RUNS = {  # tarball -> condition
    "cmp-full-solo": "solo",
    "cmp-full-coopgit": "coop_git",
    "cmp-full-team": "team",
    "cmp-full-team-noproto": "team_noproto",
}
# paper Table 6 (App. E), "No-comm" LLM column, % of 652
PAPER_NO_COMM = {"gpt5": 27.91, "claude": 27.30, "minimax": 14.88, "qwen_coder": 14.72, "qwen": 3.37}


def pair_id(repo: str, task: str, a: int, b: int) -> str:
    repo = "typst_task" if repo == "typst" else repo
    a, b = sorted((int(a), int(b)))
    return f"{repo}-{str(task).removeprefix('task')}-f{a}-f{b}"


def fetch(url: str, dest: Path) -> Path:
    if not dest.exists():
        dest.parent.mkdir(parents=True, exist_ok=True)
        req = urllib.request.Request(url, headers={"User-Agent": "adele-research"})
        dest.write_bytes(urllib.request.urlopen(req, timeout=120).read())
    return dest


# ---- 1. paper runs from HF trajectories ------------------------------------------------


def cascade(f1: dict, f2: dict, clean: bool, prefix: str = "") -> tuple:
    def both(k):
        return f1.get(k) is True and f2.get(k) is True
    naive = clean and both("naive_merge_test_passed")
    union, llm = both("union_merge_test_passed"), both("llm_merge_test_passed")
    return bool(naive or union or llm), naive, union, llm


def model_of(name: str) -> str | None:
    for m in ("qwen_coder", "gpt5", "claude", "minimax", "qwen"):  # qwen_coder before qwen
        if name.startswith(m + "_"):
            return m
    return None


def paper_runs() -> pd.DataFrame:
    snap = Path(snapshot_download(
        TRAJ_REPO, repo_type="dataset", revision=TRAJ_REV, cache_dir=str(CACHE / "hf"), max_workers=8,
        allow_patterns=["*/*/*/aggregated_results_*_k1.json", "coop/**/*_merge_report_*.json",
                        "coop_wo_comm/**/*_merge_report_*.json", "solo/**/dual_test_result_*.json"]))
    rows = {}  # (pid, cond, model) -> dict; aggregated files take precedence (the site used them)
    dates = collections.defaultdict(list)

    for f in snap.glob("*/*/*/*/*"):
        cond, repo, task, pdir, name = f.parts[-5:]
        m = re.fullmatch(r"feature(\d+)_feature(\d+)", pdir)
        if not m or cond not in ("solo", "coop", "coop_wo_comm"):
            continue
        pid = pair_id(repo, task, m[1], m[2])
        if cond == "solo" and name.startswith("dual_test_result_"):
            mod = model_of(name.removeprefix("dual_test_result_")) or "gpt5"
            d = json.loads(f.read_text())
            rows.setdefault((pid, cond, mod), {
                "success": bool(d.get("both_tests_passed")), "feature_a_pass": d.get("feature1_test_passed"),
                "feature_b_pass": d.get("feature2_test_passed"), "source": "hf_dual_test_result"})
        elif cond != "solo" and "_merge_report_" in name and name.endswith(".json"):
            mod = model_of(name)
            d = json.loads(f.read_text())
            if mod is None or "features" not in d:
                continue
            f1, f2 = list(d["features"].values())
            clean = d["merge_analysis"].get("status") == "clean"
            ok, naive, union, llm = cascade(f1, f2, clean)
            dates[(cond, mod)].append(d["metadata"]["generated_at"][:10])
            rows.setdefault((pid, cond, mod), {
                "success": ok, "naive_conflict": not clean, "naive_ok": naive, "union_ok": union,
                "llm_ok": llm, "source": "hf_merge_report"})

    for f in snap.glob("*/*/*/aggregated_results_*_k1.json"):
        cond, repo, task, name = f.parts[-4:]
        mod = model_of(name.removeprefix("aggregated_results_"))
        if cond not in ("solo", "coop", "coop_wo_comm") or mod is None:
            continue
        for it in json.loads(f.read_text())["detailed_results"]:
            pid = pair_id(repo, task, it["feature1_id"], it["feature2_id"])
            if cond == "solo":
                r = {"success": bool(it.get("both_tests_passed")), "feature_a_pass": it.get("feature1_test_passed"),
                     "feature_b_pass": it.get("feature2_test_passed"), "source": "hf_aggregated"}
            else:
                conflict = bool(it.get("has_naive_merge_conflict"))
                ok, naive, union, llm = cascade(
                    {"naive_merge_test_passed": it.get("feature1_naive_merge_test_passed"),
                     "union_merge_test_passed": it.get("feature1_union_merge_test_passed"),
                     "llm_merge_test_passed": it.get("feature1_llm_merge_test_passed")},
                    {"naive_merge_test_passed": it.get("feature2_naive_merge_test_passed"),
                     "union_merge_test_passed": it.get("feature2_union_merge_test_passed"),
                     "llm_merge_test_passed": it.get("feature2_llm_merge_test_passed")},
                    not conflict)
                r = {"success": ok, "naive_conflict": conflict, "naive_ok": naive, "union_ok": union,
                     "llm_ok": llm, "source": "hf_aggregated"}
            old = rows.get((pid, cond, mod))
            r["per_pair_file_agrees"] = None if old is None else old["success"] == r["success"]
            rows[(pid, cond, mod)] = r

    out = pd.DataFrame([{"pair_id": p, "condition": c, "config": m, **v} for (p, c, m), v in rows.items()])
    out["model"] = out.config.map(lambda m: PAPER_MODELS[m][0])
    out["agent"] = out.config.map(lambda m: PAPER_MODELS[m][1])
    out["harness"] = "paper (plan + implement)"
    out["data_source"] = f"hf:{TRAJ_REPO}@{TRAJ_REV[:7]}"
    for (c, m), ds in dates.items():
        print(f"  eval dates {c:13s} {m:10s} {min(ds)} .. {max(ds)}")
    return out


# ---- 2. leaderboard site ---------------------------------------------------------------


def site() -> tuple[pd.DataFrame, dict]:
    rows = []
    for name in ("coop", "coop_git"):
        pinned = fetch(WEBSITE_RAW + f"public/static/data/{name}/index.json", CACHE / "website" / f"{name}_index.json")
        idx = json.loads(pinned.read_text())
        try:
            live = json.loads(fetch(LIVE_SITE.format(name), CACHE / "site" / f"{name}_index_live.json").read_text())
            print(f"  live site {name}/index.json identical to pinned: {live == idx}")
        except Exception as e:  # the pinned copy is authoritative
            print(f"  live site {name}/index.json not checked: {e}")
        seen = collections.defaultdict(dict)
        for t in idx["tasks"]:  # typst appears twice ("typst" for paper models, "typst_task" for Gemini)
            pid = pair_id(t["repo"], t["taskId"], t["f1"].removeprefix("feature"), t["f2"].removeprefix("feature"))
            seen[pid].update(t["results"])
        assert len(seen) == N_PAIRS, len(seen)
        for pid, res in seen.items():
            for cfg, r in res.items():
                paper = cfg in PAPER_MODELS
                rows.append({
                    "pair_id": pid, "condition": "coop" if paper else SITE_MODELS[cfg][2], "config": cfg,
                    "model": PAPER_MODELS[cfg][0] if paper else SITE_MODELS[cfg][0],
                    "agent": PAPER_MODELS[cfg][1] if paper else SITE_MODELS[cfg][1],
                    "harness": "paper (plan + implement)" if paper else "cooperbench v0.0.x (Feb 2026)",
                    "success": bool(r["passed"]), "naive_conflict": r.get("hasConflict"),
                    "site_missing_flag": bool(r.get("missing", False)),
                    "source": "site_index", "data_source": f"github:cooperbench/website@{WEBSITE_COMMIT[:7]}"})
    astro = fetch(WEBSITE_RAW + "src/pages/leaderboard.astro", CACHE / "website" / "leaderboard.astro").read_text()
    board = {}
    for view in ("coop", "solo"):
        body = re.search(rf"\b{view}: \[(.*?)\n\s*\],", astro, flags=re.S)[1]
        for key, score in re.findall(r'modelKey: "(\w+)",.*?score: ([\d.]+)', body, flags=re.S):
            cond = view if not key.endswith("_git") else "coop_git"
            board[(cond, key)] = float(score)
    return pd.DataFrame(rows), board


# ---- 3. GPT-5.5 team-trajectories ------------------------------------------------------


def team_runs() -> pd.DataFrame:
    rows = []
    for run, cond in TEAM_RUNS.items():
        p = hf_hub_download(TEAM_REPO, f"{run}.tar.gz", repo_type="dataset", revision=TEAM_REV,
                            cache_dir=str(CACHE / "hf"))
        with tarfile.open(p) as t:
            cfg = json.load(t.extractfile(f"{run}/config.json"))
            summ = json.load(t.extractfile(f"{run}/summary.json"))
            evals = {}
            for n in t.getnames():
                if n.endswith("/eval.json"):
                    d = json.load(t.extractfile(n))
                    a, b = d["features"][:2]
                    evals[pair_id(d["repo"], d["task_id"], a, b)] = d
        for r in summ["results"]:
            repo, task, fs = r["task"].split("/")
            a, b = fs.split(",")
            pid = pair_id(repo, task, a, b)
            e = evals.get(pid, {})
            ok = r.get("eval") == "pass"
            if e and "both_passed" in e:
                assert bool(e["both_passed"]) == ok or e.get("error"), (run, pid)
            rows.append({
                "pair_id": pid, "condition": cond, "config": f"gpt55_codex_{cond}",
                "model": cfg["model"], "agent": cfg["agent_framework"],
                "harness": "cooperbench (May 2026)", "success": ok if r.get("eval") in ("pass", "fail") else None,
                "source": "hf_team_summary", "data_source": f"hf:{TEAM_REPO}@{TEAM_REV[:7]}",
                "run_started": cfg.get("started_at", "")[:10]})
    return pd.DataFrame(rows)


def main() -> None:
    print("paper runs (HF trajectories)")
    hf = paper_runs()
    print("leaderboard site")
    st, board = site()
    print("GPT-5.5 team runs")
    tm = team_runs()

    # site vs HF, per pair (coop, paper models)
    m = st[st.config.isin(PAPER_MODELS)].merge(hf[hf.condition == "coop"][["pair_id", "config", "success"]],
                                               on=["pair_id", "config"], how="left", suffixes=("", "_hf"))
    st = st.merge(m[["pair_id", "config", "success_hf"]], on=["pair_id", "config"], how="left")

    checks = []
    for (cond, cfg), score in sorted(board.items()):
        src = st if cond in ("coop", "coop_git") else hf
        sub = src[(src.condition == cond) & (src.config == cfg)]
        n_pass = int(sub.success.fillna(False).sum())
        checks.append({"condition": cond, "config": cfg, "leaderboard_pct": score,
                       "source": "site_index" if src is st else "hf", "pairs_with_result": len(sub),
                       "passed": n_pass, "reproduced_pct_of_652": round(100 * n_pass / N_PAIRS, 2),
                       "pct_of_pairs_with_result": round(100 * n_pass / max(len(sub), 1), 2)})
    for cfg in PAPER_MODELS:
        for cond, ref in (("coop", board.get(("coop", cfg))), ("coop_wo_comm", PAPER_NO_COMM[cfg])):
            sub = hf[(hf.condition == cond) & (hf.config == cfg)]
            n_pass = int(sub.success.sum())
            checks.append({"condition": cond, "config": cfg,
                           "leaderboard_pct" if cond == "coop" else "paper_table6_pct": ref,
                           "source": "hf", "pairs_with_result": len(sub), "passed": n_pass,
                           "reproduced_pct_of_652": round(100 * n_pass / N_PAIRS, 2),
                           "pct_of_pairs_with_result": round(100 * n_pass / max(len(sub), 1), 2)})
    for cond, sub in tm.groupby("condition"):
        n_pass = int(sub.success.fillna(False).sum())
        checks.append({"condition": cond, "config": sub.config.iloc[0], "source": "hf_team",
                       "pairs_with_result": int(sub.success.notna().sum()), "passed": n_pass,
                       "reproduced_pct_of_652": round(100 * n_pass / N_PAIRS, 2),
                       "pct_of_pairs_with_result": round(100 * n_pass / max(int(sub.success.notna().sum()), 1), 2)})
    ck = pd.DataFrame(checks)
    print(ck.to_string(index=False))

    agree = st[st.success_hf.notna()]
    print("site vs HF coop, per pair agreement:",
          agree.groupby("config").apply(lambda d: f"{(d.success == d.success_hf).sum()}/{len(d)}").to_dict())

    cols = ["pair_id", "condition", "config", "model", "agent", "harness", "success", "feature_a_pass",
            "feature_b_pass", "naive_conflict", "naive_ok", "union_ok", "llm_ok", "per_pair_file_agrees",
            "source", "data_source"]
    out = pd.concat([hf, tm], ignore_index=True).reindex(columns=cols)
    out = out.sort_values(["condition", "config", "pair_id"]).reset_index(drop=True)
    out.to_csv(HERE / "outcomes.csv", index=False)
    ck.to_csv(HERE / "leaderboard_check.csv", index=False)
    RAW.mkdir(parents=True, exist_ok=True)
    st.sort_values(["condition", "config", "pair_id"]).to_csv(RAW / "outcomes_site.csv", index=False)
    print(f"wrote {len(out)} HF rows, {len(st)} site rows")


if __name__ == "__main__":
    main()
