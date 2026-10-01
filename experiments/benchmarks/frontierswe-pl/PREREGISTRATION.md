# frontierswe-pl — pre-registration

Committed and pushed before any label of run `frontierswe-pl`.

**Question.** Do the PL rubrics track difficulty on FrontierSWE v2, a benchmark of long (up to 20 h) open-ended
engineering and research tasks with current-generation outcomes?

## Design

- **Tasks.** The 34 tasks of FrontierSWE v2 (tag `v2.0.0`, `da83f84`; `make_set.py` → `tasks.csv`). Data and sources:
  `../frontierswe-data/NOTES.md`.
- **Prompt** (Pablo, 2026-10-01): what the agent sees. `instruction.md` verbatim; when it cites the task README (25 of
  34), a blank line, the line `Contents of /app/README.md:` (`/app/data/README.md` for snooker-prediction, the path its
  instruction cites) and the README verbatim. Median 3,100 chars, max 9,824 (clean set: 13 of 19 with README, median
  3,190, max 9,824).
- **Outcomes.** frontierswe.com aggregates (site of 2026-09-30): 18 models × 34 tasks, mean and best reward over each
  model's runs (5, except 4 cells), all with the `proximus` harness at maximum effort. Rewards are continuous in [0, 1].
  Per-run rewards are not public (robots.txt disallows `/traces`). A (task, model) cell is solved when the model's mean
  reward is ≥ 0.9 (Pablo; first set at 0.5, changed to 0.9 before any label). Task solve rate = share of the 18 models
  solved. Trials the site's QA panel flagged for cheating are scored 0 and cannot be separated from honest zeros.
- **Clean set.** Drop never-solved tasks: no model's best run reaches 0.9. That drops 15 and keeps 19. At 0.5 only 3
  would go (meg-speech-decoding, msms-denovo-generation, optimizer-design); the stricter threshold also drops 12
  (`dropped_at_0.9_only`): cranelift-codegen-opt, ffmpeg-libswscale-optimization, fitness-recap-video-in-remotion,
  libexpat-optimization, medium-range-weather-forecast, multi-gpu-efficient-finetuning, notebook-compression,
  postgresql-18-on-sqlite, sglang-inference-system-optimization, snooker-prediction, synthetic-music-diarization,
  vision-only-torcs-racing-bot. No external defect review exists, so nothing else is dropped. All 18 models kept.
- **Flags** (not exclusions). `github_issue`: an open issue on the task repo names the task (4 tasks; 2 kept:
  flight-sim-renderer-in-opengl, reconnaissance-blind-chess-recovery). `version_suffix`: the task.toml name has a
  -patched/-hardened/-qemu/-impl suffix the site lacks (6 tasks; 3 kept: frogsgame-post-training, lua-native-compiler,
  stepper-music-sequencer-gba). Clean set without flags: 14 tasks.
- **Outcome on the clean set.** Solve rate at 0.9: median 0.17, range 0–0.39, 3 tasks at 0, 7 distinct values. The
  outcome is coarse; ties are many.
- **Labels.** PLp (text O), PLe, PLs; Opus 5.5 low, v2 prompt; run `frontierswe-pl` via `adele mass` on the 19 clean
  tasks (57 calls; spec `../mass-annotation/specs/frontierswe-pl.toml`).
- **Analysis** (`analysis/analyse.py`). Spearman of each rubric with solve rate at 0.9, predicted negative, on the clean
  set (primary). Sensitivity, same direction: solve rate at 0.75 and at 0.5, run-weighted mean reward, and the share of
  models whose best run reaches 0.9; and all outcomes on the clean set without flagged tasks. Power is low: p < 0.05
  needs |rho| ≥ 0.46 at n = 19 and ≥ 0.53 at n = 14.

## Predictions (sealed)

Priors: PLp tracks solve rate on SWE-bench and tau2 but not on Terminal-Bench 4.0 or TB-Science, where long tasks sit
at PLp 3 and failures turn on knowledge and verifiers. FrontierSWE's tasks are long, open-ended projects, closer to the
latter. With n = 19 and a coarse outcome, power is low.

- PLp against solve rate at 0.9 negative with p < 0.05: 0.2.
- PLp against solve rate at 0.9 negative in sign (ρ < 0): 0.55.
- At least 15 of the 19 tasks at PLp 3 or higher: 0.75.
- At least one task at PLp 4 or higher: 0.6.
- Neither PLe nor PLs significant (p < 0.05) against solve rate at 0.9: 0.8.
