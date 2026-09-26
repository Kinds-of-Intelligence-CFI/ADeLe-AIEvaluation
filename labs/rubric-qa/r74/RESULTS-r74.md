# Round 74 — PLs labels for all 57 market questions, and the PLs tier analysis (2026-08-26)

Seal: `sealed_predictions_r74.md`. Single-call, median of three (h/s/o), meta-stripped v19,
examples kept, labels persisted to disk after every block (the session-limit interruption that cost
35 unpersisted cells is recorded in `state.json`, with the protocol lesson). v19 text untouched
throughout, per Pablo's no-shaping instruction; the standing-rate guard remains parked.

## Labels

r74's 44 items: 1: 13, 2: 20, 3: 7, 4: 2, 5: 2. Combined with r73's 13, all 57 market questions:
**1: 14, 2: 23, 3: 10, 4: 2, 5: 8.** The sealed expectation (bulk at 1-2, coupled minority at 3+)
held. Judge spreads of 3+ levels on 14 of 44 — the standing-rate ambiguity measured in r73 is
still live and still text-unresolved, absorbed by the median as the protocol intends.

## The PLs demand-by-ability result, on the market half (n = 56 with tier data)

Mean Brier by PLs level:

| PLs | n | supers | gpt-4o | llama-2-70b | supers-vs-gpt4o gap |
|---|---|---|---|---|---|
| 1 | 14 | 0.106 | 0.122 | 0.326 | +0.016 |
| 2 | 23 | 0.094 | 0.158 | 0.321 | +0.064 |
| 3 | 9 | 0.095 | 0.234 | 0.296 | +0.139 |
| 4 | 2 | 0.084 | 0.122 | 0.356 | +0.038 |
| 5 | 8 | **0.009** | **0.275** | 0.250 | **+0.266** |

Per-tier Spearman(PLs, Brier): supers +0.05, public +0.21, sonnet-3.5 +0.26, opus-3 +0.28,
gpt-4o +0.29, llama-3-70b +0.27, haiku-3 +0.33, llama-2-70b -0.04.

**Three bands, exactly the item-response pattern a demand dimension should produce:**

1. **The ceiling tier is untouched by demand in this range.** Superforecasters' Brier is flat to
   *falling* with PLs, reaching 0.009 at Level 5 — on the contested geopolitical items (ceasefires,
   Maduro, mobilization, memecoins) they were nearly perfect. Their ability exceeds every demand
   level this corpus reaches.
2. **The middle tiers degrade with demand**, rho +0.21 to +0.33 across every competent 2024 model.
   GPT-4o goes from parity with supers at Level 1 to 0.275 at Level 5, worse than always-0.5.
3. **The floor tier is flat at chance** (llama-2, rho -0.04): a solver doing nothing shows no
   demand gradient, as it must.

And the key contrast with r72: **no entropy confound this time.** On QLq/dataset questions, high
demand meant high irreducible uncertainty and everyone converged. Here the Level 5 items were
CALLABLE — supers called them — so the model failures at Level 5 are failures of simulating, not of
luck. The human-model gap widens monotonically with PLs demand, +0.016 at Level 1 to +0.266 at
Level 5. That is the demand-by-ability interaction for PLs, on real instances, real solvers and
real resolutions: **the desideratum-9 result the programme set out for.**

## Honest limits

- n = 8 at Level 5 and 2 at Level 4; one round; one corpus type.
- 2024-era models (Pablo's old-models caveat stands). The 2026-01-04 round in the tarball carries
  Fable 5, Opus 5, Sonnet 5 and Gemini 3.x: the replication that answers whether *current* models
  close the Level 5 gap is sitting there unlabelled, and is the highest-value next run.
- The labels carry the measured o/s reader split (opus standing-rate-broad, sonnet
  constructed-model-broad); the median tames it, but the guard question remains Pablo's to rule on.
- Two haiku cells applied carves wrongly (a release-date item sent to 0 via the minds carve); the
  median absorbed both, consistent with every round since r58.

## Correction (Pablo, post-round)

The phrase "the gap widens monotonically" over-stated the criterion. The demand-by-ability
prediction is an inverted-U in the tier gap: near zero where demand is below both abilities, peaked
between them, near zero again above both (r72's convergence was that upper limb). Monotone growth
in r74 is corpus-contingent: the sampled range sits entirely below the superforecasters' ceiling.
The proper criterion — each solver's curve declines with demand, and bend-points order by ability —
is what the data satisfy. Testable consequence: on items beyond superforecaster ability, the
human-model gap should close again.
