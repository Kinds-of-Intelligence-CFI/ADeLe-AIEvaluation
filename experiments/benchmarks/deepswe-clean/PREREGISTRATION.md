# deepswe-clean — pre-registration

Committed and pushed before any label of run `deepswe-clean`.

**Question.** Do the PL rubrics track difficulty on DeepSWE v1.1, a long-horizon coding benchmark with current-generation
per-trial outcomes and an external defect review?

## Design

- **Tasks.** DeepSWE v1.1 (datacurve-ai/deep-swe at `3cda4081`; no v1.1 tag), 113 tasks. Clean set (Pablo,
  2026-10-01): drop the 23 tasks Epoch AI's review (2026-09-07, CC BY 4.0) names as defective, all false negatives.
  Never-solved tasks would also go; there are none (every task has at least 7 passes). Low solve rates stay:
  gql-incremental-graphql-delivery (3.6%) and bandit-structured-nosec-directives (6.8%). **90 tasks**
  (`make_set.py` → `tasks.csv`, `keep`).
- **Flag, not exclusion.** `community_issue`: an open issue or PR on datacurve-ai/deep-swe claims an ambiguous
  instruction or a verifier that rejects correct work on Datacurve's own runs, unfixed in v1.1
  (`../deepswe-data/community_issues.csv`, read 2026-10-01; mapping rule in `make_set.py`). Conservative: claims fixed
  by v1.1, host-dependent failures, verifier hangs and metadata typos are not flagged. 7 tasks; 4 in the clean set
  (bandit, csstree, gql, quill). Third-party claims, mostly unconfirmed by Datacurve.
- **Prompt.** `instruction.md` verbatim, including the closing line asking the agent to work on a new branch and commit
  (the text the agent sees; checked in `make_set.py`).
- **Outcome.** Binary per trial (`passed`). Task solve rate = share of scored trials resolved across all 70
  configurations (28 models × reasoning effort, mini-swe-agent, up to 4 trials). Trials Datacurve excludes from its
  score (provider, verifier, network errors) are missing, not failures. GPT-6 Astra's 5 configurations are OpenAI-run
  (`metrics_source = verified_openai_handoff`); kept, flagged per configuration in the leaderboard. Sensitivity:
  `solve_rate_pre_timeout` drops the 8 configurations first run on or after 2026-08-26, when the repo raised the agent
  timeout from 5,400 s to 10,800 s (glm-5-3-flash, gemini-3-8-flash × 2, gpt-6-astra × 5); `solve_rate_no_astra` drops
  GPT-6 Astra. No human difficulty or time estimate exists.
- **Known bias.** Epoch's review is partial. Its main error (agent tests collide with hidden tests) can hit any task,
  so clean-set solve rates are probably biased down, more for models that write tests. Accepted.
- **Data terms.** Datacurve states no terms for the trial data (#94). Only per-task solve rates (`tasks.csv`) and the
  aggregate per-configuration leaderboard are tracked; trial data stays in gitignored `data/raw/deepswe-v1.1/`.
- **Labels.** PLp (text O), PLe, PLs; Opus 5.5 low, v2 prompt; run `deepswe-clean` via `adele mass`
  (`../mass-annotation/specs/deepswe-clean.toml`, clean tasks only: 270 calls).
- **Analysis** (`analysis/analyse.py`): Spearman (swebench-pl's `rho`) of each rubric with solve rate, predicted
  negative. Primary: PLp on the 90 clean tasks. Secondary: PLe and PLs on the 90; each rubric with the two sensitivity
  rates; on the clean set without `community_issue` (86). All 113 only if the excluded tasks get labels (not planned).
  Only valid answers written by claude-opus-5-5 count.

## Predictions (sealed)

Priors: DeepSWE tasks are repository coding tasks like SWE-bench Verified, where PLp tracks solve rate (ρ = −0.58 on
the clean set), but longer and written for the benchmark, and the outcome is noisier (residual false negatives). At
n = 90, p < 0.05 needs |ρ| ≥ 0.21.

- PLp against solve rate negative with p < 0.05 on the 90: 0.65.
- PLp ρ between −0.60 and −0.20: 0.55.
- Most tasks at PLp 2 or 3, with 3 at least as common as on SWE-bench Verified (where 8 of 443 were at 3): 0.7.
- PLe against solve rate negative with p < 0.05: 0.35.
- PLs against solve rate negative with p < 0.05: 0.25.
- PLp's ρ with each sensitivity rate within 0.05 of the primary: 0.9.
