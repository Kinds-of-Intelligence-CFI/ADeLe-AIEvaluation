# Lab regression for PLp candidate C — pre-registration

Committed and pushed before any label of this study, with the items, prompts and analysis script.
Pablo approved the run and its cost on 2026-09-28.

**Question.** Does candidate C change PLp's behaviour on the lab's standing tests?

**Candidate C.** The current `PLp.txt` plus one sentence at the end of the "What this dimension
does not cover" paragraph (`../PLp_candidate_c.txt`):

> Knowing the established method is knowledge rather than planning, so pitfalls that the method
> avoids do not raise this demand.

It mirrors PLs's knowledge carve. On real tasks it moved one Terminal-Bench task from Level 3 to 2
and did no harm on SWE-bench or tau2 (`../RESULTS.md`). Adoption needs this regression first.

**Pass rule, in one line.** C passes if nothing that holds under the current text breaks under C:
example placement, the minimal pairs, the family diagonal and disentanglement.

## Design

- **Two texts.** `cur` is `PLp.txt` as the catalog loads it (sha256 `de98ab35…`). `C` is the
  candidate file (sha256 `937b0ad4…`). `make_prompts.py` asserts that C is `cur` plus the one
  sentence.
- **Both texts are judged on every item.** The lab has no stored result for the current text.
  Every round below predates the 2026-08-24 voice pass and the 2026-08-25 example pass of
  `PLp.txt`. So the stored results serve only as predictions.
- **Judges.** haiku, sonnet and opus, through `adele-judge-low` (effort low; tools Read and Write;
  no CLAUDE.md), relayed by `judge-dispatcher-low`. One item per call. The label is the median of
  the three (with two labels, the lower). Never Fable.
- **Rubric shown.** As the catalog loads it: no `#!` line, examples kept. Set P is the one
  exception: its items are the examples, so all examples are stripped, as in r25.
- **Blinding.** Prompt files have opaque ids. The two texts are shuffled together.
- **Other models.** A safety classifier can make another model write an answer. `writers.py`
  finds the writer of each answer. Answers not written by the judge's registered model
  (`claude-haiku-4-5`, `claude-sonnet-5`, `claude-opus-5-5`) are moved to `responses_fallback/`,
  and the cell is judged once more. If that fails too, the cell has no label.

## Items (`items.csv`)

| set | lab round | items | what they are |
|---|---|---|---|
| P | r25 placement | 20 | PLp's own example bullets. Target: their own level. |
| F | r34 examples disentangle | 32 | PLe, PLs and MSc example bullets at Levels 3 to 5. Target: PLp 2 or less. |
| M | r36 minimal pairs | 5 | A1, A2, A3, D1, D2, rebuilt from the round's descriptions. |
| D | r42/r43 family diagonal | 9 | PLp-1 to 4 (target 3+), PLe-1 to 3 and PLs-1, 2 (target 2 or less), rebuilt. |
| B | battery-v1 | 33 of 36 | The standing battery, verbatim from the lab record (`7159671`). |

**Rebuilt items.** r36 and r42 never saved their item texts, only one-line descriptions. The M and
D items are new texts written from those descriptions (`reconstructed_items.csv`), as r75 and r76
did. They are a fresh measurement of each design, not a byte-identical rerun. PLs-3 (gear train)
is left out: r42 dropped it because it failed its own diagonal.

**4-gram check (JUDGING.md rule 4).** Every item outside P was checked for shared word 4-grams
against every example bullet of the candidate file, at seal time. Any shared 4-gram voids the
item. Three battery items are void and are not judged:
- `B-E03` shares "in the given order" with a Level 0 bullet;
- `B-P03` shares "no standard technique applies" and two more with a Level 4 bullet;
- `B-X01` shares "for which no standard" with the same bullet.

The other 79 checked items share none. Set P is exempt by design: its items are the bullets, and
the rubric shown to its judges has no examples. That leaves 99 items to judge.

