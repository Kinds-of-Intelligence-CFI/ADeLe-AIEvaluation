# Kaggle Game Arena: tasks, model inputs and outcomes (fetched 2026-10-03)

Benchmark slug: `gamearena`. Data only: no judge calls, no labels.
Kaggle Game Arena is run by Google DeepMind and Kaggle. LLMs play games against each other
through one text harness. Paper: arXiv 2609.31473v1 (Doerschuk-Tiberi, Yan, ... 2026-09-25),
"Game Arena: Strategic LLM Evaluation in Competitive Environments". The paper covers only
chess, poker and werewolf, with 10-11 models from February 2026. The live arena is much
larger: 19 game datasets and leaderboards, 8-32 models each.

## Sources

| What | Where | Pinned | Licence |
|---|---|---|---|
| Episode logs | Kaggle datasets `kaggle/<game>-gameplay`, one JSON per episode | dataset version per game in `data/instances/meta_gamearena.csv` (most last updated 2026-09-17) | CC BY 4.0 (API `licenseName`, all 19 used) |
| Live harness (all games) | https://github.com/Kaggle/kaggle-environments | `eb8b5ef905cb066babf8bfcd776540d0e9dd8fa6` (2026-10-02, v1.33.0) | Apache-2.0 (LICENSE checked) |
| Original harness (chess, poker) | https://github.com/google-deepmind/game_arena | `6ddcc7dac06321472f2f22fabdeceab97eebeb73` (2026-02-02, last of 4 commits) | Apache-2.0 (LICENSE checked) |
| Leaderboards | `POST https://api.kaggle.com/v1/benchmarks.BenchmarksApiService/GetBenchmarkLeaderboard` (the call `kaggle b leaderboard` makes), slugs `kaggle/<game>` and `kaggle/game-arena` | fetched 2026-10-03 | not stated (see Licences) |
| Dataset list | `GET https://www.kaggle.com/api/v1/datasets/list` (anonymous) | 2026-10-03 | |
| Paper | arXiv 2609.31473v1 | v1 | |

How the logs were read. `GET /api/v1/datasets/download/kaggle/<slug>` answers anonymously with
a 302 to a signed `storage.googleapis.com` URL for the dataset zip. The scripts read only the
zip's central directory (exact episode counts) and then each sampled episode with one HTTP range
request. No whole dataset was downloaded. No login, no API key, no terms clicked.
Downloads: 1.07 GB of sampled episodes, ~10 MB of zip directories, 8 MB paper, ~0.7 GB of
partial git clones (on disk, with checkout). Total under 2 GB.

Other things tried: `/api/v1/datasets/view/...` and `/api/v1/datasets/list/<owner>/<slug>`
(file list) answer 403 without login. Not used.

## robots.txt

- `www.kaggle.com/robots.txt`: HTTP 404 (an HTML error page) for every user agent I tried.
  The Wayback Machine has only 404 snapshots of it since 2024. Under RFC 9309 a 4xx robots.txt
  means "no restriction". So `/api/v1/...` is not disallowed. I read it before any other request.
- `api.kaggle.com/robots.txt`: 404. `storage.googleapis.com/robots.txt`: 404 (NoSuchBucket).
- Both scripts check robots.txt (per host, `urllib.robotparser`) before every uncached request
  and refuse a disallowed URL. If Kaggle publishes a robots.txt later, it will be honoured.
- **Uncertainty.** A missing robots.txt is not a licence. Kaggle's Terms of Use (JS-rendered
  page, not read) may limit automated access. I believe they restrict automated access that
  exceeds what a human browser would send. My traffic was about 9,000 small range requests to
  Google Storage over ~1.5 hours, sequential, plus ~60 API calls with 1-2 s pauses. Please check
  the Terms before scaling up.
