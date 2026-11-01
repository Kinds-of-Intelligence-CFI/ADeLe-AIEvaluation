"""Build the cross-benchmark results panel: every public per-task result the benchmark studies
use, under one set of rules (README.md).

Inputs (gitignored unless noted; rebuild with the commands in README.md):
    data/results/{swebench,tau2}.parquet
    sources/terminal-bench-4/ (committed: the Harbor Hub export, see harbor_hub.py)
    data/instances/INSTANCES.tsv and the frozen instance files it lists
    data/instances/meta_terminal-bench-4.0.0.csv
    data/downloads/swe-experiments/evaluation/verified/<entry>/metadata.yaml
Outputs:
    data/results/panel.parquet   one row per (benchmark, task, configuration)
    tasks.csv                    one row per (benchmark, task): prompt hash, solve rate, flags
    coverage.csv, COVERAGE.md    what the panel covers, by benchmark and model generation
    unmapped_models.csv          raw model names missing from models.csv; must stay empty

    python experiments/benchmarks/panel/build.py
"""

import re
from pathlib import Path

import pandas as pd
import yaml

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
DATA = ROOT / "data"
SOLVABLE_FROM = 0.05
# Tasks an audit names as broken. SWE-bench Verified: the three OpenAI's 2026 audit names
# (the full list is not public); Terminal-Bench 4.0.0: Epoch's 30 (meta file, epoch_defect).
BROKEN_SWE = {"pylint-dev__pylint-4551": "OpenAI audit 2026 (narrow tests)",
              "sympy__sympy-18199": "OpenAI audit 2026 (wide tests)",
              "django__django-14725": "OpenAI audit 2026 (unstated parameter)"}
TTF = {"<15 min fix": 0, "15 min - 1 hour": 1, "1-4 hours": 2, ">4 hours": 3}


def model_key(raw: str) -> str:
    """Name-matching key: lowercase, no provider prefix, no trailing date, alphanumerics only."""
    s = str(raw).strip().lower()
    s = re.sub(r"^[a-z0-9._-]+/", "", s)
    s = re.sub(r"[-_ ]?20\d\d-?\d\d-?\d\d$", "", s)
    return re.sub(r"[^a-z0-9]", "", s)


def generation(release: str | None) -> str:
    if not isinstance(release, str) or not release:
        return "unknown"
    return ("G0" if release >= "2026-06" else "G1" if release >= "2026-01"
            else "G2" if release >= "2025-07" else "G3")


def load_registry() -> tuple[pd.DataFrame, dict]:
    reg = pd.read_csv(HERE / "models.csv", dtype=str).fillna("")
    reg["generation"] = reg["release"].map(generation)
    lookup = {}
    for r in reg.itertuples(index=False):
        for k in {model_key(r.model), *r.aliases.split()}:
            lookup[k] = r.model
    return reg, lookup


def swebench() -> pd.DataFrame:
    df = pd.read_parquet(DATA / "results/swebench.parquet")
    root = DATA / "downloads/swe-experiments/evaluation/verified"
    meta = {}
    for entry in df["entry"].unique():
        path = root / entry / "metadata.yaml"
        tags = (yaml.safe_load(path.read_text()) or {}).get("tags", {}) if path.exists() else {}
        models = tags.get("model") or []
        models = [models] if isinstance(models, str) else [str(m) for m in models]
        meta[entry] = {"models": models, "effort": tags.get("reasoning_effort"), "agent": tags.get("agent")}
    rows = df.assign(
        model_raw=df["entry"].map(lambda e: meta[e]["models"][0] if len(meta[e]["models"]) == 1 else ""),
        system=df["entry"].map(lambda e: len(meta[e]["models"]) != 1),
        effort=df["entry"].map(lambda e: meta[e]["effort"]),
        config=df["entry"], date=df["entry"].str[:4] + "-" + df["entry"].str[4:6],
        text_matches_frozen=True)
    return rows


