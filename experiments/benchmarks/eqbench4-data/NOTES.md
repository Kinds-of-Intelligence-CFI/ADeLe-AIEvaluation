# EQ-Bench 4: scenarios, prompts, outcomes

Benchmark slug: `eqbench4`. Fetched 2026-10-03. Data only: no judge calls, no labels.
EQ-Bench 4 (Sam Paech) runs 120 persona scenarios. Each is an 8-turn roleplay chat between the tested
model and a simulated person played by Gemini 3.1 Pro Preview.

## Sources and revisions

| What | Source | Revision | Licence |
|---|---|---|---|
| Harness, prompt templates, dataset (`src/eqbench/datasets/test.json`, v0.17), Elo file, judge-bias report | github.com/EQ-bench/eqbench4 | `93dcb7f5` (2026-09-26, "add license") | BSD-3-Clause + Commons Clause (no selling), Samuel J. Paech |
| One raw run file, used only to check prompt rendering | same repo, `results/r23.json` (Claude Haiku 4.5, 20 MB) | `93dcb7f5` | same |
| Per-(scenario, model) scores, transcripts, `personas.json`, leaderboard `eqbench4_data.js` | github.com/EQ-bench/EQ-bench-site, folder `eqbench4/` | `033fc135` (2026-07-26, last commit touching `eqbench4/`; HEAD `108382e3` of 2026-09-24 has the same files) | **none** (no licence file) |
| Site commit dates per model | GitHub REST API, commits on `transcripts/<slug>/index.json` | read 2026-10-03 | |

- The scout was right on the counts: 120 scenarios, 28 models. It was wrong on one point:
  `ability_score` is **not** an Opus 4.8 score. Opus 4.8 gives the pointwise trait scores. The
  abilities come from pairwise judging (see "Outcomes").
- The harness repo is public. Its README links to a different source repo (`LimLims/eqbench4_public`).
  I did not check that one.
- The licence was added on 2026-09-26, after all runs. It covers the harness repo, so also its
  `test.json` and `results/`. The site repo has no licence.
- Whom to ask: Sam Paech (licensor; owner of the EQ-bench GitHub org).
- Nothing was gated. No login. I did not fetch eqbench.com pages; all data came from GitHub.
- Downloads: about 290 MB under `data/downloads/eqbench4/` (site `eqbench4/` 171 MB, harness 99 MB,
  `r23.json` 19 MB). The other 31 raw run files (`results/r25.json` to `r60.json`, 1.83 GB) hold the
  pairwise verdicts. They were **not** downloaded (size rule).
- Harness code was **not** run (it is external code). The prompt builders were re-implemented in
  `fetch_tasks.py` and checked byte for byte against `r23.json`.

## What the tested model sees

From `src/eqbench/core/conversation_runner.py` and `core/prompts.py` at `93dcb7f5`:

- The tested model speaks first. Its turn-1 messages are: a system prompt, then one user message
  `[Presenting issue (what begins this conversation): "<presenting text>"]`.
- System prompt (`prompts/evaluated_system_prompt.txt`) opens with
  "You are participating in a roleplay scenario as part of an EQ evaluation." It names the role
  (friend, partner, chatbot, employee ...), says there are 8 turns each and which turn it is, gives
  the person's demographics and the presenting text, and lists goals (support, build trust, learn
  what they want and need, help them gain insight). It ends with "Respond only with dialogue".
- For `chatbot` scenarios (67 of 120) it adds a short "CHATBOT RELATIONSHIP CONTEXT" paragraph.
- For hand-authored scenarios the presenting text is `[scenario background] ... [user message] ...`.
  So the model gets a short public set-up as well as the opening line.
- The system prompt is rebuilt each turn (only the turn counter changes). The model sees the
  persona's spoken dialogue only, never its inner monologue.

## What the persona simulator sees

- `prompts/persona_system_prompt_no_state_no_unlock.txt` (or the `no_core_issue` variant). This is
  the "canon" variant: no numeric emotional state, no reveal schedule.
