# plp-b2 — pre-registration

Committed and pushed before any label of this study.

**Background.** `rivercross-v2` found that PLp, as the judges apply it, follows the length of the
remaining solution and not the search it needs, while strong solvers find search hard. Pablo chose
option B2 on 2026-09-30: say in the description that only choices that could go wrong add to planning
demand, and add one contrasting pair of examples. He approved the wording the same day.

**The candidate** (`PLp_B2.txt`, built by `make_b2.py`). It is the current
`src/adele/rubrics/data_v2/Paolo_Pablo/PLp.txt` plus exactly these insertions, which the script checks:
- **Description**, after the sentence about length: "Only choices that could go wrong add to this
  demand. A step with one sensible option, or a choice where every option works, adds nothing, however
  many such steps there are."
- **Level 1 example:** "Move a tower of eight disks from one peg to another under the usual rules.
  The standard recursive procedure fixes all 255 moves, so nothing has to be searched for."
- **Level 3 example:** "Solve a sliding-block puzzle that is four moves from solved, where the move
  that looks most natural blocks the only way out."

No level definition changes. The new examples are not river-crossing puzzles. They share no word
4-gram with the 54 test frames.

**Order of tests.** This test comes first, because it is cheap and decisive. The lab regression
(JUDGING.md) is pre-registered separately, and only if E1 holds. Adoption in `src/` then needs Pablo's
OK and the team's.

## Test 1: run `b2-search`

- **States.** The same 54 states as `rivercross-v2` amendment 2: a 3 × 3 grid of crossings left by
  search bits.
- **Judging.** The same prompt builder (v2) and the same judge (Opus low, three repeats, median).
- **Only the rubric text differs** from run `rc-search`, the current text.

**Tests** (`analysis/analyse.py`). Predictors are standardised; OLS uses HC3 standard errors.

| test | holds if | p |
|---|---|---|
| **E1 (exit criterion).** PLp ~ bits + ctg under B2 | bits coefficient > 0 with p < 0.05, and larger than ctg's | 0.35 |
| E2 | B2's ctg coefficient below the current text's (0.328) | 0.6 |
| E3 | Spearman of B2's PLp with Opus 5.5's non-optimal share (amendment 3) at least 0.3 | 0.3 |

**Reading, fixed in advance.**
- **E1 holds:** B2 makes the judges follow search. Next come the lab regression, then the team, then
  the relabel.
- **E1 fails but E2 holds:** B2 weakens the length effect without making search visible. The next step
  is more examples, or examples at the 2/3 boundary.
- **Both fail:** the wording does not change behaviour. Then the choice is between a structural change
  to the levels and accepting that PLp, as judged, is a length-weighted difficulty measure.

**Descriptive.** Level counts, cell means under B2 and under the current text, agreement between them,
and repeat agreement.

## Cost

162 Opus-low calls, under 1 weekly point.

## Deviations

None. See `RESULTS.md`.

## Amendment 1 — candidate S, the structural change (2026-09-30, before any of its labels)

**Why.** B2 failed because PLp's levels are kinds of planning, not amounts. Every river-crossing state
is the same kind, so the scale had no place for more or less search. Pablo chose to change the
structure and approved the wording of the level sentences. He asked for the cap to be set from first
principles.

**Principle.** Planning demand is the search a competent solver must still do after using what they
know, since knowledge collapses search. The kinds of planning are proxies for typical search sizes.
So the size of the search can place a task directly.
- **It can reach Level 4.** A deep search with no shortcut is hard whether or not a decomposition is
  discovered, and capping it lower would squeeze the hard end of the scale.
- **It cannot reach Level 5.** A vast search with a known method is mechanical, and one without any
  method is invention, which is what defines Level 5.

**Candidate S** (`PLp_S.txt`, built by `make_s.py`). It is B2 plus:
- **Introduction:** "Two things set the level: the kind of planning the task needs, and the size of
  the search it needs. The size of the search is how many choices could go wrong and how far ahead
  their consequences show. Place the task at the higher of the two."
