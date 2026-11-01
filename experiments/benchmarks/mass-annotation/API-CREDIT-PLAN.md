# Plan for the API and cloud credits (drafted 2026-11-01)

> **Update 2, 2026-11-01: the Console $400 is two grants.**
> - **$200, expires 2026-11-04.** Granted 2026-10-28.
> - **$200, expires 2026-12-04.** Granted 2026-11-01.
>
> Both cover the API, the Batch API, the Agent SDK, Playground and Managed Agents. The expiry time of day and
> timezone are not shown, so assume Nov 4 00:00 UTC. Assume, unverified, that the grant expiring first is spent
> first; any overrun then falls on the December grant, so nothing is lost by going over.
>
> **Order for the November grant** (≥ $200 used before Nov 4):
> 1. Gates: $13, Nov 1–2.
> 2. `bulk-w2-static`: ~$99, sent by Nov 2.
> 3. Memory validity package: ~$38, sent by Nov 3 morning. If its script isn't ready, it moves to December.
> 4. Fillers to reach $200, whichever are ready: the rest of `w1v1-code` on the API (≤ $22, a recorded
>    deviation), `bulk-w1-memory` ($34, needs the team), or more noise-floor repeats.
>
> Every batch goes out by Nov 2 at 18:00 UTC where possible, so it finishes within 24 h, before the expiry.
> The cloud's $250 still runs out on Nov 5 at 07:59 UTC, as in the first update. `w1v1-other` goes to the cloud.

> **Update, 2026-11-01 (later): there are two pools, not one.**
> - **$400 Console organisation credit.** This pays for the Batch API. Its owner and expiry are not checked yet.
> - **$250 Claude Code cloud credit.** It runs out on **2026-11-05 at 07:59 UTC** (08:59 GMT+1). It pays only for cloud sessions, not the Batch API.
>
> The tables below were written for a single $250 API pool. The revised split:
> - **Console:** tiers 0–2 ($150) as below. Tier 3 is no longer needed. What is left (~$250) goes later to `bulk-w1-memory`, TB 2.1, Toolathlon, the LongMemEval profile, and a fallback for wave 1.
> - **Cloud:** the rest of wave 1 (`w1v1-code` + `w1v1-other`, 9,356 cells) on subagents in cloud sessions. This is the pre-registered route, so there is no deviation. Start with a 50-cell pilot to measure how the credit is charged and to check the transcripts (model, effort, no CLAUDE.md attached).
> - **What the cloud route needs:**
>   - a cloud environment for `Kinds-of-Intelligence-CFI/ADeLe-AIEvaluation` (none exists yet, and the org may have to approve the GitHub app);
>   - `ADELE_HF` as an environment secret, with network access to huggingface.co;
>   - the judge agent files committed to `.claude/agents` in the public repo;
>   - the goal inputs rebuilt on the VM (`mass check` verifies them against the pinned hashes);
>   - `ADELE_JUDGE_IO` and `ADELE_AGENTS_DIR` set for the VM's paths.
> - **If the cloud route isn't running by Nov 3**, wave 1 goes to the subscription after the reset, or to the Console as the fallback.

## Principles

1. **API money expires and the subscription renews every week.** So the API takes well-defined work that would otherwise eat many weekly points. Exploration, and anything still waiting on a decision, goes on the subscription.
2. **Short prompts are best value on the API.** The harness overhead dominates short prompts on subagents:
   - `bulk-w2-static`: about 0.85 weekly points per API dollar;
   - `w1v1-other`: about 0.47.
   Self-runs of subject models must be plain API calls anyway, because the harness would confound them.
3. **Quality before volume:**
   - a dry run, then the gates;
   - pre-register before any label;
   - recalibrate the cost after the gate;
   - spend the flexible work last, sized to the real balance.
4. **The biggest unknown is output tokens.** Opus 5.5 always thinks (adaptive thinking cannot be turned off). The estimates assume 200 output tokens per call. At 500, `bulk-w2-static` costs about $80 more. The gate measures this before anything big is sent.

## Order of work

