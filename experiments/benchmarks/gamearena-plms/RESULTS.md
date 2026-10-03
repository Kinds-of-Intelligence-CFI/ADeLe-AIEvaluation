# gamearena-plms — results

**Question.** How do the planning and social rubrics profile the games of Kaggle Game Arena, and does a model's edge on
the games with high social demand match its rating on EQ-Bench 4, a separate social benchmark?

**Answer.** The profiles mostly make sense, but the ability test finds nothing. MSc is 0 on every board game and 4 on
the three werewolf village roles and bargaining. MSm also rises on some board games where the opponent's intent
matters (dark hex 3, with hidden stones). A model's edge on social games does not track its EQ-Bench 4 Elo (ρ = +0.01,
n = 14); its general board-game skill tracks it more (+0.45, not significant).

**Status.** Complete (2026-10-03). 120 cells (24 game × role instances × 5 rubrics), all labelled by Opus 5.5 at effort
low, check OK. Four of eight sealed predictions held.

## Design

See `PREREGISTRATION.md`, pushed before any label (`6256356`). 24 instances from 19 games; prompt = the exact harness
prompt of one early decision. No difficulty test: no game has a fixed baseline, so games cannot be ordered by
difficulty. Ability test on the 17 per-game leaderboards with at least 20 models.

## Pre-registered results

From `results/analysis.json` (`analysis/analyse.py`).

**Profiles** (level per instance; PLe is 0 everywhere except word-art artist, 3).

| instance | PLp | PLs | MSm | MSc |
|---|---|---|---|---|
| chess, chess openings, go, reversi | 1 | 2 | 0 | 0 |
| clobber, five-in-a-row | 3 | 2 | 0 | 0 |
| four-in-a-row | 3 | 2 | 1 | 0 |
| lines of action | 3 | 2 | 2 | 0 |
| dark hex | 3 | 2 | 3 | 0 |
| checkers / dots and boxes | 2 / 1 | 2 / 1 | 1 | 0 |
| nine men's morris / ultimate tic-tac-toe | 2 | 2 | 2 | 0 |
| poker heads-up | 1 | 1 | 2 | 0 |
| coin game | 2 | 2 | 3 | 0 |
| bargaining | 2 | 2 | 3 | 4 |
| word association: cluemaster / guesser | 2 / 0 | 1 | 3 / 2 | 1 |
| word art: artist / guesser | 2 / 1 | 1 / 0 | 3 | 1 |
| werewolf: villager / seer / doctor | 1 / 2 / 1 | 2 / 3 / 3 | 4 | 4 |
| werewolf: werewolf (night kill) | 0 | 1 | 2 | 0 |

**Ability test** (14 models on both leaderboards):

| | ρ | 95% CI | p |
|---|---|---|---|
| social edge against EQ-Bench 4 Elo (primary) | +0.01 | [−0.53, +0.54] | 0.98 |
| general board-game skill against EQ-Bench 4 Elo | +0.45 | [−0.13, +0.80] | 0.11 |

**Sealed predictions.**

| prediction | p | outcome |
|---|---|---|
| all 13 board games MSc 0 and MSm at most 1 | 0.65 | failed (MSm 2–3 on dark hex, lines of action, nine men's morris, ultimate tic-tac-toe) |
| MSm ≥ 3 on at least 3 of 4 werewolf roles | 0.6 | held (4, 4, 4; wolf 2) |
| MSc ≥ 3 on at least 3 of 4 werewolf roles | 0.55 | held (4, 4, 4; wolf 0) |
| word association: both roles MSm ≥ 2 | 0.6 | held (3, 2) |
| werewolf has the highest social demand of the 19 games | 0.5 | failed (bargaining 3.5, werewolf 3.25) |
| median PLp of board games ≥ that of the other games | 0.65 | held (2 against 1.25) |
| social edge against Elo positive, p < 0.05 | 0.15 | did not happen (+0.01) |
| its ρ above the general-skill ρ | 0.5 | did not happen (+0.01 against +0.45) |

## Reading

- **MSc behaves as its rubric says.** It is 0 wherever there is no talk, including the wolves' night kill, and high only
  where what is said depends on others (werewolf day talk, bargaining offers).
- **MSm reads opponent modelling in adversarial games.** Hidden information (dark hex, poker) and games where one
  anticipates the opponent's threats get 2–3. Whether that should count as mind modelling is a construct question:
  the rubric reads beliefs and intentions of another agent, and a game opponent is one.
- **PLp is low on chess and go** (1). Each prompt is one move with the board, and the judge rates the decision, not
  the game; long-horizon planning over a whole game is not in the prompt.
- **The ability test is null.** With 14 models and a few social games per leaderboard, it was weak by design. General
  game skill relates to EQ-Bench 4 at least as much as social edge does, so the leaderboards do not isolate a social
  ability here.

## Deviations and caveats

- No deviations.
- One prompt per instance (a single early decision). Demand over a whole game is not labelled.
- Leaderboards are relative ratings read on 2026-10-03; their model sets differ by game.