- **Level 2:** "Or the search is small: a few choices could go wrong, but each shows its consequence
  at once or one step later, so no looking ahead is needed."
- **Level 3:** "Or the search is moderate: several choices could go wrong, and their consequences show
  only a few steps later, so options must be compared by looking ahead."
- **Level 4:** "Or the search is large: many choices could go wrong and depend on one another, their
  consequences show only far ahead, and most plans that look workable fail." Plus the example:
  "Timetable twelve exams into five slots under stated clashes and room limits, where most partial
  timetables that look fine fail only when the last few exams are placed."
- **Level 5:** "The size of the search alone does not place a task here."

No new text shares a word 4-gram with the 54 frames.

**Run `s-search`.** The same 54 states, builder and judge as `b2-search` (Opus low, three repeats,
median). `analysis/analyse.py` gained `--run` and `--out` options. Its defaults are unchanged, and
rerunning them reproduces `b2_search.json` byte for byte.

**Tests** (as for B2):

| test | holds if | p |
|---|---|---|
| **E1 (exit criterion)** | bits coefficient > 0 with p < 0.05, and larger than ctg's | 0.45 |
| E2 | ctg coefficient below the current text's (0.328) | 0.55 |
| E3 | Spearman with Opus 5.5's non-optimal share at least 0.3 | 0.35 |

**Descriptive.** How many states reach Level 4, by cell.

**Reading.**
- **E1 holds:** next are the SWE-bench gate sanity check (44 tasks) and the lab regression, each
  pre-registered before it runs.
- **E1 fails:** the judges cannot estimate the size of the search from a state's text, even when the
  scale asks for it. PLp is then kept as a kind-of-planning scale, and this is reported to the team.

**Cost.** 162 Opus-low calls, under 1 weekly point.

## Amendment 2 — SWE-bench sanity check for candidate S (2026-09-30, before any of its labels)

**Why.** S passed the rivercross exit criterion, but its labels bunch at 2. The next step fixed in
amendment 1 is to check that S keeps PLp's link to difficulty on a real benchmark.

**Run `s-swe-gate`** (`make_s_swe.py`). PLp on the 44 SWE-bench Verified gate tasks, one Opus-low call
each, with the v2 prompt. The baseline is `natural-prompt` run `npb-gate-opuslow`: the same tasks,
builder and judge with the current text. Every baseline prompt was rebuilt and matched its stored hash,
so only the rubric differs.

**Tests** (`analysis/swe_gate.py`), over the 37 solvable gate tasks (solve rate at least 0.05), as in
`swebench-pl`:

| test | holds if | p |
|---|---|---|
| G1 | Spearman of S's PLp with solve rate < 0, one-sided p < 0.05 | 0.75 |
| G2 | S's Spearman at most 0.15 weaker (closer to zero) than the current text's | 0.6 |
| G3 | no collapse: the most common level holds at most 85% of the 44 tasks | 0.75 |

The baseline value was known before this pre-registration: ρ = −0.554 for the current text on the 37
tasks, from existing labels. The synthetic test of the analysis script printed it. So G2 asks S to
reach −0.404 or stronger.

**Reading.**
- **G1–G3 hold:** the lab regression comes next, in a fresh session, pre-registered first.
- **G1 or G2 fails:** S trades benchmark validity for construct validity. Pablo and the team decide
  between S, the current text, and a revision.
- **G3 fails:** the scale collapses on real tasks, and S needs revision before anything else.

**Cost.** 44 Opus-low calls.

## Amendment 3 — lab regression for candidate S (2026-09-30, before any of its labels)

S passed the SWE-bench gate (amendment 2), so the lab regression runs next. It is pre-registered in
`../plp-candidate/lab-regression/PREREGISTRATION.md`, section "Candidate S", with the lab's items
and checks: v2 prompt, S only, Opus low with three repeats, runs `labreg-s1` and `labreg-s2`.