- It holds: demographics, background, personality traits; the presenting issue; the hidden core issue
  ("SITUATION CONTEXT", or "SCENARIO DYNAMIC" for hand-authored); "THINGS YOU MAY KNOW DEEP DOWN"
  (adjacent attributes with LOW/MEDIUM/HIGH admission thresholds); trust style; defence style; verbal
  sophistication; sensitivities; preferences; and behaviour rules ("Don't make it easy",
  "Lean into your adversarial traits").
- Hand-authored scenarios add a long task context and a character card (persona tags, hidden local
  state to track, backfire tendencies).
- Each turn it writes `<internal>`, `<dialogue>` and `<status>` (`active` or `ended`). It may end
  the chat early.
- The help-seeking stance is in the dataset but no template has a slot for it. In generated
  scenarios neither the simulator nor the judges see it. Hand-authored cards show a one-line marker.

## Instances

`data/instances/instances_eqbench4.parquet` (gitignored): 120 rows. `instance_id` = the dataset's
scenario id (36-char UUID for generated scenarios, `hand_<type>_<n>_<slug>_<hash>` for hand-authored).
`prompt` = a one-line header, then `=== WHAT THE TESTED MODEL SEES AT THE START ===` (turn-1 system
prompt + first user message), then `=== HIDDEN FROM THE TESTED MODEL: the persona simulator's system
prompt ... ===`. No transcript.

`data/instances/meta_eqbench4.csv`: source type, task type, title, relationship, presenting and core
issue ids, core category, trust, defence, help-seeking and verbal styles, age, gender, sensitivities,
preferences, `num_turns` (8 for all), `prompt_chars`, `seen_chars`, `persona_prompt_chars`.

Composition: 60 generated (random draws from a registry of issues, traits and modifiers) and 60
hand-authored, 15 each of `ego_threat_accountability`, `power_imbalanced_navigation`,
`reality_distortions`, `social_exclusion_ambiguous_rejection`.

Prompt length (chars), whole prompt: min 9,377; median 14,104; p90 22,520; max 23,159. None exceed
24k. The part the model sees is small (median 3,561, max 4,130). The persona prompt is most of it:
median 6,374 for generated and 14,995 for hand-authored.

## Outcomes

`outcomes.csv` here: one row per (scenario, model). 3,357 rows = 120 x 28 minus 3 missing cells
(minimax-m3, muse-spark-1.1, claude-opus-4-6 each miss one scenario). Columns: ids, `persona_model`,
`pointwise_judge`, `n_messages`, `n_assistant_turns`, `final_status`, `ended_early`, 8 `trait_*`,
6 `ability_*`, `ability_score`, `ability_samples_total`, `success_nat7`. No text.
`leaderboard.csv`: one row per model, with Elo, CI, site commit dates and the checks below.

### What the scores are

1. **Leaderboard Elo.** Pairwise. A judge sees two models' transcripts on the same scenario, plus the
   hidden persona profile and the persona's inner monologue. It picks a winner and a margin (`+` to
   `+++++`, or tie) on 6 abilities (bond and rapport, authenticity, attunement, meeting preferences and
   needs, emotion sensemaking, emotion management; equal weights). Both orders are judged. Judges:
   Claude Opus 4.6, GPT-5.5, Gemini 3.1 Pro Preview. Margins become fractional outcomes, then a soft
   Bradley-Terry fit on the Elo scale. The config lists anchors o3 = 1500 and Llama 3.2 1B = 200;
   neither is among the 28 models, so how the scale is pinned is unclear to me. 10,690 comparisons,
   21,366 judge verdicts. Matchups are mostly between rank neighbours (+-1 to 3).
2. **Per-scenario `abilities` / `ability_score`** (site, `export_to_site.py`). For one scenario and
   one model: the mean signed margin against its Elo neighbours (up to 4 ranks each side, balanced,
   one-sided at the ends). Scale -5 to +5. Positive = beat its neighbours on this scenario. It is
   **relative by construction**. It is recomputed whenever a model is added.