- **Disclosure.** While locating the leaderboard endpoint I made 3 GETs to
  `pypi.org/pypi/<pkg>/json` (kagglesdk, kaggle-environments). pypi.org's robots.txt disallows
  `/pypi/*/json`. I noticed only after the third. The scripts do not use PyPI. The kagglesdk
  wheel itself came from files.pythonhosted.org (robots.txt 404); I only read its source.

## Games and roles

Counts: episodes = non-empty members of the dataset zip (exact). Models = leaderboard rows.
"Harness dates" = release dates of the kaggle-environments versions seen in the sample
(`module_version` in each log, dated from the repo's pyproject history). Episode logs carry no
timestamp, except Werewolf (`created_at` 2026-03-20). So dates are a proxy only.

| game | players | roles (instances) | structure | hidden info | free text | models | episodes | harness dates (sample) |
|---|---|---|---|---|---|---|---|---|
| chess-text | 2 | player | zero-sum | no | no | 31 | 6,024 | 2025-12-03 .. 2026-08-14 |
| chess-text-openings | 2 | player | zero-sum, starts from 20 openings | no | no | 11 | 2,200 | 2025-12-12 only (old run) |
| checkers | 2 | player | zero-sum | no | no | 30 | 5,774 | 2026-05-27 .. 08-14 |
| clobber | 2 | player | zero-sum | no | no | 28 | 5,896 | 2026-05-27 .. 08-14 |
| dark-hex | 2 | player | zero-sum | yes (opponent stones) | no | 30 | 7,274 | 2026-05-27 .. 08-14 |
| five-in-a-row | 2 | player | zero-sum | no | no | 20 | 4,422 | 2026-02-13 .. 06-29 (retired?) |
| four-in-a-row | 2 | player | zero-sum | no | no | 32 | 10,875 | 2026-02-02 .. 08-14 |
| dots-and-boxes | 2 | player | zero-sum | no | no | 29 | 7,232 | 2026-05-27 .. 08-14 |
| go (13x13) | 2 | player | zero-sum | no | no | 28 | 7,576 | 2026-05-27 .. 08-14 |
| lines-of-action | 2 | player | zero-sum | no | no | 28 | 5,430 | 2026-07-08 .. 08-14 |
| nine-mens-morris | 2 | player | zero-sum | no | no | 28 | 6,094 | 2026-07-08 .. 08-14 |
| reversi | 2 | player | zero-sum | no | no | 28 | 6,426 | 2026-07-08 .. 08-14 |
| ultimate-tic-tac-toe | 2 | player | zero-sum | no | no | 28 | 8,942 | 2026-07-08 .. 08-14 |
| poker-heads-up | 2 | player | zero-sum, chance, 100 hands/episode, duplicate deals | yes (cards) | no | 31 | 38,854 | older than 1.25 .. 2026-08-14 |
| bargaining | 2 | player | general-sum; stated goal: higher payoff than opponent | yes (valuations) | no (structured offers) | 28 | 14,244 | 2026-05-27 .. 08-14 |
| coin-game | 4 | player | 2v2; each team = 2 copies of one model, on its own private board | yes (other board) | no | 27 | 4,970 | 2026-05-27 .. 08-14 |
| word-art | 4 | artist, guesser | 2v2; each team = 2 copies of one model; parallel rounds, team scores independent | yes (secret word) | yes (ASCII art, guesses) | 26 | 3,338 | 2026-07-23 .. 08-14 |
| word-association | 4 | cluemaster, guesser | 2v2 Codenames-like; each team = 2 copies of one model; shared board | yes (colours, guesser) | yes (one-word clues) | 30 | 6,094 | 2026-05-27 .. 08-14 |
| werewolf | 8 | werewolf, seer, doctor, villager | 2 wolves vs 6 village; models mixed at random per table | yes (roles) | yes (day discussion) | 8 | 30,101 | 2026-03-17 (one tournament) |

Notes on the list:
- The scout's "17-18 games" is close: 19 game leaderboards answer, plus `kaggle/game-arena`
  (aggregate, "Games Covered" up to 17 per model). The aggregate's game list is not published.
- `kaggle/werewolf-dataset` (6.8 GB) has the same 30,101 names but 22,653 members are empty
  files. I used `kaggle/werewolf-gameplay` (27 GB zip). The paper reports 31,472 werewolf
  games; this dataset has 30,101. Not explained.
- Old datasets exist (`chess-text-gameplay-old`, `-v2`, `chess-opening-gameplay-v2`,
  `four-in-a-row-gameplay-old`, `chess-text-openings-gameplay-old`). Not used.
- Model names in logs mix display names ("GPT-5.5") and slugs ("gpt-5.5-2026-04-23",
  "claude-fable-5-1-default"). The scripts map both to the leaderboard display name. Some
  1.30.1 chess games carry a "-<n>" suffix (e.g. "Grok 4-27"); the suffix is dropped.
  After mapping, every sampled name matches a leaderboard name.

## What the model sees

Each decision is one user message. The current harness sends no system prompt. The old-format
logs I checked (chess openings, poker) also hold a single user message. The message holds the instructions, the
rules, the current observation and the answer format. Legal moves are NOT listed. On an illegal
or unparsable answer the harness re-prompts with a short suffix; after the last attempt it
submits an invalid action and the player forfeits (OpenSpiel games). Current harness: 2
attempts in total (`core_harness.py`, `max_retries=2`). Old harness (chess 1.25.x): up to 4.
Poker instead remaps a second illegal action to check/fold. Werewolf has its own ReAct harness
(JSON with private reasoning and public action; a parse failure gives a skipped turn).

`data/instances/instances_gamearena.parquet` (24 rows; sha256 of file `2888480d269c...`):
`prompt` = a prompt the harness actually sent, read from the log
(`call_details[].prompt`; `generate_returns[].request_for_logging` in old logs;
`kwargs.raw_prompt` for Werewolf). Rule: most recent episode with saved prompts, the role's
SECOND decision, first attempt (so the board or history is not empty). Prompt lengths: 475
(chess) to 7,740 chars (werewolf seer); median 2,973. Prompts grow during a game (move
history; poker keeps the full 100-hand history; werewolf the full timeline).

Harness source per game (all at kaggle-environments `eb8b5ef`, except chess-text-openings):
`core_harness.py` (chess template `BASIC_PROMPT_TEMPLATE`, ported from game_arena),
`envs/open_spiel_env/games/<game>/harness.py` (checkers, clobber, dark_hex, connect_four for
both in-a-row games, dots_and_boxes, go, lines_of_action, nine_mens_morris, othello,
ultimate_tic_tac_toe, repeated_poker, bargaining, coin_game_arena), `envs/word_art/harness.py`,
`envs/word_association/harness.py`, `envs/werewolf/werewolf.py`. chess-text-openings used the
game_arena template `game_arena/harness/prompt_templates.py` (`6ddcc7d`).
A probe line from each template is found both in the pinned source and in the logged prompt for
all 24 instances (`probe_in_source`, `probe_in_prompt` in the meta file). This does not prove
the whole template is unchanged across versions.

Short quotes (templates are Apache-2.0):
- chess: "It is now your turn. Play your strongest move. The move MUST be legal. Reason step by
  step ... "Final Answer: X" where X is your chosen move in standard algebraic notation (SAN)."
- coin game: "every player on your team is another instance of YOU (same model, same
  submission) ... There is NO in-game communication".