## Amendment 4 — candidate S-q: search size as odds (2026-10-01, before any of its labels)

**Why.** S failed its lab regression narrowly: the covering-letter example (Level 1) read 2, through
the "search is small" clause. S measures the search by counting choices that could go wrong, and a
count grows with the length of a task. Pablo asked to quantify the size of the search better before
testing a fix, and chose to define it by odds (2026-10-01). This is the search-bits measure of
`rivercross-v2` put into words. It is length-invariant: a long task whose method fixes every step
has odds of one. And it settles the covering letter without an extra sentence, since almost any
sensible letter works.

**Candidate S-q** (`PLp_Sq.txt`, built by `make_sq.py`). It is S with four sentences replaced:
- Introduction: "The size of the search is how rarely a plan works when it is built by someone who
  knows the usual methods for this kind of task but does not look ahead."
- Level 2: "Or the search is small: such a plan works at least one time in four, and any slip shows
  at once."
- Level 3: "Or the search is moderate: such a plan works between one time in four and one in a
  hundred, so options must be compared by looking ahead."
- Level 4: "Or the search is large: such a plan works less than one time in a hundred, and most plans
  that look workable fail only far ahead."

The thresholds are about 2 and 6.6 bits. No new text shares a word 4-gram with the 54 frames or the
lab items.

**Three tests, as for S, in this order.**
1. **Rivercross, run `sq-search`.** The 54 states of `s-search`, Opus low, three repeats, median.
   `analysis/analyse.py --run sq-search --out sq_search.json`. Tests E1 (exit), E2 and E3 as for S.
2. **SWE-bench gate, run `sq-swe-gate`.** The 44 tasks of `s-swe-gate`, one Opus-low call each.
   Every S prompt was rebuilt and matched its stored hash. `analysis/swe_gate.py --run sq-swe-gate
   --out sq_swe_gate.json`. Tests G1 to G3 as for S (G2 against the current text, ρ = −0.554).
3. **Lab regression, runs `labreg-sq1` and `labreg-sq2`.** Exactly the design and rule of S's lab
   regression (`../plp-candidate/lab-regression/PREREGISTRATION.md`, "Candidate S"), with S-q in place
   of S. `make_prompts_s.py --candidate sq`, `analysis/analyse_s.py --candidate sq`.

Tests 1 and 2 run together. Test 3 runs only if E1 and G1 to G3 hold.

**Decision rule (Pablo, 2026-10-01).** S-q is accepted if E1 holds, G1 to G3 hold, and the lab
regression passes. Otherwise S is frozen, and the next step is to plan the remaining experiments.

**Also reported, against S** (not ruled on). Bits and ctg coefficients, E3, level counts and repeat
agreement on rivercross; the SWE Spearman; the covering letter's level; and how often answers quote
the odds ("one time in", "one in a hundred").

**Predictions (sealed).**
- E1 holds: 0.5. S-q's bits coefficient above S's (0.230): 0.45. Its ctg coefficient below S's (0.213): 0.5.
- E3 holds: 0.25.
- Fewer rivercross states at Level 2 than under S (38 of 54): 0.55.
- G1 to G3 hold: 0.75. S-q's SWE Spearman stronger than S's (−0.729): 0.35.
- The lab regression passes, given it runs: 0.45. The covering letter is at Level 1 in pass 1: 0.55.
- S-q is accepted: 0.25.
- Rivercross answers quote the odds in 30 per cent or more of cases: 0.6.

**Cost.** 162 + 44 + 306 Opus-low calls, plus pass 2. About 3 to 4 weekly points.

## Amendment 5 — candidate O: odds as the single driver (2026-10-01, before any of its labels)

