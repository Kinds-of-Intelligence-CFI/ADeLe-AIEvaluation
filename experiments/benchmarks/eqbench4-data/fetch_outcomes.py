"""EQ-Bench 4 per-(scenario, model) scores from the public leaderboard site.

Source: github.com/EQ-bench/EQ-bench-site (no licence file), folder eqbench4/, pinned to SITE_COMMIT
(the last commit that touched eqbench4/, 2026-07-26; HEAD 108382e3 of 2026-09-24 has the same files).
Sparse, blob-filtered checkout of eqbench4/ only (~130 MB). Per model:
eqbench4/eqbench4_docs/transcripts/<slug>/<i>.json holds one conversation with
  dims       8 pointwise trait scores, 0-10, one judge (Claude Opus 4.8; Opus 4.6 for grok-4.3)
  abilities  6 pairwise abilities, neighbour-relative signed margin, -5..+5 (see NOTES.md)
  ability_score = mean of the 6; ability_samples = judged comparisons behind each value
  turns      the transcript (not copied here), final_status
The leaderboard (Elo, CI, model-level traits and abilities) is eqbench4/eqbench4_data.js.

Writes (numbers and ids only, no text):
  experiments/benchmarks/eqbench4-data/outcomes.csv     one row per (scenario, model)
  experiments/benchmarks/eqbench4-data/leaderboard.csv  one row per model, with reproduction checks
Caches under data/downloads/eqbench4/ (site checkout; first/last site commit date per model from the
GitHub REST API, 28 unauthenticated calls, cached in site_dates.json).

Run after fetch_tasks.py: python experiments/benchmarks/eqbench4-data/fetch_outcomes.py
"""

import json
import subprocess
import urllib.request
from pathlib import Path

import numpy as np
import pandas as pd

SITE_URL = "https://github.com/EQ-bench/EQ-bench-site.git"
SITE_COMMIT = "033fc13598a9291e842ab59730f83b6859c70b48"  # "add new models", 2026-07-26
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CACHE = ROOT / "data" / "downloads" / "eqbench4"
SITE = CACHE / "EQ-bench-site"
DOCS = SITE / "eqbench4" / "eqbench4_docs"
DATASET = CACHE / "eqbench4" / "src" / "eqbench" / "datasets" / "test.json"
ELO_FILE = CACHE / "eqbench4" / "results" / "elo_results.json"
DATES = CACHE / "site_dates.json"
NAT_THRESHOLD = 7  # proposed binary success: naturalness_authenticity >= 7


def checkout() -> None:
    def git(*args):
        subprocess.run(["git", "-C", str(SITE), *args], check=True,
                       env={"GIT_LFS_SKIP_SMUDGE": "1", "PATH": "/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin"})
    if not (SITE / ".git").exists():
        SITE.mkdir(parents=True, exist_ok=True)
        git("init", "-q")
        git("remote", "add", "origin", SITE_URL)
        git("sparse-checkout", "set", "--no-cone", "/eqbench4/")
    git("fetch", "-q", "--depth", "1", "--filter=blob:none", "origin", SITE_COMMIT)
    git("checkout", "-q", SITE_COMMIT)


def site_dates(slugs: list) -> dict:
    """slug -> (first, last, n) commit dates touching transcripts/<slug>/index.json."""
    cached = json.loads(DATES.read_text()) if DATES.exists() else {}
    for slug in slugs:
        if slug in cached:
            continue
        url = ("https://api.github.com/repos/EQ-bench/EQ-bench-site/commits?per_page=100&until=2026-07-27T00:00:00Z"
               f"&path=eqbench4/eqbench4_docs/transcripts/{slug}/index.json")
        with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "adele-data"})) as r:
            dates = [c["commit"]["author"]["date"] for c in json.load(r)]
        cached[slug] = [min(dates), max(dates), len(dates)]
        DATES.write_text(json.dumps(cached, indent=1))
    return cached


def leaderboard_js() -> dict:
    s = (SITE / "eqbench4" / "eqbench4_data.js").read_text(encoding="utf-8")
    return json.loads(s[s.index("{"):s.rindex("}") + 1])