| tier | when (UTC) | work | est. | cumulative | needs |
|---|---|---|---|---|---|
| 0 | Nov 1–2 | dry run: 10 cells of `gate-api-bridge` | <$0.1 | | API key in `.env` |
| 0 | Nov 1–2 | `gate-api-bridge`: 450 calls, API vs subagent on identical prompts | $4 | $4 | pin + prereg note |
| 0 | Nov 2 | `gate-v1-bridge`: 60 battery items × 18 v1 rubrics vs GPT-4o (`subsets/v1_bridge.csv` exists) | $6 | $10 | pin |
| 0 | Nov 2 | memory gate, lab-lite (~360 calls) | $3 | $13 | prereg; tell Marko |
| — | Nov 2 | **Checkpoint:** real cost per call → re-estimate every tier | | | |
| 1 | Nov 2–3 | `bulk-w2-static`: ARC-AGI-2, GPQA, ArXivMath, BrokenArXiv; v1 + MSm; 16,434 calls; plus a 3% re-judge (noise floor) | ~$99 | $112 | prereg |
| 2 | Nov 3 | memory validity package: LongMemEval-S and GraphWalks ablations, profiles on 22 non-memory rubrics (`reports/Frontier memory benchmarks.md`) | ~$38 | $150 | self-run script, prereg |
| 3 | Nov 4, before 12:00 | **filler, sized to the Console balance**: the rest of `w1v1-other` on the API (≤ $72), as a new run | ≤$72 | ≤$222 | gate passes + Pablo approves the deviation |

- **The remaining ~$28 is contingency.** The tier 0–2 estimates could be ±30%. Tier 3 absorbs the error: its size is set on Nov 4 from the real balance.
- **Spend guard:** send a batch only if its estimate is ≤ 85% of the remaining balance. Run in tier order, so any cut falls on the lowest tier.
- **If tier 1 re-estimates above $120:** split it. Send ARC-AGI-2, GPQA and ArXivMath first; BrokenArXiv waits.
- **If `gate-api-bridge` fails:** stop all API judging and ask. Wave 1 stays on subagents. Wave 2 on the API would then be a different judge setting.
- **Batches can take up to 24 h.** So the last batch goes out on Nov 4 morning, and Nov 5 is only for retries and collection.

## Subscription in parallel

- **Now** (weekly 81%, stop at 95%): `w1v1-code`, 2,610 cells, about 13 points.
- **After the Nov 3 20:00 reset:**
  - `w1v1-other`, if tier 3 does not take it;
  - the anchor set and noise floor for the subagent runs;
  - the scripts and pre-registrations above.
- **Housekeeping first:** commit the 884 tau2 and 100 code labels that are still uncommitted.

## Postponed, and why

| work | why it waits | later route |
|---|---|---|
| `bulk-w1-memory` ($34) | the team, the memory gate, and the construct ruling | API next time, or subscription |
| choosing a memory benchmark and labelling it | after the validity package and Marko's ruling | subscription + self-runs |
| TB 2.1, Toolathlon-Verified (~$40) | no loaders; needs a Harbor Hub login and Pablo accepting Toolathlon's terms | subscription (~8–10 points each) |
| LongMemEval-S demand profile (~$50) | too costly for 10 items | only if the ablations look promising |
| HAL wave 3 | not planned yet | — |
| wave-2 outcome ingestion (EEE GPQA, ARC dump, MathArena) | code only, no API cost | subscription, any time |

## Decisions for Pablo

1. Confirm these are Anthropic Console credits, put the key in `.env`, and say which timezone the deadline uses.
2. Go for tiers 0–2 (~$150).
3. Tier 3: if the gate passes, may the rest of `w1v1-other` move to the API? This is a recorded deviation from the wave1-v1 pre-registration.
4. Memory: run Marko's gate and the validity package now and send him the results, or ask him first?

**Minor calls I made (veto any):**
- the tier order;
- the 85% spend guard;
- re-judges only on API runs (subagent runs use the subscription);
- splitting BrokenArXiv off if tier 1 overruns;
- the postponements above.
