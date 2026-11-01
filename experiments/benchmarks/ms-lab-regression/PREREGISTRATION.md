# Lab regression for MSm and MSc — pre-registration

To be committed and pushed before any label of this study, with the items, prompts and analysis script.
The run needs Pablo's go and his OK on its cost.

**Question.** Do today's judge and prompt reproduce the lab's results for the two social rubrics, MSm (Mind
modelling and social cognition) and MSc (Communication and social interaction)?

**No rubric text changes.** Both rubrics are judged exactly as the catalog loads them: `MSm.txt` (sha256
`b8c3ec15…`) and `MSc.txt` (sha256 `9c38881d…`). This study tests the judge and the prompt, not a text.

**Why.** The lab measured MS with three judges (haiku, sonnet, opus), the v1 prompt and one call per item.
Real tasks are now labelled with the v2 prompt (`build_annotation_prompt_v2`) and Opus at low effort. The PL
rubrics went through this check (`../plp-candidate/lab-regression/`). MSm and MSc have not.

**Pass rule, in one line.** The regression passes if every ruled check below holds, or if no failure of one
is confirmed in pass 2: example placement, no foreign leaks, the lab's own items at their recorded levels or
contrasts, and the battery's checks.

## Design

- **Judge.** `adele-judge-v2-low` (tools Read and Write, effort low, no CLAUDE.md), model opus, relayed by
  `judge-dispatcher-v2-low`. Three repeats per item, in judge folders `opus-low-r1` to `opus-low-r3`. One item
  per call. The label is the median of the three (with two labels, the lower). Never Fable.
- **Prompt.** The v2 prompt, with the rubric as the catalog loads it (no `#!` line, examples kept). Set P is
  the one exception: its items are the examples, so every Examples block is stripped, as in r25 and in the PL
  regression.
- **Blinding.** Prompt files have opaque, shuffled ids. Nothing in a file name tells the set, the level or the
  source. The file name carries the rubric (`<id>@MSm`), which the prompt shows anyway.
- **Writers.** A safety classifier can make another model write an answer. `writers.py` finds the writer of
  each answer. Only answers written by `claude-opus-5-5` count. Others are moved to `responses_fallback/`
  and the cell is judged once more (`writers.py --set-aside` writes the retry relay). If that fails too, the
  cell has no label.
- **Relays.** `make_prompts.py` writes the relay messages to `$ADELE_JUDGE_IO/ms-labreg1/relays/`
  (default `~/Developer/ADELE/judge-io`): four per repeat, at most 50 cells each, twelve in all.

## Items (`items.csv`)

Each item is judged on one rubric. `check` is the item's own test; `target` its expected level.

| set | items | what they are | target |
|---|---|---|---|
| P | 19 on MSm, 20 on MSc | every example bullet, on its own rubric, examples stripped | its own level, within 1 |
| F | 33 on MSm, 33 on MSc | every PLp, PLe and PLs example bullet at Levels 3 to 5, on each rubric | 2 or less (3+ is a leak) |
| S | 10 on MSc, 10 on MSm | MSm's bullets at Levels 3 to 5 on MSc, and MSc's on MSm | none: descriptive |
| L | 5 on MSm, 17 on MSc (+2 void), + 7 human | the lab's MS items (`lab_items.csv`) | the round's recorded level or contrast |
| B | 20 on MSm, 13 on MSc (+1 void) | battery-v1 (`battery_targets.csv`) | battery-v1's registered level; on MSm, decided per item |

**Set L.**
- r30 (MSc): the eight minimal pairs of `r30/cset.csv`, verbatim. r30 registered contrasts, not levels
  (`prereg_r30.json`, C_set and H7):
  - stakes rise while willingness stays fixed (S1 to S2, S3 to S4): no change;
  - resistance rises while the stakes stay trivial (R1 to R2): a rise;
  - one agreeing party becomes three (A1 to A2): no change.

  H7 passes a rubric that matches its own predictions on at least 3 of the 4 contrasts. The pairs were judged
  in r33 (arm `MSc_new`, MSc text of 2026-07-27): 4 of 4. The medians were S 3, 3, 3, 3; R 1, 4; A 1, 1. They
  are the item targets, reported only. S1 and S2 are void (below), so three contrasts remain.
- r36 (MSc): D1 and D2, the minimal pair on plan search. Stored MSc medians 4 and 5.
- r60 (MSm): B1, a stated preference (0); B2, an insincere final price (registered 4); B3, five stated
  diary constraints (0); B4, one belief about another's belief (4).