def main() -> None:
    checkout()
    ids = {d["id"] for d in json.loads(DATASET.read_text(encoding="utf-8"))["docs"]}
    persona_ids = {d["id"] for d in json.loads((DOCS / "personas.json").read_text(encoding="utf-8"))["docs"]}
    assert ids == persona_ids and len(ids) == 120
    lb = leaderboard_js()
    rows = []
    for m in lb["models"]:
        slug = m["slug"]
        index = json.loads((DOCS / "transcripts" / slug / "index.json").read_text(encoding="utf-8"))
        for e in index["transcripts"]:
            x = json.loads((DOCS / "transcripts" / slug / e["file"]).read_text(encoding="utf-8"))
            assert x["scenario_id"] in ids and x["evaluated_model"] == m["model"]
            turns = x["turns"]
            r = {"instance_id": x["scenario_id"], "model": m["model"], "slug": slug, "file_index": x["i"],
                 "persona_model": x["persona_model"], "pointwise_judge": x.get("pointwise_judge_model"),
                 "n_messages": len(turns),
                 "n_assistant_turns": sum(t["role"] == "assistant" for t in turns),
                 "final_status": x["final_status"],
                 "ended_early": len(turns) < 2 * x["num_turns"]}
            r.update({f"trait_{k}": v for k, v in (x.get("dims") or {}).items()})
            r.update({f"ability_{k}": v for k, v in (x.get("abilities") or {}).items()})
            r["ability_score"] = x.get("ability_score")
            r["ability_samples_total"] = sum((x.get("ability_samples") or {}).values())
            rows.append(r)
    df = pd.DataFrame(rows)
    assert not df.duplicated(["instance_id", "model"]).any()
    nat = df["trait_naturalness_authenticity"]
    df["success_nat7"] = (nat >= NAT_THRESHOLD).astype(int)
    df = df.sort_values(["model", "instance_id"])
    df.to_csv(HERE / "outcomes.csv", index=False)

    # Leaderboard and reproduction checks.
    elo_h = json.loads(ELO_FILE.read_text())["model_ratings"]
    dates = site_dates([m["slug"] for m in lb["models"]])
    g = df.groupby("model")
    out = []
    for m in lb["models"]:
        mm = df[df.model == m["model"]]
        row = {"model": m["model"], "slug": m["slug"], "rank": m["rank"], "elo": m["elo"],
               "ci_low": m["ci_low"], "ci_high": m["ci_high"], "elo_harness": elo_h[m["model"]]["elo"],
               "n_scenarios_leaderboard": m["n_scenarios"], "n_scenarios": len(mm),
               "n_with_ability": int(mm.ability_score.notna().sum()),
               "site_first_commit": dates[m["slug"]][0][:10], "site_last_commit": dates[m["slug"]][1][:10],
               "pointwise_judge": ";".join(sorted(mm.pointwise_judge.dropna().unique())),
               "ended_early_rate": round(mm.ended_early.mean(), 3),
               "naturalness_mean": round(mm.trait_naturalness_authenticity.mean(), 3),
               "success_nat7_rate": round(mm.success_nat7.mean(), 3),
               "ability_score_item_mean": round(mm.ability_score.mean(), 3),
               "ability_score_leaderboard": round(np.mean(list(m["abilities"].values())), 3)}
        row["max_abs_trait_diff"] = round(max(abs(mm[f"trait_{k}"].mean() - v) for k, v in m["dims"].items()), 4)
        row["max_abs_ability_diff"] = round(max(abs(mm[f"ability_{k}"].mean() - v) for k, v in m["abilities"].items()), 3)
        out.append(row)
    L = pd.DataFrame(out)
    L.to_csv(HERE / "leaderboard.csv", index=False)

    print(f"{len(df)} rows, {df.instance_id.nunique()} scenarios, {df.model.nunique()} models; "
          f"missing cells {120 * df.model.nunique() - len(df)}; no ability score {df.ability_score.isna().sum()}")
    print(f"site Elo vs harness elo_results.json: max |diff| {(L.elo - L.elo_harness).abs().max():.3f}")
    print(f"trait means vs leaderboard: max |diff| {L.max_abs_trait_diff.max():.4f} (rounding)")
    print(f"item-mean abilities vs leaderboard (pooled): max |diff| {L.max_abs_ability_diff.max():.3f}, "
          f"Pearson r of ability_score {L.ability_score_item_mean.corr(L.ability_score_leaderboard):.3f}")
    print("Spearman with Elo:", {c: round(L.elo.corr(L[c], method="spearman"), 2) for c in
                                 ["naturalness_mean", "success_nat7_rate", "ability_score_item_mean", "ended_early_rate"]})


if __name__ == "__main__":
    main()