3. **Per-transcript `dims` (traits)**. One pointwise judge (Claude Opus 4.8; Opus 4.6 for grok-4.3)
   scores 12 tendencies 0-10; the site shows 8 (`yielding` merges yielding and frame capture).
   The README says they are "neutrally valenced tendencies, not abilities". They do not enter the
   leaderboard.
4. **Persona emotional state.** The README says the persona updates trust, anger, shame each turn.
   In the canon runs it does not: `state_history` is empty in `r23.json`, and the code says the canon
   prompt "does not emit numeric persona state". So there is no state-change outcome.
5. **Early ending.** `ended_early` = fewer than 16 messages. 1,397 of 3,357 (42%).

### Verification

- Site Elo vs harness `results/elo_results.json`: max difference 0.05 (rounding). Snapshot
  2026-07-26, 28 models.
- Trait means per model from `outcomes.csv` equal the leaderboard's trait profile (max diff 0.005,
  rounding). Exact match.
- Abilities: per-model means of the per-scenario values track the leaderboard's pooled
  neighbour abilities (r = 0.87 to 0.97 per ability; 0.89 for the mean; max diff 0.36). Not exact,
  as expected: the leaderboard pools all comparisons before culling.
- **The Elo itself cannot be rebuilt from per-scenario scores.** It needs the pairwise verdicts in
  `r25.json`..`r60.json` (1.83 GB), not downloaded. The judge-bias report re-solves it per judge;
  per-judge rankings agree with the pooled one (Spearman 0.97 to 0.99).
- Haiku 4.5: the 120 site transcripts equal the conversations in `r23.json` (first message, all 120).
  But `r23.json` still holds Opus 4.6 trait scores; the site has Opus 4.8 re-judgements.

### Distribution and what it means for ADeLe

- `ability_score`: mean 0.01, SD 1.81, range -5 to 4.67. Variance share: model 0.6%, scenario 0.3%,
  residual 99%. Split-half (odd vs even Elo rank) correlation of scenario means: **-0.90**
  (neighbours are of opposite parity; the scores are zero-sum). Model means vs Elo: Spearman 0.01.
  **It carries no scenario difficulty and no model ability.** Pairwise judging on the same scenario
  cancels scenario difficulty; it is not identifiable from these data.
- 145 cells have no ability score: 72 each for Opus 5 and Fable 5 (the top two), 1 Inkling.
- `trait_naturalness_authenticity` (0-10): values 2-9, never 10; mean 6.21, SD 1.45. No hard floor or
  ceiling (7 cells at 2, 100 at 9). Variance share: model 29%, scenario 26%, residual 45%. Scenario
  means split-half r = 0.90 (Spearman-Brown 0.95). Model means vs Elo: Spearman 0.81.
- `success_nat7` (naturalness >= 7): 47% of cells. Per scenario: mean 0.47, SD 0.22, range 0 to
  0.96; 1 scenario never succeeds, none always; 4 at <= 0.1, 4 at >= 0.9. Split-half r = 0.81.
  Model rates 0.10 (Qwen 3.6 27B) to 0.93 (Opus 5); Spearman with Elo 0.78.
- By scenario type (success_nat7): ego-threat 0.30, reality distortions 0.43, generated 0.42,
  power-imbalanced 0.60, social exclusion 0.75.
- `ended_early`: mostly a scenario property (46% of variance), rarely a model one (4%). Model rates
  correlate **positively** with Elo (Spearman 0.62). So an early end is often a natural close, not a
  walk-out. It is not a failure signal. Hand-authored 64%, generated 19%.

### Proposed outcome

- **Continuous:** `trait_naturalness_authenticity`. It is absolute, per transcript, reliable at the
  scenario level, spread out, and tracks the pairwise Elo (0.81). The judge saw the hidden persona
  profile and inner monologue.
- **Binary:** `success_nat7` (>= 7). It is close to the median (6-7), so it gives the most balanced
  split (47%). >= 6 gives 66%, >= 8 gives 21%.
