# ms-candidate — results (2026-10-25)

**Question.** Do the candidates (MSc v4, written from Pablo's framework; MSm back toward v1) keep the lab's results and
match Pablo's agent-side labels on real tau2 tasks at least as well as the current texts?

**Answer.** Almost. Both candidates keep every lab check, with and without reasoning. On the 15 tau2 tasks MSc v4
matches Pablo far better than the current text (13 vs 6 exact), but it fails the pre-registered H2 rule on one item
(H-08, 1 against his 3). Bare-digit labels sit lower at the 1/2 border (11 of 15 exact). The recurring cause is v4's new
Level 1 example (a refused library patron), which the judges cite whenever a rule answers each objection.

## By rule

| rule | MSc v4 | MSm candidate |
|---|---|---|
| R (lab regression), reasoning | holds (r36 D2 loss not confirmed in pass 2) | holds |
| R, bare digit (N1) | holds (battery M04 loss not confirmed in pass 2) | holds |
| N3 (bare digit vs reasoning) | 98% exact, 100% within 1 | 90% exact, 100% within 1 |
| M (refusal pairs) | holds: all five at 1, with and without reasoning | — |
| Pairs that need something (5–7) | supplier and builder at 4; **curfew at 1** (Pablo: belongs at 4) | — |
| H1 (exact vs Pablo, full task, reasoning) | **holds: 13 of 15** (current text 6 of 15) | not run (no MSm labels) |
| H2 (no item 2+ off where current is within 1) | **fails: H-08** (Pablo 3, v4 1, current 3) | — |
| H3 (full task ≥ script, current text) | holds (6 = 6); under v4, 13 vs 12 | — |

Pablo's 15 labels (MSc, agent's side, 2026-10-25, in chat): nine at 1, five at 2, one at 3. None was marked "not enough
information".

## Where v4 and Pablo differ

| item | Pablo | v4 reasoning (full / script) | v4 bare digit (full / script) | judge's reason |
|---|---|---|---|---|
| H-08 (retail: returns refunded to the original methods, after a refused swap) | 3 | 1 / 2 | 1 / 2 | "the same as the Level 1 example of turning down a library patron… her anger is emotional colour, not real resistance" |
| H-12 (banking: the customer must choose the one card that fits) | 2 | 1 / 1 | 1 / 1 | the customer states every requirement upfront and decides alone |
| H-01, H-14 (cooperative exchanges and changes) | 2 | 2 / 2 | **1** / 2, 1 | bare digit only: drops to 1 |

Every refusal Pablo put at 1 (nine items) is at 1 under v4, with both inputs and both prompts. Under the current text
the same items scored 2 to 4.

## Reading

- **v4's driver works.** Refusals, the main problem of the current text, are now placed as Pablo places them, on real
  tasks as well as on the written pairs.
- **The Level 1 library example over-reaches.** The judges cite it for the curfew pair, the supplier pair under v5, and
  H-08: wherever a rule answers each objection, they place the task at 1, even when the task needs the other party's
  agreement. It probably also pulls bare-digit labels from 2 to 1.
- **Input.** With v4, the full task and the script give nearly the same labels (13 vs 12 exact). The input question
  does not decide MSc.

## Deviations and caveats

- Fifteen items, ten of them not blind to the judge's current-text labels. Pablo labelled from the agent-side
  worksheets, with Claude's neutral summary of the goal and the customer's behaviour for each.
- The minimal pairs were reused across screens; they are not fresh.
- Battery M04 and r36 D2 are noisy (each moved between pass 1 and pass 2).

## Update 2026-10-25: v4b replaces v4 (amendment 7)

v4b is v4 without the Level 1 library example. Under both prompts it keeps every lab check (r36 D2 noisy again: 3,
then 4, 4, 4), holds the refusal rule (4 of 5; the gym pair B at 4), places all three "needed" pairs at 4 (the curfew
included), and passes H1 and H2.

| | v4 reasoning | v4 bare digit | **v4b reasoning** | **v4b bare digit** |
|---|---|---|---|---|
| exact vs Pablo's labels (full task) | 13 | 11 | **13** | **13** |
| exact vs his revised labels (H-08 2, H-12 1) | 14 | 12 | **15** | **15** |
| H2 | fails (H-08) | fails (H-08) | holds | holds |
| curfew pair B | 1 | 1 | **4** | **4** |
| refusal pairs at 3 or less | 5 | 5 | 4 | 4 |

Reading: removing the example fixes the over-reach without bringing back the old refusal problem, and it makes the
bare-digit judge (the production setting) agree with the reasoning judge on the tau2 tasks. One cost: the gym
refusal pair (a member disputing a paid pause) goes back to 4. On the script input, v4b matches less often (9 of 15)
than on the full task, so the full task is the better input for MSc.