- word art: "your score is independent of the other team's outcome for the round."
- bargaining: "Your goal is to end the game with a higher reward than your opponent."

`data/instances/meta_gamearena.csv`: game facts (table above), dataset version, licence,
episode counts and id range, leaderboard size, source episode / step / seat / model /
module_version, harness file and commit, probe checks, prompt length, episode configuration.

## Sample

Per game, non-empty episodes sorted by EpisodeId (a time proxy) are cut into 10 equal strata;
N/10 are drawn at random from each (seed 20261003). N = 500, except bargaining 800, dark-hex
800, go 300, chess-text-openings 300, word-art 300, werewolf 200, poker 120 (2.7 MB per
episode). The draw cannot see models, so counts per model vary. All 8,840 sampled episodes
parsed. Seat-games per model (median, range):

| instance | models | seat-games per model |
|---|---|---|
| chess-text | 31 | 33 (9-50) |
| chess-text-openings | 11 | 53 (44-63) |
| checkers | 30 | 33 (15-55) |
| clobber | 28 | 36 (15-54) |
| dark-hex | 30 | 55 (21-83) |
| five-in-a-row | 20 | 51 (21-78) |
| four-in-a-row | 31 | 33 (10-58) |
| dots-and-boxes | 29 | 32 (10-57) |
| go | 28 | 22 (8-32) |
| lines-of-action | 28 | 37 (17-51) |
| nine-mens-morris | 28 | 35 (14-57) |
| reversi | 28 | 37 (17-63) |
| ultimate-tic-tac-toe | 28 | 36 (12-58) |
| poker-heads-up | 31 | 7 (2-19) episodes of 100 hands |
| bargaining | 28 | 62 (15-84) |
| coin-game | 27 | 38 (16-52) team-games |
| word-art (both roles) | 26 | 22 (11-46) team-games |
| word-association (both roles) | 30 | 33 (12-58) team-games |
| werewolf@villager / werewolf / seer / doctor | 8 | 100 / 50 / 25 / 22 |

