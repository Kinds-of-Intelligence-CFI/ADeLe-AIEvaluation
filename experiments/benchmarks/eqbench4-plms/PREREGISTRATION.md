# eqbench4-plms — pre-registration

Committed and pushed before any label of runs `eqbench4-plms` and `eq4-outcome`.

**Question.** On EQ-Bench 4, a benchmark of 8-turn support conversations with a simulated person who hides a core
issue, do the social rubrics (MSm, MSc) and the planning rubrics (PLp, PLe, PLs) track how often frontier models get
the person to disclose it?

## Design

- **Tasks.** The 120 persona scenarios of EQ-Bench 4 (harness `EQ-bench/eqbench4` at `93dcb7f5`, dataset v0.17: 60
  generated, 60 hand-authored in 4 types of 15). Data and sources: `../eqbench4-data/NOTES.md`.
- **Prompt for the rubric labels.** What the tested model sees at the start (system prompt and the presenting
  message), then, in a labelled section, the persona simulator's hidden brief (core issue, things it knows deep down,
  trust and defence styles, sensitivities, preferences). This follows the tau2 precedent: the other party's
  instructions shape the demand. Median 14.1k chars, max 34.5k.
- **Why a new outcome.** The published per-scenario `ability_score` is a margin against neighbouring models from
  pairwise judging, so scenario difficulty cancels: its scenario means have a split-half correlation of −0.83 across
  models. It cannot test demand. Pablo chose (2026-10-03) to judge a new, absolute outcome.
- **Outcome.** Per (scenario, model) transcript, an outcome judge reads the persona's hidden core issue and deep-down
  items and the spoken dialogue (no model name, no persona inner monologue, no EQ-Bench scores), and answers
  `CORE: yes | partly | no` (did the person openly acknowledge the core issue in their own words?) and, per item,
  `A<k>: yes | no` (did the person voice it?). Prompt: `make_outcome_prompts.py`. **Success = CORE yes.** Scenario
  outcome: `disclosure_rate`, the share of the 10 models whose transcript is a success. Secondary: `acknowledged_rate`
  (yes or partly) and `items_rate` (deep-down items voiced, pooled over models).
- **Models.** Ten of the 28, across the Elo range (1385 to 993) and six families: Claude Opus 5, Kimi K3, GPT-5.5,
  GPT-5.6 Sol, Claude Sonnet 5, GLM-5.2, DeepSeek V4 Pro, Gemini 3.1 Pro, Gemini 3.5 Flash, Mistral Medium 3.5. One
  transcript each per scenario (the published canon run; persona played by Gemini 3.1 Pro).
- **Judges.** Both runs: Claude Opus 5.5 at effort low as Claude Code subagents. Labels: run `eqbench4-plms` via
  `adele mass` (600 calls; PLp text O). Outcome: run `eq4-outcome`, agents `eq-outcome-judge` / `eq-outcome-dispatcher`
  (1,200 calls plus 60 seeded repeats for reliability). Only answers written by claude-opus-5-5 count (writer check
  against the judge transcripts); one recorded retry for an answer by another model or one that does not parse.
- **Known biases.** Same-family judging: the outcome judge is a Claude model and two of the ten models are Claude.
  Blinding hides model names, not style. The persona simulator is a Gemini model.
- **Analysis** (`analysis/analyse.py`, tested on synthetic labels). Spearman (swebench-pl's `rho`), each rubric
  predicted negative. Primary: MSm and MSc against `disclosure_rate` within source type (generated, hand-authored),
  combined by Fisher z (tau2-tb4-pl's `combined`). Secondary: PLp, PLe, PLs the same way; every rubric against the two
  secondary outcomes; all 120 pooled. Checks: outcome-judge repeatability on the 60 repeats (CORE exact agreement,
  kappa); model-level disclosure rate against EQ-Bench 4 Elo (n = 10, predicted positive).

## Predictions (sealed)

Priors: every scenario is social, so MSm and MSc should sit high with modest spread; on tau2 they sat at 2 and did not
track difficulty. Disclosure depends on the persona's defences, which the brief makes visible to the rubric judge.

- Median MSm at least 3: 0.85.
- Median MSc at least 3: 0.8.
- MSm takes at least two levels with 15 or more scenarios each: 0.6.
- MSm against disclosure rate, within source, negative with p < 0.05: 0.3.
- MSc against disclosure rate, within source, negative with p < 0.05: 0.3.
- PLp against disclosure rate, within source, negative with p < 0.05: 0.15.
- Outcome repeatability: CORE exact agreement at least 0.8: 0.7.
- Model-level disclosure rate against Elo positive with p < 0.05: 0.5.

**Cost.** 1,860 Opus-low calls, about 10 weekly points.
