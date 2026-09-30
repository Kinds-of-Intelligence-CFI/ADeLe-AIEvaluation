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