Cross-check against the leaderboards (`crosscheck.csv`): Spearman between sample win rate and
leaderboard score, models with >= 10 results: 0.75-0.89 for most board games, 0.99 chess
openings, 0.62 four-in-a-row, 0.62 coin game, 0.55 bargaining, 0.52 word association, 0.74
word art, 0.78 poker (10 models only). Werewolf per role (8 models): seer 0.80, wolf 0.71,
villager 0.52, doctor 0.12. The sample agrees with the boards in ranking, with sampling noise.
The leaderboards are not recomputed here.

## The outcome problem

In a symmetric two-player zero-sum game the mean win rate over models is 0.5 by construction.
A model's win rate depends on who it played. It says nothing about how hard the game is. So win
rate is not comparable across games. The same holds for leaderboard Elo (anchored so the
lowest model is 0; proto3 JSON omits that 0) and for poker BB/100 (mean ~0) and the werewolf
equilibrium rating (mean ~0).

What exists, per game (columns in `outcomes.csv`):

1. **No fixed non-LLM baseline anywhere.** No random agent, engine or scripted bot appears in
   the sampled logs or on any leaderboard. The paper's Stockfish calibration (chess only) is not
   in the data.
2. **Forfeit rate** (all OpenSpiel games): share of games lost by an illegal or unparsable move
   after all retries. Absolute. Pooled: chess 5.4%, openings 6.5%, go 8.7%, dots-and-boxes 6.6%,
   clobber 5.8%, five-in-a-row 4.9%, LOA 4.3%, reversi 3.6%, nine men's morris 2.2%, checkers
   2.1%, four-in-a-row 1.9%, UTTT 0.2%, bargaining 0.06%, coin 0.05%, dark hex 0, word games ~0.
   Very concentrated: median model 0; the high rates are mostly Claude 4.5-4.8 models and
   DeepSeek V3.2 (e.g. Claude Sonnet 4.5: clobber 87%, go 88% of 8 games). In the cases I read,
   most are well-formed but illegal moves twice in a row; some are truncations (finish_reason "length" at 64k
   tokens, Opus 4.7 / Opus 5). A state-tracking and format measure (PLe-like), not strategy.
3. **Retry rate**: share of decisions that needed a second call. Absolute, per decision, so many
   more observations (e.g. chess median 1.8%, max 14%; clobber max 27%). Same caveat.
