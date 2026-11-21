"""Pre-registered analysis of gamearena-plms. Writes results/analysis.json.

Labels: mass run gamearena-plms (PLp, PLe, PLs, MSm, MSc on 24 game x role instances; Opus 5.5 low, v2 prompt); only
valid answers written by claude-opus-5-5 count. Game Arena has no outcome that compares across games (no fixed
baseline; ../gamearena-data/NOTES.md), so there is no difficulty test. Two parts:

1. Demand profiles (descriptive, with sealed predictions): levels per instance; a game's demand is the mean over its
   roles.
2. Ability test. Games: every per-game leaderboard with at least 20 models (so not werewolf, chess-text-openings or
   the aggregate board). Each model's score is z-scored within a game, across that leaderboard's models. A game's
   social demand is the mean of its MSm and MSc. Per model on at least 10 such games: `social_edge` = Spearman, across
   games, of the model's z with the game's social demand. Primary: Spearman of social_edge with the model's EQ-Bench 4
   Elo, over models on both (predicted positive). Secondary: the same with the model's mean z over games of social
   demand 0 (a general-skill control; expected weaker than the primary).

    python experiments/benchmarks/gamearena-plms/analysis/analyse.py
"""

import importlib.util
import json
from pathlib import Path

import pandas as pd
from scipy.stats import spearmanr

HERE = Path(__file__).resolve().parents[1]
BENCH = HERE.parent
DIMS = ["PLp", "PLe", "PLs", "MSm", "MSc"]
MODEL = "claude-opus-5-5"
RUN = BENCH / "mass-annotation/runs/gamearena-plms/labels.csv"
MIN_MODELS, MIN_GAMES = 20, 10
# Game Arena model name -> EQ-Bench 4 slug (../eqbench4-data/leaderboard.csv). Fable 5.1 (Game Arena) is not Fable 5.
EQ4 = {"Claude Opus 5": "claude-opus-5", "Claude Opus 4.8": "claude-opus-4-8", "Claude Opus 4.7": "claude-opus-4-7",
       "Claude Opus 4.6": "claude-opus-4-6", "Claude Sonnet 5": "claude-sonnet-5", "Claude Sonnet 4.6": "claude-sonnet-4-6",
       "Claude Haiku 4.5": "claude-haiku-4-5-20251001", "GPT-5.5": "openai_gpt-5.5", "GPT-5.4": "openai_gpt-5.4",
       "GPT-5.6 Sol": "openai_gpt-5.6-sol", "GPT-5.6 Terra": "openai_gpt-5.6-terra", "GPT-5.6 Luna": "openai_gpt-5.6-luna",
       "Gemini 3.1 Pro Preview": "google_gemini-3.1-pro-preview", "Gemini 3.5 Flash": "google_gemini-3.5-flash",
       "Grok 4.3": "x-ai_grok-4.3"}

_spec = importlib.util.spec_from_file_location("swepl_analyse", BENCH / "swebench-pl/analysis/analyse.py")
_swepl = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_swepl)
rho = _swepl.rho


def main() -> None:
    lab = pd.read_csv(RUN, dtype={"instance_id": str})
    lab = lab[lab["valid"].astype(bool) & lab["writer_model"].astype(str).str.startswith(MODEL)]
    inst = lab.assign(d=lab["rubric_ref"].str.removeprefix("v2/")).pivot(
        index="instance_id", columns="d", values="level").reindex(columns=DIMS)
    inst["game"] = inst.index.str.split("@").str[0]
    game = inst.groupby("game")[DIMS].mean()
    game["social"] = game[["MSm", "MSc"]].mean(axis=1)

    lb = pd.read_csv(BENCH / "gamearena-data/leaderboards.csv")
    n_models = lb.groupby("game")["model"].nunique()
    games = [g for g in n_models.index if n_models[g] >= MIN_MODELS and g in game.index and g != "game-arena"]
    lb = lb[lb["game"].isin(games)].copy()
    lb["z"] = lb.groupby("game")["lb_score"].transform(lambda s: (s - s.mean()) / s.std())
    lb = lb.join(game["social"], on="game")
    edge, base = {}, {}
    for m, g in lb.groupby("model"):
        if len(g) >= MIN_GAMES and g["social"].nunique() > 1:
            edge[m] = spearmanr(g["z"], g["social"])[0]
        zero = g[g["social"] == 0]
        if len(zero):
            base[m] = zero["z"].mean()
    eq = pd.read_csv(BENCH / "eqbench4-data/leaderboard.csv").set_index("slug")["elo"]
    mod = pd.DataFrame({"social_edge": pd.Series(edge), "nonsocial_mean_z": pd.Series(base)})
    mod["eq4_elo"] = [eq.get(EQ4.get(m)) for m in mod.index]
    both = mod.dropna(subset=["social_edge", "eq4_elo"])

    out = {"instances": inst[DIMS].astype("Int64").astype(object).where(inst[DIMS].notna(), None).to_dict("index"),
           "games": game.round(2).to_dict("index"),
           "ability_test": {"games": sorted(games), "n_models_with_edge": int(mod["social_edge"].notna().sum()),
                            "n_models_on_both": int(len(both)),
                            "primary_social_edge_vs_eq4_elo": rho(both["social_edge"], both["eq4_elo"], "positive"),
                            "secondary_nonsocial_z_vs_eq4_elo": rho(both["nonsocial_mean_z"], both["eq4_elo"],
                                                                    "positive"),
                            "models": both.round(3).to_dict("index")}}
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results/analysis.json").write_text(json.dumps(out, indent=2, default=str) + "\n")
    print(json.dumps(out["ability_test"], indent=1, default=str))
    print(game.round(2).to_string())


if __name__ == "__main__":
    main()