- Caveat: the benchmark author calls this trait a tendency, not a quality score. It is one judge's
  view. It is the best absolute outcome in the public data, not a validated one.

## Known issues

- **No absolute ability outcome is published.** The leaderboard is relative. See "Decisions".
- **Same-family judging.** Opus 4.8 scores traits for 8 Claude models (and itself). Model-mean
  naturalness minus the Elo-predicted value: Claude +0.28, OpenAI -0.61, others +0.05. This fits a
  family bias, or a style preference; cannot tell which. Pairwise self-bias (judge-bias report, margin
  points): GPT-5.5 +4.09, Gemini 3.1 Pro +3.20, Opus 4.6 +1.71 for their own model. GPT-5.5 ranks
  GPT-5.6 Luna 14th vs 19th pooled.
- **Gemini 3.1 Pro Preview is the persona, a pairwise judge and a tested model.**
- **Mixed trait judge.** grok-4.3 was scored by Opus 4.6, all others by Opus 4.8.
- **One run per cell.** `convos_per_scenario = 1`. No repeats; no within-cell variance estimate.
- **Adversarial filtering.** Dataset v0.17 dropped the 15 generated scenarios on which Haiku 4.5
  scored highest (v0.16 pointwise), and all 15 `constrained_truth` hand-authored ones. Difficulty was
  selected on an outcome of one model.
- **Run dates unknown for most models.** Site commit dates: first models 2026-06-07; Opus 5
  2026-07-24; Muse Spark 1.1 and MiMo v2.5 Pro 2026-07-26. Haiku 4.5 ran 2026-06-01 (`r23.json`).
  Dates for others are in the raw run files, not downloaded.
- **Neighbour-relative scores drift.** Every export re-sorts the ladder, so `ability_score` changes
  when models are added.
- **The model knows it is an EQ evaluation** (first line of its system prompt).
- **The help-seeking stance** is in the dataset but in no generated-scenario prompt.

## Decisions for Pablo

1. **Outcome.** Use `trait_naturalness_authenticity` (continuous) and `success_nat7` (binary)?
   I recommend yes, with the caveats above. Do not use `ability_score` or `ended_early`.
2. **A real absolute outcome would need new judge calls**: e.g. score the 3,357 public transcripts
   pointwise on EQ-Bench's own 6 abilities, with a non-Claude or mixed judge. Out of scope here; your
   call.
3. **Pairwise data (1.83 GB).** Only needed to rebuild the Elo or to study discrimination (does the
   strong-weak gap grow with demand). Fetch it, or skip? I would skip unless (2) is rejected.
4. **Persona spec in the judge prompt.** I recommend yes (as in tau2). The hidden spec is where MSm
   demand lives (what the persona hides, how it defends). The visible part alone is about 3.5k chars
   and nearly identical across scenarios. Option: drop the generic "HOW TO RESPOND" block of the persona
   prompt (about 2.0-2.2k chars, same for all) to cut length. I kept it verbatim.
5. **Drop grok-4.3** (different trait judge) or keep and flag?
6. **Committing numbers.** `outcomes.csv` and `leaderboard.csv` hold ids and numbers only. The same
   numbers sit in the BSD-licensed harness repo (`results/`) for most models. I think committing is
   fine. If you prefer caution, move `outcomes.csv` to `data/raw/eqbench4/` and commit only
   `leaderboard.csv`.
7. **EQ-Bench 3 for spread** (only noted, not fetched): github.com/EQ-bench/eqbench3 (MIT) and
   `EQ-bench/eqbench-leaderboard-results` (no licence). If it publishes per-item rubric scores, they
   would be absolute outcomes. Not checked.
8. **Model ids.** The 28 models need `panel/models.csv` entries before any panel build.

## Rebuild

```
python experiments/benchmarks/eqbench4-data/fetch_tasks.py     # ~1 min; checks prompts vs r23.json
python experiments/benchmarks/eqbench4-data/fetch_outcomes.py  # ~1 min; 28 GitHub API calls first time
```
Not registered in `data/instances/INSTANCES.tsv`.