- r69 (MSm): M5, the turned agent, a three-deep nested route to Level 5 (5).
- r75 (MSc): the nine ladder and carve items R1 to R9, verbatim from the r75 seal. Targets are the r75
  medians, which equal r61's.
- r70 (MSc, `human`): Pablo's labels on seven of r61's items. r61 never saved its texts, so his labels are
  read against r75's reconstructions of the same items (`judged_as`). They add no calls.

**Rebuilt items.** r36, r60 and r69 never saved their item texts, only descriptions. Seven items are new texts
written from those descriptions, marked `rebuilt` in `lab_items.csv` with the description quoted. The r36 pair
reuses the PL regression's rebuild word for word (`make_prompts.py` checks this). These are a fresh measurement
of each design, not a byte-identical rerun. One target departs from the stored median: r60's B2 scored 5, but
RESULTS-r60 records that item as a paraphrase of MSm's Level 5 seller example and its level as unreliable. Its
target is the registered 4, and its check is r60's own rule (3 or more). The rebuilt B2 shares no 4-gram with
the seller example, but its idea (is a "last price" a bluff) stays close to it.

**Set B.** battery-v1's texts, verbatim from the lab record (`7159671`). On MSc: the four pure MSc items, the
three co-occurring items involving MSc (X03, X05, X06R), the three MSc mid-band items and the four anchors. On
MSm: the four anchors and the twelve pure PL items, each with target 0 and check 1 or less. None needs a mind
modelled. P02's guests and S01/S02's staff are agents, but their constraints are stated or only their actions
matter (decisions per item in `battery_targets.csv`). Also on MSm, the four pure MSc items. Their targets are
read from MSm's text, with the reasons in `battery_targets.csv`:
- M01 (shift swap) and M04 (supplier's March date) state the stance and the reasons in full. The stated-stance
  carve applies: target 1, check 2 or less.
- M02 (boundary fence) states both positions, so the carve and Level 5's anti-count guard keep it below 4. But
  how each neighbour will take what the other is offered is not stated, and that needs feelings attributed. It
  is a genuine Level 3 demand: target 3, check 3 or less.
- M03 (premium plan) states what he wants but not why. The carve needs the reasons too, so it does not apply,
  and his reasons must be inferred: target 3, check within 1.

battery-v1 never scored MSm, so the MSm checks are new.
Registered levels come from `prereg.csv` and stored levels from r36's labels (the last full battery run, with
X06R); `make_prompts.py` checks both against the lab record.

**4-gram check (JUDGING.md rule 4).** Every item outside P was checked for shared word 4-grams against every
example bullet of the rubric it is judged on, at build time. Three items are void and are not judged:
- `B-D08-on-MSc` (MSc mid-band, registered 3) shares "and bring them to", "bring them to accept" and "them to
  accept a" with MSc's Level 3 doctor example;
