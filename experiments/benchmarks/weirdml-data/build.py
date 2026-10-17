"""Build WeirdML instance + outcome tables from the files fetch.py downloaded.

    python experiments/benchmarks/weirdml-data/fetch.py
    python experiments/benchmarks/weirdml-data/build.py

Writes (all under gitignored data/):
  data/instances/instances_weirdml-v2.parquet  4 scored v2 tasks with a full public prompt
  data/instances/meta_weirdml.csv              every v2/v3 task: public status, source, time estimates
  data/results/weirdml/runs_v2.parquet         per-run scores (87 models, snapshot 2026-02-13)
  data/results/weirdml/runs_v3.parquet         per-run scores (983 runs, 2026-09-13..28)

Prompt = v2 system prompt + task prompt, i.e. the full first message set the
model receives in v2 (the system prompt is the benchmark's own, shared by all
tasks). No v3 instance file: no v3 task prompt is public. No LLM calls.
"""

import hashlib
import json
import statistics
import sys
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parents[3]
RAW = REPO / "data" / "results" / "weirdml"
INST = REPO / "data" / "instances"
sys.path.insert(0, str(REPO / "src"))
from adele.instances import validate_instances  # noqa: E402  (read-only use)

SITE_COMMIT = "9553938f2cb0c7077ab47ba0cadde18bc440e71d"
SITE_URL = "https://htihle.github.io"
BENCH_V2 = "weirdml-v2"

# v2 tasks with a public prompt. shuffle_* are public (v1 tasks) but were dropped
# from v2 scoring for prompt issues (Epoch review; htihle on X), so no v2 outcomes.
V2_SCORED_PUBLIC = ["shapes_easy", "shapes_hard", "digits_unsup", "chess_winners"]
V2_DROPPED_PUBLIC = ["shuffle_easy", "shuffle_hard"]
# v3 tasks described (not prompted) on /weirdml_tasks.html
V3_DESCRIBED = {"shapes_generalize", "ship_detect", "tod_pipeline", "weirdml_bonanza"}


def sha12(t: str) -> str:
    return hashlib.sha256(t.encode()).hexdigest()[:12]


def fenced(name: str) -> str:
    """Text between the two '~~~~' fence lines of a site prompt page."""
    lines = (RAW / "prompts" / name).read_text().splitlines()
    idx = [i for i, l in enumerate(lines) if l.strip() == "~~~~"]
    assert len(idx) == 2, (name, idx)
    return "\n".join(lines[idx[0] + 1: idx[1]]).strip()


def time_estimates():
    est = json.loads((RAW / "timehorizons_all_estimates.json").read_text())
    hum = json.loads((RAW / "timehorizons_human_estimates.json").read_text())
    out = {}
    for task, d in est.items():
        def med(th):
            return statistics.median(e[th]["hours"] for e in d["estimates"].values())
        h = hum.get(task, {}).get("estimates", {}).get("50%", {}).get("hours")
        out[task] = {"llm_hours_50pct_median": med("50%"),
                     "llm_hours_90pct_median": med("90%"),
                     "human_hours_50pct": h}
    return out


def main() -> None:
    system = fenced("system_prompt_v2.md")
    rows, meta = [], []
    te = time_estimates()

    for t in V2_SCORED_PUBLIC:
        task = fenced(f"task_prompt_{t}.md")
        prompt = system + "\n\n" + task
        rows.append({"benchmark": BENCH_V2, "instance_id": t, "prompt": prompt,
                     "prompt_sha12": sha12(prompt)})
    df = pd.DataFrame(rows)
    warnings = validate_instances(df, where=BENCH_V2)
    df.to_parquet(INST / f"instances_{BENCH_V2}.parquet", index=False)
    print(f"instances_{BENCH_V2}.parquet: {len(df)} rows, warnings={warnings}")

    # ---- meta: v2 (17 scored + 2 dropped) ----
    v2csv = pd.read_csv(RAW / "weirdml_v2_data.csv")
    v2_scored = [c[:-4] for c in v2csv.columns if c.endswith("_acc") and c != "avg_acc"]
    for t in v2_scored + V2_DROPPED_PUBLIC:
        public = t in V2_SCORED_PUBLIC or t in V2_DROPPED_PUBLIC
        meta.append({
            "version": "v2", "task": t,
            "public_status": "full_prompt" if public else "name_only",
            "in_v2_scoring": t in v2_scored,
            "in_instances": t in V2_SCORED_PUBLIC,
            "source_url": f"{SITE_URL}/prompts/task_prompt_{t}.html" if public else f"{SITE_URL}/weirdml_v2.html",
            "source_commit": SITE_COMMIT,
            "task_prompt_sha12": sha12(fenced(f"task_prompt_{t}.md")) if public else None,
            **te.get(t, {}),
        })
    # ---- meta: v3 (11 tasks) ----
    v3 = json.loads((RAW / "weirdml_v3_results.json").read_text())
    for t, d in v3["tasks"].items():
        meta.append({
            "version": "v3", "task": t, "display_name": d["display_name"], "kind": d["kind"],
            "v3_prompt_version": d["prompt_version"],
            "public_status": "description_only" if t in V3_DESCRIBED else "name_only",
            "in_v2_scoring": False, "in_instances": False,
            "source_url": f"{SITE_URL}/weirdml_tasks.html" if t in V3_DESCRIBED else f"{SITE_URL}/weirdml.html",
            "source_commit": SITE_COMMIT,
        })
    m = pd.DataFrame(meta)
    m.to_csv(INST / "meta_weirdml.csv", index=False)
    print(f"meta_weirdml.csv: {len(m)} rows")

    # ---- per-run outcomes ----
    v2r = json.loads((RAW / "weirdml_v2_runs_timehorizons.json").read_text())
    r2 = pd.DataFrame([
        {"benchmark": BENCH_V2, "instance_id": task, "model_id": mid,
         "display_name": mv["display_name"], "release_date": mv["release_date"],
         "run_id": r["run_id"], "score": r["score"]}
        for mid, mv in v2r["models"].items()
        for task, tv in mv["tasks"].items() for r in tv["runs"]
    ])
    r2.to_parquet(RAW / "runs_v2.parquet", index=False)
    keep = ["sample_key", "eval_id", "task", "sample_id", "hints_enabled", "model_id",
            "run_date", "prompt_version", "agent", "agent_version", "task_score",
            "final_best", "best_raw", "best_effective", "floor", "ceiling",
            "submissions_used", "tokens_total", "cost_usd", "stop_reason"]
    r3 = pd.DataFrame([{k: s[k] for k in keep} for s in v3["samples"]])
    r3.to_parquet(RAW / "runs_v3.parquet", index=False)
    print(f"runs_v2.parquet: {len(r2)} runs, {r2.model_id.nunique()} models; "
          f"runs_v3.parquet: {len(r3)} runs, {r3.model_id.nunique()} models")


if __name__ == "__main__":
    main()