def tau2() -> pd.DataFrame:
    df = pd.read_parquet(DATA / "results/tau2.parquet")
    frozen = pd.concat(pd.read_csv(p, dtype={"instance_id": str}) for p in sorted(DATA.glob("instances/instances_tau2-*.csv")))
    df = df.merge(frozen[["benchmark", "instance_id", "prompt_sha12"]], on=["benchmark", "instance_id"], how="left")
    return df.assign(model_raw=df["model"], system=False, effort=df["reasoning_effort"], config=df["run"],
                     date=df["submission_date"].astype(str).str[:7],
                     text_matches_frozen=df["task_prompt_sha12"] == df["prompt_sha12"]).drop(columns="prompt_sha12")


def terminalbench4() -> pd.DataFrame:
    from adele.results.sources import harbor_hub
    src = HERE / "sources/terminal-bench-4"
    df = harbor_hub.from_export(src / "harbor_hub_trials_4-0-0.json", src / "leaderboard_4-0-0.tsv")
    return df.assign(model_raw=df["model"], system=False, config=df["leaderboard_row"],
                     date="", text_matches_frozen=True)


def main() -> None:
    reg, lookup = load_registry()
    cols = ["benchmark", "instance_id", "model_raw", "system", "scaffold", "effort", "config", "date",
            "success", "n_trials", "text_matches_frozen", "source"]
    panel = pd.concat([f()[cols] for f in (swebench, tau2, terminalbench4)], ignore_index=True)

    keys = panel["model_raw"].map(model_key)
    panel["model"] = keys.map(lookup)
    panel["system"] = panel["system"] | panel["model"].isin(reg.loc[reg["system"] == "yes", "model"])
    unmapped = panel.loc[~panel["system"] & panel["model"].isna(), ["benchmark", "model_raw"]].drop_duplicates()
    unmapped.to_csv(HERE / "unmapped_models.csv", index=False)
    panel.loc[panel["system"], "model"] = "system"
    panel["generation"] = panel["model"].map(reg.set_index("model")["generation"])
    old = panel["system"] & (panel["date"] <= "2025-06")        # a system is no newer than its entry
    panel.loc[old, "generation"] = "G3"
    panel["generation"] = panel["generation"].fillna("unknown")

    # Frozen text for every task; tasks.csv keeps ids, hashes and flags, never text.
    manifest = pd.read_csv(DATA / "instances/INSTANCES.tsv", sep="\t")
    frames = []
    for f in manifest[manifest["benchmark"].isin(panel["benchmark"].unique())]["file"]:
        path = DATA / "instances" / f
        frames.append(pd.read_parquet(path) if path.suffix == ".parquet" else pd.read_csv(path, dtype={"instance_id": str}))
    inst = pd.concat(frames)[["benchmark", "instance_id", "prompt_sha12"]]
    inst["text_collapsed"] = inst.groupby(["benchmark", "prompt_sha12"])["instance_id"].transform("size") > 1

    use = panel[panel["text_matches_frozen"]]
    tasks = (use.assign(solved=use["success"] * use["n_trials"])
             .groupby(["benchmark", "instance_id"])
             .agg(n_configs=("config", "nunique"), n_trials=("n_trials", "sum"), solved_trials=("solved", "sum"))
             .reset_index())
    tasks["solve_rate"] = (tasks["solved_trials"] / tasks["n_trials"]).round(4)
    tasks = inst.merge(tasks, on=["benchmark", "instance_id"], how="inner")
    tb4 = pd.read_csv(DATA / "instances/meta_terminal-bench-4.0.0.csv", dtype=str).fillna("")
    broken = {("swe-bench-verified", k): v for k, v in BROKEN_SWE.items()}
    broken |= {("terminal-bench-4.0.0", r.instance_id): f"Epoch review 2026 ({r.epoch_defect})"
               for r in tb4.itertuples() if r.epoch_defect}
    tasks["known_broken"] = [broken.get((b, i), "") for b, i in zip(tasks["benchmark"], tasks["instance_id"])]
    tasks["verifiably_solvable"] = (tasks["solve_rate"] >= SOLVABLE_FROM) & (tasks["known_broken"] == "")

    from datasets import load_dataset
    ttf = (load_dataset("princeton-nlp/SWE-bench_Verified", split="test", revision="c104f840cc67f8b6eec6f759ebc8b2693d585d4a")
           .to_pandas().set_index("instance_id")["difficulty"])
    tasks["human_time_bucket"] = [ttf.get(i, "") if b == "swe-bench-verified" else "" for b, i in zip(tasks["benchmark"], tasks["instance_id"])]
    hours = tb4.set_index("instance_id")
    tasks["expert_hours"] = [hours["expert_time_estimate_hours"].get(i, "") if b == "terminal-bench-4.0.0" else ""
                             for b, i in zip(tasks["benchmark"], tasks["instance_id"])]
    tasks["category"] = [hours["category"].get(i, "") if b == "terminal-bench-4.0.0" else "" for b, i in zip(tasks["benchmark"], tasks["instance_id"])]

    panel.to_parquet(DATA / "results/panel.parquet")
    tasks.sort_values(["benchmark", "instance_id"]).to_csv(HERE / "tasks.csv", index=False)
    coverage(panel, tasks)
    print(f"panel: {len(panel)} rows; tasks: {len(tasks)}; unmapped models: {len(unmapped)}")


