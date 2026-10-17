# gamearena-plms — pre-registration

Committed and pushed before any label of run `gamearena-plms`.

**Question.** How do the planning and social rubrics profile the games of Kaggle Game Arena, and does a model's edge on
the games with high social demand match its rating on EQ-Bench 4, a separate social benchmark?

## Design

- **Tasks.** 24 game × role instances from 19 games (13 two-player board games, poker, bargaining, coin game, word
  art, word association, werewolf with 4 roles). Data and sources: `../gamearena-data/NOTES.md` (Kaggle datasets,
  CC BY 4.0; harness repos Apache-2.0).
- **Prompt.** The exact prompt the harness sent for one early decision (the role's second decision in the most recent
  sampled episode), as kept in the episode log: rules, observation and action format. 475–7,740 chars of task text.
- **Why no difficulty test.** No game has a fixed baseline (random agent, engine, scripted bot), and the absolute
  scores that exist (coin-game points, word hit rates, werewolf vote accuracy, bargaining payoffs) are on different
  scales. Average win rate in a symmetric game is 0.5 by construction. So games cannot be ordered by difficulty.
  Pablo chose (2026-10-03) labels plus a model-level ability test.
- **Labels.** PLp (text O), PLe, PLs, MSm, MSc; Opus 5.5 low, v2 prompt; run `gamearena-plms` via `adele mass` (120
  calls). A game's demand is the mean over its roles.
- **Ability test** (`analysis/analyse.py`, tested on synthetic labels). Games: every per-game leaderboard with at least
  20 models (17 games; not werewolf, 8 models, nor chess-text-openings, a closed old run). Each model's leaderboard
  score is z-scored within a game. A game's social demand is the mean of its MSm and MSc. Per model on at least 10
  games: `social_edge`, the Spearman correlation across games of the model's z with social demand. Primary: Spearman
  of `social_edge` with EQ-Bench 4 Elo over the models on both (14 expected; mapping in the script), predicted
  positive. Secondary: the same with the model's mean z on games of social demand 0 (general game skill). The test is
  weak by design: 14 models, and each edge rests on a few social games. The leaderboards are relative ratings
  (`../gamearena-data/leaderboards.csv`, read 2026-10-03).

## Predictions (sealed)

Each prompt is one decision with its rules, which is what the judge rates.

- All 13 board games have MSc 0 and MSm at most 1: 0.65.
- MSm at least 3 on at least 3 of the 4 werewolf roles: 0.6.
- MSc at least 3 on at least 3 of the 4 werewolf roles: 0.55.
- Word association: both roles have MSm at least 2: 0.6.
- Werewolf has the highest mean of MSm and MSc of the 19 games: 0.5.
- Median PLp of the board games at least the median PLp of the other six games: 0.65.
- `social_edge` against EQ-Bench 4 Elo positive with p < 0.05: 0.15.
- Its ρ above the secondary (general game skill) ρ: 0.5.

**Cost.** 120 Opus-low calls, under 1 weekly point.
