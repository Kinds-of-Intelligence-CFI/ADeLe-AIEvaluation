# r47 sealed predictions — does PLs key on the situation or on the question? (2026-08-22)

Two hypotheses explain PLs scoring 0–1 across all 20 natural agentic instances:

- **H-coverage**: these situations genuinely contain little interacting change. The rubric is
  fine; the battery does not exercise it.
- **H-question**: the situations do contain interacting change, but PLs only scores it when
  the *answer asked for* is itself a prediction. Simulation that is instrumental to doing a
  task is routed away by the planning exclusion, so PLs measures a narrower class than anyone
  chose — "tasks whose deliverable is a forecast."

Three minimal pairs. Each **(a)** is the benchmark task as posed; each **(b)** holds the same
underlying system fixed and asks the most demanding *fair* prediction that system supports.
Judges h/s/o, 3 seeds, never Fable.

| pair | system held fixed | (a) do | (b) predict |
|---|---|---|---|
| P1 | matplotlib scale-conditioning → view interval → draw, with autoscale re-entry | fix the log-limit bug | does the axis invert for two given limit calls |
| P2 | retail order: pending status, item cancellation, re-pricing, gift-card settlement | serve the customer | order status and card balance after a modification, and whether a later cancellation is still permitted |
| P3 | pairing process over a line that closes up between passes, so neighbours change | compute the maximum matching | how many cows remain unpaired at the fixed point |

## Predictions

Under **H-coverage**: the (b) items stay at 1–2, because a fair terminal question about these
systems still runs one course with nothing feeding back.
Under **H-question**: the (b) items reach 3+ on systems whose (a) form scored 0–1.

Sealed prediction: **P1b 3, P2b 3, P3b 3; P1a 1, P2a 1, P3a 0** — i.e. I expect H-question to
be at least partly right, with a 2-level jump on P2 and P3. If I am wrong and the (b) items
stay ≤2, H-coverage is confirmed and Stage 5's reading stands as written.

## Decision rule, and the constraint on any response

- **Jump ≥2 on 2 of 3 pairs** → H-question. PLs's scope is narrower than intended, and that
  is a construct decision for the team: is PLs meant to score simulation *demanded by the
  answer*, or simulation *required to do the task*?
- **All (b) ≤ 2** → H-coverage. Stage 5's recommendation stands unchanged.
- **Mixed** → report per-pair; no conclusion.

**Constraint carried into any response (Pablo, 2026-08-22): the rubric must stay natural, with
demand rising with the driver.** If H-question holds, the response is NOT to bolt an
instrumental-simulation clause onto the ladder — that would score the same task twice, once
under Planning for choosing the action and once here for foreseeing it, and would make the
level text read as a rule-book rather than a description of rising demand. The candidate
responses, in order of how little they disturb the ladder:
1. Change nothing; document that PLs scores terminal prediction, and record the scope in the
   provenance entry so no one reads the zeros as evidence about agents' world models.
2. Add instances whose deliverable is a prediction to the battery — a change to coverage, not
   to text.
3. Only if the team decides instrumental simulation must be scored: re-key the driver, with a
   full re-validation, not a patch.