def coverage(panel: pd.DataFrame, tasks: pd.DataFrame) -> None:
    gens = ["G0", "G1", "G2", "G3", "unknown"]
    rows = []
    for b, g in panel.groupby("benchmark"):
        t = tasks[tasks["benchmark"] == b]
        row = {"benchmark": b, "tasks_with_results": len(t),
               "verifiably_solvable": int(t["verifiably_solvable"].sum()),
               "known_broken": int((t["known_broken"] != "").sum()),
               "text_collapsed": int(t["text_collapsed"].sum()),
               "configs": g["config"].nunique(),
               "single_models": g.loc[~g["system"], "model"].nunique(),
               "systems": g.loc[g["system"], "config"].nunique(),
               "rows_text_differs": int((~g["text_matches_frozen"]).sum())}
        for gen in gens:
            row[f"models_{gen}"] = g.loc[~g["system"] & (g["generation"] == gen), "model"].nunique()
        rows.append(row)
    cov = pd.DataFrame(rows)
    cov.to_csv(HERE / "coverage.csv", index=False)

    models = panel[~panel["system"]].groupby("model").agg(
        generation=("generation", "first"), benchmarks=("benchmark", lambda s: sorted(set(s))))
    shared = models[models["benchmarks"].map(len) > 1]
    lines = ["# Panel coverage", "",
             "Generated by `build.py`; do not edit by hand. Rules in `README.md`.", "",
             "| benchmark | tasks with results | verifiably solvable | known broken | text shared by several tasks | configurations | single models (G0/G1/G2/G3/unknown) | multi-model systems | results dropped for text drift |",
             "|---|---|---|---|---|---|---|---|---|"]
    for r in cov.itertuples(index=False):
        lines.append(f"| {r.benchmark} | {r.tasks_with_results} | {r.verifiably_solvable} | {r.known_broken} | {r.text_collapsed} "
                     f"| {r.configs} | {r.single_models} ({r.models_G0}/{r.models_G1}/{r.models_G2}/{r.models_G3}/{r.models_unknown}) "
                     f"| {r.systems} | {r.rows_text_differs} |")
    lines += ["", "Models with results on more than one benchmark (they link the benchmarks' scales):", "",
              "| model | generation | benchmarks |", "|---|---|---|"]
    lines += [f"| {m} | {r.generation} | {', '.join(r.benchmarks)} |" for m, r in shared.sort_index().iterrows()]
    (HERE / "COVERAGE.md").write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