- `L-r30-S1` and `L-r30-S2` (r30's first stakes pair) each share "will hear you out" with MSc's Level 3
  colleague example.

The other 148 checked items share none. So the MSc mid-band check has two items (D04, D07), not three. r30's
stakes contrast rests on S3 to S4 alone.

**Calls.** 180 judged items × 3 repeats = **540 calls** in pass 1 (`ms-labreg1`), plus pass 2.

## Checks (`analysis/analyse.py`)

Each check holds if every one of its items meets its item check. The r30 check is ruled on contrasts within
pairs instead, and its items' own checks are reported only. `lab` checks have a stored result to
reproduce. `new` checks are first measurements: the lab never scored these items on this rubric.

| check | kind | what must hold |
|---|---|---|
| P-MSm placement | new | every MSm example within 1 of its level |
| P-MSc placement | lab | every MSc example within 1 of its level (r34, older text) |
| F-on-MSc no leak | lab | no PL example at Levels 3 to 5 scores 3+ on MSc (r34) |
| F-on-MSm no leak | new | the same on MSm |
| L r30 MSc minimal pairs | lab | r30 H7 on the three remaining contrasts: S4 equals S3, R2 is above R1, A2 equals A1. With S1 to S2 void, "at least 3 of 4" means all three |
| L r36 MSc pair | lab | D1 and D2 within 1 of 4 and 5 |
| L r60 stated-stance carve | lab | B1 at 1 or less, and B2 at 3 or more (r60 rule 2) |
| L r60 anti-count guard | lab | B3 at 3 or less (r60 rule 3) |
| L r60/r69 Level 4/5 boundary | lab | B4 at exactly 4, and M5 at exactly 5 (`MSm.md`, r69 entry) |
| L r75 MSc ladder | lab | R1 to R9 each at its r61/r75 median (r75 rule 1) |
| L r70 human labels | lab | all seven within 1 of Pablo's label (r70: 6 exact, 7 within 1) |
| B MSc high | lab | M01 to M04, X03, X05 and X06R at 4 or more (battery H1, H2) |
| B MSc mid-band | lab | D04 and D07 within 1 of their registered 2 (battery H4) |
| B MSc anchors | lab | L01 to L04 at 1 or less (battery H3) |
| B MSm low | new | the anchors and the pure PL items at 1 or less on MSm |
| B MSm on pure MSc items | new | M01 and M04 at 2 or less, M02 at 3 or less, M03 within 1 of 3 |

## Decision rule

1. A **failure** is a check that does not hold in pass 1.
2. **Pass 2** (`ms-labreg2`, `make_prompts.py --replicate ITEM ...`). Every item behind a failure is judged
   again with the same prompt, under a new id, three more repeats. For the r30 check, these are both items of
   each contrast that went against the prediction.
3. A failure is **confirmed** if the check still fails with the pass-2 labels of those items.
4. **The regression passes** if no failure is confirmed. Otherwise it fails, and the report names each
   confirmed failure and says whether it is `lab` (the lab's result did not reproduce) or `new` (a first
   measurement that came out against the rubric's claim).
5. Set S is not ruled on. Genuine co-loading between the two rubrics is allowed.

Pass 2 is the only guard against judge noise. It is limited to the items that could fail a check.

**Also reported:**
- per set and rubric, how many medians are exact and within 1 of their target, and the leaks in F;
- the S table: each sibling example's own level and its median on the other rubric;
- Pablo's seven labels against today's medians and against r61's, apart from the lab targets;
- today's medians against every stored lab median (exploratory: the stored ones came from older texts or
  other judges);
- how often all three repeats agree, the level counts per rubric, and how many answers were set aside.

## Caveats

- **Stored results are not like for like.** battery-v1, r30/r33, r34 and r36 used MSc texts of late July. r60, r69 and
  r75 used today's operative texts. All used haiku, sonnet and opus with the v1 prompt.
- **Set P is a lower bound.** JUDGING.md rule 2 warns that stripped rubrics under-determine the top band.
  Placement within 1 is the lab's standard for this design.
- **Some foreign examples carry minds.** PLs's Level 5 bank run and arms race are about what agents expect
  others to do. A 3+ on MSm there may be a genuine co-load rather than a leak. The rule still counts it.
- **Human labels ride on reconstructions.** Pablo labelled r61's originals, which are lost.
- **"No change" in r30's contrasts means equal medians.** A one-level wobble on a single item fails the
  contrast. Pass 2 is the guard.
- **The MSm targets for M02 and M03 are my reading of the text.** A different reading is a construct question
  for Pablo, not a judge error.

## Cost

540 Opus-low calls in pass 1, plus up to about 60 in pass 2 and any retries. The PL regression's Opus-low
runs took about 2 to 3 weekly points per 300 calls, so about 4 to 6 points here.

## What happens next

- If the regression passes, MSm and MSc are cleared for real-task labelling with this judge and prompt.
- If it fails, the report names each confirmed failure. No text changes follow from this study alone. A
  `lab` failure points at the judge or the prompt. A `new` failure goes to Pablo as a construct question.

## Predictions (sealed)

Probability that each check holds in pass 1 (before pass 2). Priors: the low band has been stable in every lab
round; disagreement concentrates at Level 3 and above; set P is a lower bound for the top band; and PLs's Level 5
examples (bank run, arms race) are about what agents expect of each other.

| check | p |
|---|---|
| P-MSm placement | 0.55 |
| P-MSc placement | 0.6 |
| F-on-MSc no leak | 0.75 |
| F-on-MSm no leak | 0.35 |
| L r30 MSc minimal pairs | 0.6 |
| L r36 MSc pair | 0.7 |
| L r60 stated-stance carve | 0.7 |
| L r60 anti-count guard | 0.8 |
| L r60/r69 Level 4/5 boundary | 0.45 |
| L r75 MSc ladder | 0.4 |
| L r70 human labels | 0.7 |
| B MSc high | 0.6 |
| B MSc mid-band | 0.7 |
| B MSc anchors | 0.9 |
| B MSm low | 0.7 |
| B MSm on pure MSc items | 0.55 |

- At least one check fails in pass 1: 0.95.
- The regression passes (no failure confirmed in pass 2): 0.3.
- If F-on-MSm fails, every leak is a PLs Level 5 example: 0.7.