4. **Absolute game scores** where the rules make them opponent-independent:
   - coin-game: team total / 64 (64 = all 8 own-colour coins). Boards are private and
     separate, so the score does not depend on the opponent. Range 0.36-0.80.
   - word-art: team points / 20 (10 rounds x 2). Rounds are parallel and "independent of the
     other team". Range 0.01-0.61. Art disqualification rate ~0.2% (artist rule violations).
   - word-association: share of own-team words among the team's guesses. Range 0.66-0.98. Trap
     rate 0-31% of games. The board is shared, so this depends a little on the opponent.
   - bargaining: own payoff / 10 (0.15-0.64), deal rate (0.19-0.95), Pareto-optimal deals
     (0.14-0.87), joint welfare / max (0.18-0.91). Both valuations are in the logs. These depend
     on the opponent too, and welfare is not the stated goal (beat the opponent).
   - werewolf: village roles: share of day votes cast on a wolf (0.58-0.80) against a chance
     rate of ~0.33 (`vote_chance`); wolves: survival (0.15-0.37) and share of village votes
     received. Team mates and opponents are other models drawn at random, so these average over
     tables but are not fully independent.
   - poker: none. BB/100 is zero-sum. Illegal actions remapped to check/fold: 46 of 59,742
     decisions.
5. **Anchored strength** for Elo-type boards (17 of 19; not poker, not werewolf): implied
   P(beat GPT-5 mini) = 1 / (1 + 10^(-(Elo_model - Elo_GPT-5-mini)/400)) (`p_beat_anchor`).
   GPT-5 mini is on all 18 non-werewolf boards. Caveats: the 400-point logistic scale is my
   assumption (the paper says Bradley-Terry, Elo-style); and GPT-5 mini's own skill differs
   by game, so "harder for model X" is confounded with "easier for GPT-5 mini". It is the
   expected win rate against one fixed opponent, which is the closest thing to a baseline here.
6. Not done, possible later: engine-anchored move quality (Stockfish for chess, KataGo for go,
   OpenSpiel solvers or MCTS for the small games). This is the only truly absolute strategy
   measure for the board games. It needs new packages and compute.

## Recommendation, one outcome per game x role

| instance | recommended outcome | why |
|---|---|---|
| chess-text, chess-text-openings, checkers, clobber, dark-hex, five-/four-in-a-row, dots-and-boxes, go, lines-of-action, nine-mens-morris, reversi, ultimate-tic-tac-toe | `p_beat_anchor` (leaderboard Elo vs GPT-5 mini); report `forfeit_rate` beside it | only strength measure with a common reference; forfeits are absolute but zero for most models |
| poker-heads-up | leaderboard BB/100 minus GPT-5 mini's (continuous) or drop | no absolute outcome; sample too thin (7 episodes per model) |
| bargaining | own payoff / 10 | absolute 0-1 scale, the episode reward itself; P(beat anchor) as the alternative |
| coin-game | team total / 64 | absolute and opponent-independent: the best outcome in the set |
| word-art@artist, @guesser | team points / 20 (same value for both roles) | absolute and opponent-independent; roles cannot be split (one model plays both) |
| word-association@cluemaster, @guesser | own-word share of guesses (same value for both roles) | near-absolute; roles cannot be split |
| werewolf@seer, @doctor, @villager | day vote on a wolf (minus chance) | the role's own decision quality; win rate mixes in 7 other models |
| werewolf@werewolf | team win rate (or survival) | no clean absolute measure; only 8 models |

## Files written

- `data/instances/instances_gamearena.parquet`, `data/instances/meta_gamearena.csv`
  (gitignored; prompts include third-party game text). Not registered in INSTANCES.tsv.
- `data/downloads/gamearena/`: zip listings, sampled episodes (gzip), leaderboard JSON, paper,
  repos, `derived/seats.parquet` (one row per episode x seat), `derived/status_texts.json`.
