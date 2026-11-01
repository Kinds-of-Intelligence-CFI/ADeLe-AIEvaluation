# cooperbench-plms — pre-registration

Committed and pushed before any label of run `cooperbench-plms`.

**Question.** On CooperBench, where the same pair of coding features is built by one agent (solo) or by two agents
who must coordinate (coop), do the social rubrics of the coop task predict how much success drops from solo to coop?

## Design

- **Tasks.** CooperBench: 652 feature pairs from 30 task pools in 12 repositories. Data, sources and what the agents
  see: `../cooperbench-data/NOTES.md`. The unit is a (pair, condition) task, solo or coop. coop_wo_comm is left out:
  its plans were negotiated with messaging, so it is not a clean no-communication condition.
- **Prompt.** What the agents see (`instances_cooperbench.parquet`): solo, one agent building both features; coop,
  two labelled sections ("Agent 1 sees", "Agent 2 sees"), each agent seeing only its own feature. Each prompt opens
  with one paragraph stating the setup and the success rule (both test suites pass after merging), which the agents
  are not shown as such. The model-written plan is a placeholder, repeated feature text appears once, and the generic
  OpenHands system prompt is summarised in a line. Median 7.9k chars (solo) and 16.8k (coop), max 36k.
- **Outcomes** (`make_set.py`). From the HF trajectories (MIT; GPT-5.5 from team-trajectories, Apache-2.0), where solo
  and coop come from the same evaluation. Three models: GPT-5 and Claude Sonnet 4.5 (OpenHands 0.54, paper runs, solo
  and coop) and GPT-5.5 (codex agent, May 2026, solo and coop with git). One run per cell. Left out: Qwen3-30B (floor:
  6% solo, 5% coop), MiniMax M2 and Qwen3-Coder (solo results do not match the leaderboard), Gemini (no per-pair solo
  results). Per pair: `solo_rate` and `coop_rate`, the share of the three models that succeed, and
  **`drop` = solo_rate − coop_rate** (in thirds).
- **Sample.** Frame: the 452 pairs (22 pools) with all six results. 120 pairs, seed 0, stratified by pool (up to two
  per pool, then proportional fill; 1–14 per pool), so 240 prompts. Sampled: 74% gold-patch conflicts, 27% flagged,
  mean solo 0.49, coop 0.33.
- **Flag** (`any_flag`): a feature's spec or tests changed after the runs (benchmark audit, Aug–Sep 2026).
- **Labels.** PLp (text O), PLe, PLs, MSm, MSc; Opus 5.5 low, v2 prompt; run `cooperbench-plms` via `adele mass`
  (1,200 calls).
- **Analysis** (`analysis/analyse.py`, tested on synthetic labels). Spearman (swebench-pl's `rho`). Primary: MSc of the
  coop prompt against `drop`, and MSm of the coop prompt against `drop`, both predicted positive. The solo version of
  the same pair holds the coding work fixed, so `drop` isolates the cost of cooperating. Secondary: each rubric's coop
  − solo difference against `drop` (positive); each rubric's solo level against `solo_rate` and coop level against
  `coop_rate` (negative). Sensitivity: primary without flagged pairs; primary with the official site coop results for
  GPT-5 and Claude (unlicensed site repository, local file). At n = 120, p < 0.05 needs |ρ| ≥ 0.18; the drop has six
  values and 57 pairs at 0, so power is modest.

## Predictions (sealed)

Priors: on tau2 MSm and MSc sat at 2 and did not track difficulty. Here the coop task adds a partner whose actions are
hidden and must be coordinated, while the solo task has none. Each cell is one run, so the drop is noisy.

- MSc is 0 on at least 90% of solo prompts: 0.85.
- MSc is higher on the coop prompt than on the solo prompt for at least 90% of pairs: 0.8.
- Median MSc on coop prompts at least 2: 0.7.
- MSc (coop) against drop positive with p < 0.05: 0.25.
- MSm (coop) against drop positive with p < 0.05: 0.2.
- PLp (solo) against solo rate negative with p < 0.05: 0.45.

**Cost.** 1,200 Opus-low calls, about 6 weekly points.
