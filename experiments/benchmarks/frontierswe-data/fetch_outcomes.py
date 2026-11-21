"""FrontierSWE v2 outcomes from the public frontierswe.com pages that robots.txt allows.

Per-run outcomes live under /traces, which robots.txt disallows for every user agent
(checked on 2026-10-01), so this script does NOT fetch them. It reads only the home
page and the 34 /tasks/<slug> pages. Both are Next.js pages that inline their data in
the React server-component payload (``self.__next_f.push``); no API call is needed.

What the allowed pages give:
  home page   per task x model: mean@5 and best@5 reward (heatmap), runs, mean cost,
              mean hours, mean / best-model mean; per model: leaderboard (best / mean /
              worst aggregation, by category), cost, tokens, duration; per model: the
              sorted list of all its run rewards pooled over tasks (no task labels).
  task pages  per model on that task: score, its "±" spread, steps, input and output
              tokens, average cost, average time.
Per-run, task-labelled rewards are not available without /traces.

Raw HTML is cached under data/raw/frontierswe-v2/site/ (gitignored) and reused.
Needs data/instances/meta_frontierswe-v2.csv from fetch_tasks.py (site name -> task dir).

Writes, to experiments/benchmarks/panel/sources/frontierswe-v2/ (ids and numbers only):
  task_model.csv           one line per task x model
  models.csv               one line per model (leaderboard)
  model_reward_pools.json  per model, sorted run rewards pooled over tasks
  task_summary.csv         one line per task

Run: python experiments/benchmarks/frontierswe-data/fetch_outcomes.py
"""

import json
import re
import time
import urllib.request
import urllib.robotparser
from pathlib import Path

import pandas as pd

SITE = "https://www.frontierswe.com"
UA = "adele-data/0.1"
REPO = Path(__file__).resolve().parents[3]
CACHE = REPO / "data" / "raw" / "frontierswe-v2" / "site"
META = REPO / "data" / "instances" / "meta_frontierswe-v2.csv"
OUT = Path(__file__).resolve().parents[1] / "panel" / "sources" / "frontierswe-v2"
THRESHOLDS = (0.1, 0.5, 0.9, 0.99)
# Leaderboard additions from frontierswe.com/changelog (fetched 2026-10-01). Models not
# listed were on the board at the v2 launch (blog, 2026-09-02).
ADDED = {"Gemini 3.8 Flash": "2026-09-08", "Claude Opus 5": "2026-09-08", "Claude Fable 5": "2026-09-08",
         "GPT-6 Astra": "2026-09-11", "Grok 4.7": "2026-09-21", "Claude Opus 5.5": "2026-09-22",
         "Claude Sonnet 5.5": "2026-09-28", "Gemini 4 Argon": "2026-09-30"}

_robots = urllib.robotparser.RobotFileParser(SITE + "/robots.txt")


def get(path: str, name: str) -> str:
    """GET SITE+path once (cached as CACHE/name.html), refusing anything robots.txt disallows."""
    f = CACHE / f"{name}.html"
    if f.exists():
        return f.read_text(encoding="utf-8")
    if _robots.last_checked == 0:
        _robots.read()
    assert _robots.can_fetch(UA, SITE + path), f"robots.txt disallows {path}"
    req = urllib.request.Request(SITE + path, headers={"User-Agent": UA})
    html = urllib.request.urlopen(req, timeout=60).read().decode()
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(html, encoding="utf-8")
    time.sleep(2)
    return html


def rsc_rows(html: str) -> dict:
    """Decode the inlined RSC payload into {row id: parsed JSON}.

    Rows are "<id>:<json>\\n", except text rows "<id>:T<hex byte length>,<text>", which
    carry no terminator; JSON rows that fail to parse (none expected) are skipped."""
    chunks = re.findall(r'self\.__next_f\.push\(\[1,"(.*?)"\]\)</script>', html, re.S)
    b = "".join(json.loads('"' + c + '"') for c in chunks).encode()
    rows, pos = {}, 0
    while pos < len(b):
        colon = b.index(b":", pos)
        k = b[pos:colon].decode().strip()
        if b[colon + 1:colon + 2] == b"T":
            comma = b.index(b",", colon)
            pos = comma + 1 + int(b[colon + 2:comma], 16)
            continue
        end = b.find(b"\n", colon)
        end = len(b) if end < 0 else end
        v = b[colon + 1:end].decode()
        pos = end + 1
        if v[:1] in "[{":
            try:
                rows[k] = json.loads(v)
            except json.JSONDecodeError:
                pass
    return rows