**Why.** S-q failed E1, but a bootstrap showed that E1 cannot separate the texts: the chance that bits beats
crossings left is 0.58 for S and 0.23 for S-q, and they label 87% of states alike. Pablo prefers S-q's idea
(search measured by odds) and asked for it to be made sound. Review against the desiderata found three
problems in S and S-q. First, "two things set the level … the higher of the two" makes two drivers
(desideratum 3). Second, naming levels in the preamble breaks the v1 shape (desideratum 7). Third, odds of a
"plan works" grow with length, and they overlap with UG, which is the success floor of a blind guesser. O
was rewritten with Pablo, sentence by sentence, on 2026-10-01.

**Candidate O** (`PLp_O.txt`). One driver: the search that remains for someone who has the knowledge the
task calls for (knowing how tasks of a kind are done is knowledge, not planning). It rises with how rarely a
plan built step by step comes out workable without an earlier step having to be undone, and with how far
back the undoing reaches. Each level keeps S's description and ends with one odds anchor: a plan built
from the routine is never undone (1); hardly ever, however many steps (2); workable between one time in two
and one in a hundred (3); less than one in a hundred, undone far back (4); almost never, as no knowledge
structures the search (5). Where description and odds disagree, the odds decide. The scope paragraph adds
that answer format adds nothing, and that for a task scored partway through the plan is the one still to be
made. The Level 4 timetabling example is reworded to the odds. No text new in O shares a word 4-gram with
the 54 frames or the lab items.

**Tests.**
1. **Lab regression, runs `labreg-o1`/`labreg-o2`** (confirmatory). S's design and rule
   (`../plp-candidate/lab-regression/PREREGISTRATION.md`, "Candidate S"), with O in place of S, plus set U:
   three minimal pairs (`format_pairs.csv`), each one planning problem posed open-ended and as four listed
   options. A pair fails if its two items get different medians in pass 1 and again in pass 2 (both re-judged
   under both texts). 108 items, three Opus-low repeats.
   `make_prompts_s.py --candidate o`, `analysis/analyse_s.py --candidate o`.
2. **SWE-bench gate, run `o-swe-gate`** (confirmatory). G1–G3 as for S. `analysis/swe_gate.py --run o-swe-gate
   --out o_swe_gate.json`.
3. **Rivercross levels, run `o-search`** (descriptive). E1–E3 reported, not ruled on: E1 cannot separate texts.
   `analysis/analyse.py --run o-search --out o_search.json`.
4. **Odds elicitation, run `o-odds`** (exploratory). The same 54 states, one Opus-low call each, with a prompt
   that asks only for O's odds ("one time in N"), not a level. It asks whether judges can estimate the quantity
   O is built on. Q1: Spearman of log2 N with search bits at least 0.5. Q2: in log2 N ~ bits + ctg, bits is
   significant and above ctg. Bits are a proxy: they count random non-undo sequences, not O's agent.
   `analysis/odds_o.py`.

All four run together.

**Decision rule.** O replaces S as the frozen PLp candidate if the lab regression passes (including the format
pairs) and G1–G3 hold. Otherwise S stays frozen. Tests 3 and 4 inform the write-up and the team, not the
decision. Adoption in `src/` still needs Pablo's explicit OK.

**Predictions (sealed).**
- Lab regression passes: 0.45. The covering letter is at Level 1 in pass 1: 0.65.
- Format pairs: all three equal in pass 1: 0.45. No confirmed split: 0.7. If a pair splits, the
  multiple-choice item is lower: 0.8.
- The Level 4 timetabling example lands at 4: 0.5. `D-PLp2` (exam timetabling) reaches 4: 0.4.
- Lab answers quote the odds or the undoing in 30% or more of cases: 0.7.
- G1–G3 hold: 0.75. O's SWE Spearman stronger than S's (−0.729): 0.3.
- Rivercross: ctg coefficient below the current text's (0.328): 0.6. E1: 0.35. Any state at Level 4: 0.2.
- Odds elicitation: Q1 0.5, Q2 0.4.
- O replaces S: 0.35.

**Cost.** 324 + 44 + 162 + 54 = 584 Opus-low calls, plus pass 2. About 4 to 5 weekly points.