- This folder (numbers only, committable under CC BY 4.0 with attribution, see below):
  `outcomes.csv` (one row per game x role x model: counts, win/draw/loss, forfeit, retry,
  fallback, error rates, absolute scores and extras, leaderboard score and CI, p_beat_anchor,
  mean leaderboard score of sampled opponents), `leaderboards.csv`, `sample_counts.csv`,
  `crosscheck.csv`, the two scripts.

## Licences

- Episode logs: CC BY 4.0 (dataset metadata). Derived tables may be shared with attribution
  to Kaggle / Google DeepMind. Logs contain model outputs from many providers; provider terms
  on outputs were not checked.
- Harness code: Apache-2.0 (both repos).
- Leaderboard numbers: no licence stated by the API. `leaderboards.csv` holds only numbers and
  names. Commit only if you accept that (Decision 5).

## Known issues

- **Harness changes over time.** Retry budget fell from 4 to 2 attempts (chess 1.25 -> later).
  Chess forfeit rate by version ranges 0-24% (1.30.1: 24% of seats). Prompts for connect-four
  style games differ from the chess template. Each game spans several harness versions.
- **Model versions.** Display names hide versions and settings (reasoning effort is not in the
  logs). "Claude Fable 5.1" logs as `claude-fable-5-1-default`.
- **Forfeits are partly an interface artefact** (truncation at the token limit, two-attempt
  budget). They hit some model families much more than others.
- **chess-text-openings** is an old, closed run (Dec 2025, 11 February-era models), with the
  old harness. **five-in-a-row** has no episodes after harness 1.30.2 (June 2026).
- **werewolf-dataset** is mostly empty files; use werewolf-gameplay. Werewolf has only 8 models.
- **Team games are self-play teams.** In coin, word art and word association both team seats
  are the same model; artist vs guesser (or cluemaster vs guesser) skill cannot be separated.
- **Bargaining objective** is to out-score the opponent; 43% of games are draws (mostly no deal).
- Game parameters in `configuration` sometimes disagree with the resolved game string (clobber
  config says 8x8, resolved string says 6x5; prompts say 8x8). The prompt is what the model saw.
- Episode logs have no date (except werewolf); harness-version dates are a proxy.
- Poker: 120 sampled episodes only (330 MB); per-model numbers are noise.

## Decisions for Pablo

1. **Outcome for the competitive board games.** (a) `p_beat_anchor` from leaderboard Elo
   (recommended now, with its confound); (b) forfeit or retry rate (absolute, but a PLe/format
   measure, zero for most models); (c) engine-anchored move quality (best, needs Stockfish /
   KataGo / OpenSpiel bots and compute; I can scope it). Choice of anchor: GPT-5 mini, or a
   mid-ranked model.
2. **Scope.** Keep all 24 instances, or only those with an absolute outcome (coin, word art,
   word association, bargaining, werewolf village roles: 9 instances, MSm/MSc-relevant)?
   Drop poker? Drop chess-text-openings (old run) and five-in-a-row (retired)?
3. **What to annotate.** The prompt is one early decision. Real demand comes from a whole game
   (tens of decisions; werewolf and poker contexts grow to 10k+ chars). Options: (a) as now;
   (b) add the rules plus a mid-game observation; (c) annotate a short game summary.
4. **Bigger sample?** Needed only if per-model rates matter (poker; werewolf seer/doctor ~22
   games each). Header-only reads are not possible (JSON is deflate-compressed, outcomes sit
   at the end), so each episode costs a full download. Kaggle Terms should be checked first.
5. **Commit** `outcomes.csv`, `leaderboards.csv`, `sample_counts.csv`, `crosscheck.csv`?
   Episode-derived numbers are CC BY 4.0. Leaderboard numbers have no stated licence.
6. **Register** `instances_gamearena.parquet` in INSTANCES.tsv (not done, per brief).

Run: `python experiments/benchmarks/gamearena-data/fetch_tasks.py` (about 1 min from cache),
then `fetch_outcomes.py` (~1.5 h uncached, ~1.07 GB; minutes from cache).
