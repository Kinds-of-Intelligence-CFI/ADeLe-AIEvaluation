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

None yet.
