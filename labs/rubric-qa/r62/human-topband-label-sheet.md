# Human top-band label sheet, v2 — PLp, PLe, PLs (2026-08-25)

## Provenance, since Pablo asked

**Every item below is designed by me. None is a benchmark instance.** The first version of this
sheet was also underspecified: S1 said "given the stairwell layout, door-closer settings and where
people are" and S3 said "given the reset schedule and stated elasticities", which is the same
placeholder pattern Pablo caught in the rubric examples and which was stripped out of the rubric
earlier in this same session. Reproducing it in the validation sheet was careless.

This version puts the deciding quantities in. Where a designed item is the only option, it is
marked so, and the note at the end says what a real-instance replacement would take.

| dimension | could these be real instances? |
|---|---|
| PLs top band | **Yes.** ForecastBench publishes question sets nightly at `github.com/forecastingresearch/forecastbench-datasets`, drawn from Kalshi, Manifold, Metaculus and Polymarket, with automatic resolution. Pulling that set would give real items at 2 through 5 *and* the resolved outcomes desideratum 9 needs. Not done yet. |
| PLp top band | No source known. The agentic pilot tops out well below 4 on planning. Designed items are the only option today. |
| PLe top band | No source known, same reason. |

**How to use.** A number 0 to 5 against each id. No candidate levels are offered and my predictions
are withheld, because r53's honest limit was that I framed the options and may have anchored the
answers. Full ladders are given so the framing does not push high either.

---

## PLp — Planning. How hard a workable plan is to find.

`0` plan is given · `1` plan retrieved, one standard routine covers it · `2` plan assembled from a
few independent standard steps · `3` plan searched for, subtasks listable but decisions interact ·
`4` structure of the plan must be constructed, no procedure supplies the decomposition · `5` plan
invented, no established procedure exists and workable plans are so rare that finding one is a
discovery

- **P1** A bank's core ledger runs on a mainframe with 1,400 batch jobs and 300 downstream systems, and must move to a new platform with no service interruption. No vendor has done this combination. Once the first 40 jobs are cut over, rolling back means replaying two days of transactions. The deliverable is the migration plan.
- **P2** A drug candidate is suspected of causing liver injury in roughly 1 patient in 20,000. The registration trial of 3,000 patients would expect to see none. Design the study that would settle whether the effect is real. The deliverable is the protocol.
- **P3** Plan a three-week field season for six people. Permits take five weeks to issue, the equipment ships in twelve days, the weather window is the last two weeks of July, and the boat is available only in the first of those two.
- **P4** Given the recipe and the shopping list, cook the meal.

## PLe — Action control and execution. How the agent can tell, while working, that it is going right.

`0` single atomic action · `1` environment checks at every step · `2` environment checks at
checkpoints, forced by the structure of the work · `3` checks easy but elected, the agent decides
when to check · `4` no ready-made check, verification must be constructed · `5` no check available
and none constructible, open-loop

- **E1** Hand-copy 300 archival records, each with 14 fields, into a new register. The source is sealed and returned the same day, before any comparison is possible.
- **E2** Run a 26-week animal study to a fixed protocol. Any interim sampling destroys the cohort, so the only readout is at week 26.
- **E3** Rewrite a 4,000-line payroll module that has no tests. A tax-banding error would affect 3 per cent of employees and surface only at the annual reconciliation, eleven months later.
- **E4** Follow a recipe in which each step's outcome is plain before moving on to the next.

## PLs — Simulating. How complex and how accurate a model of the situation must be.

`0` no model, nothing changes · `1` model of a single step · `2` a known rule supplies the model and
yields the answer without stepping through · `3` the model's parts act on one another, but it may
stay coarse · `4` coupled and accurate, a loose run flips the answer · `5` a model no one can be
sure of, indirect effects rival the direct ones

- **S1** A fire starts on the third floor of a six-storey building. Forty people are on floors four and five, the two stairwells sit at opposite corners, three fire doors are propped open, and smoke fills a stairwell in about ninety seconds. Does anyone on floor five fail to reach an exit within four minutes?
- **S2** Two trawler fleets fish one stock of 80,000 tonnes. Each raises its catch 10 per cent when the other does, and the stock's recovery rate falls from 6 per cent a year to 2 per cent once it drops below 30,000 tonnes. Does the stock fall below 10,000 tonnes within twelve years?
- **S3** A central bank raises rates by 2 points. Seventy per cent of mortgages are fixed for five years, a fifth of those reset each year, and a 1-point rise has historically lifted arrears 0.4 points among those resetting. Do arrears exceed 3 per cent within two years?
- **S4** A general strike is called for next month. Four unions have voted to join and six are undecided, and each undecided union's executive has said it will come out only if at least half the others do. Is the strike still running after two weeks?

## The chess pair — both on PLs

The phrasing difference is the whole point, so these two stay as they are. Pablo's answers being the
same or different settles the precedence question r62 left open, between the rules-supply-the-model
clause and the instrumental-scope clause.

- **C1** Find a strong plan in a club-level chess middlegame position, given as a diagram.
- **C2** In a club-level chess middlegame position given as a diagram, which of two candidate moves leaves the better position four moves later?

---

## What the answers are worth

If nothing lands above 3, the top bands are unreachable in practice and all three rubrics need
their top levels re-pitched rather than re-worded. If they spread across 3, 4 and 5, this is the
first human anchor above 3 the project has had, and rounds 57 to 62 acquire a foundation they
currently lack. Either way these are **designed** anchors, which sit below real instances in the
evidence hierarchy, and the ForecastBench pull would put the PLs half of this sheet on firmer ground.