def find(o, pred):
    """First dict in o (depth first) for which pred(dict) holds."""
    if isinstance(o, dict):
        if pred(o):
            return o
        o = list(o.values())
    if isinstance(o, list):
        for v in o:
            x = find(v, pred)
            if x is not None:
                return x
    return None


def resolve(o, rows: dict, seen=frozenset()):
    """Inline "$L<id>" references to other payload rows."""
    if isinstance(o, str):
        m = re.fullmatch(r"\$L([0-9a-f]+)", o)
        return resolve(rows[m.group(1)], rows, seen | {o}) if m and m.group(1) in rows and o not in seen else o
    if isinstance(o, list):
        return [resolve(v, rows, seen) for v in o]
    if isinstance(o, dict):
        return {k: resolve(v, rows, seen) for k, v in o.items()}
    return o


def text(o) -> str:
    """Visible text of an RSC element tree (svg skipped; "$$" is an escaped "$")."""
    if isinstance(o, str):
        return o[1:] if o.startswith("$$") else "" if o.startswith("$") else o
    if isinstance(o, list):
        if len(o) == 4 and o[0] == "$":
            return "" if o[1] == "svg" or not isinstance(o[3], dict) else text(o[3].get("children"))
        return "".join(map(text, o))
    return "" if o is None or isinstance(o, bool) else str(o)


def td_texts(row) -> list:
    """Texts of the <td> cells inside one RSC table row element."""
    out = []
    def walk(o):
        if isinstance(o, list):
            if len(o) == 4 and o[0] == "$" and o[1] == "td":
                out.append(text(o[3].get("children")))
                return
            for v in o:
                walk(v)
        elif isinstance(o, dict):
            walk(o.get("children"))
    walk(row)
    return out


def num(s: str):
    """'230.4M' / '715k' / '$65.17' / '$13.52*' / '15.2h' -> float; '' or '-' -> None."""
    s = s.strip().lstrip("$").rstrip("h*").replace(",", "")  # "*": cost caveat marker
    if s in ("", "-", "—"):
        return None
    mult = {"k": 1e3, "M": 1e6, "B": 1e9}.get(s[-1], 1)
    return float(s[:-1] if mult != 1 else s) * mult


def home() -> tuple:
    rows = rsc_rows(get("/", "index"))
    board = find(rows, lambda d: "entries" in d)["entries"]["abs"]
    heat = find(rows, lambda d: "best" in d and "mean" in d and isinstance(d["best"], dict) and "cells" in d["best"])
    per_model = find(rows, lambda d: "tasks" in d and d["tasks"] and "perModel" in d["tasks"][0])["tasks"]
    pools = find(rows, lambda d: "series" in d and "any" in d)
    return board, heat, per_model, pools


def task_page(slug: str) -> list:
    rows = rsc_rows(get(f"/tasks/{slug}", f"tasks/{slug}"))
    table = resolve(find(rows, lambda d: d.get("aria-label") == "Task results"), rows)
    out = []
    def walk(o):
        if isinstance(o, list):
            if len(o) == 4 and o[0] == "$" and isinstance(o[3], dict) and str(o[3].get("href", "")).startswith("/traces?model="):
                href = o[3]["href"]
                cells = td_texts(o[3].get("children"))
                assert len(cells) == 8, (slug, href, cells)
                score, pm = re.fullmatch(r"([0-9.]+|[-—]?)(?:±([0-9.]+))?", cells[2]).groups()
                out.append({"model_key": re.search(r"model=([^&]+)", href).group(1), "page_rank": int(cells[0]),
                            "model": cells[1], "page_score": num(score),
                            "page_pm": float(pm) if pm else None, "steps": num(cells[3]),
                            "tokens_in": num(cells[4]), "tokens_out": num(cells[5]),
                            "avg_cost_usd": num(cells[6]), "avg_hours_page": num(cells[7]), "traces_url": SITE + href})
                return
            for v in o:
                walk(v)
        elif isinstance(o, dict):
            walk(o.get("children"))
    walk(table)
    return out