**Calls.** 99 items × 2 texts × 3 judges = 594 calls in pass 1 (`labreg-r1`), plus pass 2 below.

## Outcomes checked (`analysis/analyse.py`)

Each is computed separately under `cur` and under C, from the medians.
- **Placement (P).** Each example is placed at its own level.
- **Minimal pairs (M), as r36.** A1 to A2 rises by 2 or more. A1 to A3 does not rise. D1 stays at
  1 or less. D2 reaches 3 or more.
- **Family diagonal (D), as r42.** PLp-1 to 4 score 3 or more. The PLe and PLs items score 2 or
  less. The battery's pure PLp items are checked the same way (3 or more), and its other pure items
  must stay at 2 or less.
- **Disentanglement.**
  - F, as r34: each foreign example scores 2 or less. A 3 or more is a leak.
  - B, as battery-v1: separation in the six directions that involve PLp (gap of 3 or more on all
    but at most one item, with the other dimension at its registered level); co-occurring PLp items
    at 4 or more; anchors at 1 or less; mid-band items within 1 of their registered level.

## Decision rule

1. A **loss** is an outcome that holds under `cur` and fails under C. A **gain** is the reverse.
2. **Pass 2.** Every item behind a pass-1 loss, and every item whose median moves by 2 or more, is
   judged again under both texts (`labreg-r2`, same prompts, new ids, same judges).
3. A loss is **confirmed** if pass 2 repeats it. A move of 2 or more is confirmed if pass 2 moves the
   item in the same direction.
4. **C passes** if no loss and no move of 2 or more is confirmed. Otherwise C fails, and the report
   names each confirmed loss.
5. Gains are reported as changes. They do not fail C.

Pass 2 is the only guard against judge noise. It is limited to the items that could fail C.

**Also reported:**
- per set, how many medians agree exactly between the texts, and how many move down or up;
- a sign test over single-judge labels (C against `cur`, two-sided). A significant shift is
  flagged as a caveat, and does not fail C by itself;
- how often C's judges quote the new sentence, overall and on items that moved;
- exploratory: the current text against the stored lab medians (battery-v1 and rebuilt items).

## Predictions (sealed)

- **C passes: 0.5.**
- Per check, no confirmed loss: placement 0.75, minimal pairs 0.9, family diagonal 0.8,
  disentanglement 0.9. No confirmed move of 2 or more: 0.95.
- If C loses anything, it is an item moving down: 0.9. The items I expect to be at risk are those
  whose difficulty is choosing among known methods: `P-L3-3` and `D-PLp4` (contest programming),
  `B-P01` and `B-P04` (route and picking order), `D-PLp2` (timetabling), `M-A2` (packing),
  `B-D06` (meal plan).
- Single-judge labels: more are lower under C than higher, 0.75. The sign test is significant with C
  lower, 0.3.
- C removes at least one leak in F (a gain): 0.35.
- C's judges quote the new sentence in 10 to 40 per cent of their answers: 0.6.
- Under `cur`, the predicted medians are each item's target: the example's level in P, and the
  stored medians in M, D and B (`items.csv`). Under C, the same. Exploratory: `cur` matches the
  stored medians on at least 80 per cent of the 47 items that have one: 0.6.

## Cost

About 600 calls in pass 1, plus up to about 60 in pass 2 and any retries. Estimated 3 to 6 weekly
points, best guess 4. Pablo chose to run everything at once.

## What happens next

- If C passes, I propose the edit to `src/adele/rubrics/data_v2/Paolo_Pablo/PLp.txt` and an entry
  in `docs/rubric-provenance/PLp.md` recording Pablo's ruling ("knowing the method is knowledge,
  not planning"). They are pushed only with Pablo's explicit OK, since they lie outside
  `experiments/benchmarks/`.
- If C fails, `PLp.txt` stays unchanged and the report names what broke.

## Deviations

None yet.
