# Round 47 — does PLs key on the situation, or on the question? (2026-08-22)

Seal: `sealed_predictions_r47.md`. Raw: `results_r47.csv`. Judges h/s/o, 3 seeds, never Fable.
Three minimal pairs: each **(a)** is the benchmark task as posed, each **(b)** holds the same
underlying system fixed and asks the most demanding *fair* prediction that system supports.

| pair | system | (a) do | (b) predict | jump |
|---|---|---|---|---|
| P1 | matplotlib limit-conditioning → view interval | **1** | **3** | +2 |
| P2 | retail order status / re-pricing / gift-card settlement | **1** | **2** | +1 |
| P3 | pairing process over a line that closes up between passes | **0** | **4** | **+4** |

**Verdict: H-question, on the pre-registered rule (jump ≥2 on 2 of 3).** The situations are
not thin. Ask the same system a terminal question and PLs finds real interacting change in
two of the three — including a 4, the top of the band the whole agentic pilot never reached.

## What this means, stated carefully

PLs is working exactly as designed. The judges are applying the planning exclusion correctly:
when the deliverable is *do the task*, choosing among one's own actions is planning, and the
foreseeing that goes into choosing is not scored here. When the deliverable is *say what will
happen*, the same propagation becomes the answer and scores.

So the zeros in Stage 5 are not evidence that agentic tasks contain no simulable structure.
They are evidence that **PLs measures simulation-as-deliverable, not simulation-as-means** —
which is a real scope, arrived at by the mechanism-vs-demand doctrine, but narrower than the
name "Simulating" suggests to a reader.

P2's +1 is the informative near-miss: even asked terminally, that system's threads (status,
balance, permission) do not feed back into one another, so it lands at 2. That is exactly the
coverage reading holding *for one system*, and it is why the verdict is 2 of 3 rather than 3.

## The decision this raises, and what NOT to do

**The question for the team: should PLs score simulation that a task requires in order to be
done, or only simulation that a task asks for?**

Pablo's constraint on any answer — the rubric must stay natural, with demand rising with the
driver — rules out the tempting fix. Bolting an "instrumental simulation counts too" clause
onto the ladder would (a) score the same task twice, once under Planning for choosing the
action and once here for foreseeing it, and (b) turn level text that currently describes
rising demand into a rule-book about deliverable types. The ladder would stop reading as one
thing getting harder.

Ranked responses, least disturbance first:

1. **Change nothing; document the scope.** Record in the provenance entry that PLs scores
   simulation-as-deliverable, so no one reads Stage 5's zeros as a finding about agents' world
   models. Cost: nothing. Leaves the narrowness in place.
2. **Fix the coverage, not the text.** Add instances whose deliverable is a prediction —
   forecasting, mechanical and physical outcome questions, ecological and economic dynamics.
   r47's own (b) items show such instances reach 3 and 4 immediately. This is what I would
   recommend: it makes the dimension measurable without touching a validated ladder.
3. **Re-key the driver** to include simulation required by the task. Only if the team decides
   the narrower scope is wrong — and then as a full re-validation, not a patch, because the
   planning/simulating carve is load-bearing and was measured (r42 diagonal, B1 probe).

## Honest notes
- These are designed items, and I wrote the (b) forms. A (b) item is only as fair as its
  author; I aimed each at the most demanding question its system genuinely supports, but a
  reviewer should check that I did not inflate them.
- The (a) forms reproduce their Stage 5 values exactly (P1a 1, P2a 1, P3a 0), so the pairs
  are anchored to the earlier measurement.
- No human labels. The standing PLs limitation is unchanged.