def main() -> None:
    board, heat, per_model, pools = home()
    tasks = [t["slug"] for t in heat["mean"]["tasks"]]
    models = heat["mean"]["models"]
    key_of = {m["model"]: m["key"] for m in models}
    name2id = dict(pd.read_csv(META)[["name", "instance_id"]].itertuples(index=False))
    slug2id = {t["slug"]: name2id[t["name"]] for t in heat["mean"]["tasks"]}
    assert len(set(slug2id.values())) == len(tasks) == 34

    rows, best_run = [], {}
    pm_by_slug = {t["slug"]: {m["model"]: m for m in t["perModel"]} for t in per_model}
    for i, slug in enumerate(tasks):
        page = {r["model_key"]: r for r in task_page(slug)}
        for j, m in enumerate(models):
            p, q = pm_by_slug[slug][m["model"]], page.get(m["key"], {})
            mean, best = heat["mean"]["cells"][i][j], heat["best"]["cells"][i][j]
            rows.append({
                "instance_id": slug2id[slug], "site_slug": slug, "model_key": m["key"], "model": m["model"],
                "vendor": m["vendor"], "harness": m["harness"], "n_runs": p["runs"],
                "mean_reward": None if mean is None else round(mean / 100, 8),
                "best_reward": None if best is None else round(best / 100, 8),
                "mean_reward_home": p["mean"], "mean_frac_of_top_model": p["meanFrac"],
                "page_score": q.get("page_score"), "page_pm": q.get("page_pm"), "steps": q.get("steps"),
                "tokens_in": q.get("tokens_in"), "tokens_out": q.get("tokens_out"),
                "avg_cost_usd": p["meanCost"], "avg_hours": p["meanHours"],
                "traces_url": q.get("traces_url"),
            })
        href = heat["best"]["anyTraceHref"][i]
        best_run[slug] = {"best_run_reward": round(heat["best"]["anyModel"][i] / 100, 8),
                          "best_run_id": href.rsplit("/", 1)[-1] if href else None}
    tm = pd.DataFrame(rows)

    lb = []
    for agg in ("best", "mean", "worst"):
        for e in board[agg]:
            lb.append({"agg": agg, **{k: e.get(k) for k in ("model", "vendor", "harness", "generation", "overall",
                       "implementation", "performance", "research", "avgCostUsd", "costCaveat", "avgTokensOut",
                       "avgTokensTotal", "avgDurationSeconds")}})
    lb = pd.DataFrame(lb)
    wide = lb.pivot(index="model", columns="agg", values=["overall", "implementation", "performance", "research"])
    wide.columns = [f"{c}_{a}" for c, a in wide.columns]
    first = lb[lb["agg"] == "mean"].set_index("model")[["vendor", "harness", "generation", "avgCostUsd", "costCaveat",
                                                     "avgTokensOut", "avgTokensTotal", "avgDurationSeconds"]]
    md = first.join(wide).reset_index()
    md.insert(1, "model_key", md.model.map(key_of))
    runs = tm.groupby("model").n_runs.agg(["sum", "min", "max"]).rename(
        columns={"sum": "n_runs", "min": "min_runs_per_task", "max": "max_runs_per_task"})
    md = md.join(runs, on="model")
    md["pooled_rewards"] = md.model_key.map({s["key"]: len(s["rewards"]) for s in pools["series"]})
    md["added_to_board"] = md.model.map(ADDED).fillna("launch (<=2026-09-02)")
    md = md.sort_values("overall_mean", ascending=False)

    summ = []
    for iid, g in tm.groupby("instance_id", sort=False):
        slug = g.site_slug.iloc[0]
        r = {"instance_id": iid, "site_slug": slug, "n_models": len(g), "n_runs": int(g.n_runs.sum()),
             "mean_reward": round((g.mean_reward * g.n_runs).sum() / g.n_runs.sum(), 4),
             "max_model_mean": round(g.mean_reward.max(), 4),
             **best_run[slug],
             "n_models_mean_zero": int((g.mean_reward == 0).sum()),
             "n_models_best_zero": int((g.best_reward == 0).sum())}
        for t in THRESHOLDS:
            r[f"share_models_mean_ge_{t}"] = round((g.mean_reward >= t).mean(), 4)
            r[f"share_models_best_ge_{t}"] = round((g.best_reward >= t).mean(), 4)
        summ.append(r)
    summ = pd.DataFrame(summ)

    OUT.mkdir(parents=True, exist_ok=True)
    tm.to_csv(OUT / "task_model.csv", index=False)
    md.to_csv(OUT / "models.csv", index=False)
    summ.to_csv(OUT / "task_summary.csv", index=False)
    (OUT / "model_reward_pools.json").write_text(json.dumps({
        "source": f"{SITE}/ home page, chart 'share of a model's runs scoring at or above each threshold'",
        "note": "sorted run rewards per model, pooled over all tasks; no task labels",
        "best_of_all_per_task_sorted": pools["any"],
        "models": {s["key"]: {"model": s["label"], "vendor": s["vendor"], "rewards": s["rewards"]}
                   for s in pools["series"]}}, indent=1))
    print(f"{len(tasks)} tasks x {len(models)} models, {int(tm.n_runs.sum())} runs -> {OUT}")


if __name__ == "__main__":
    main()
