# plp-b2 — results

**Question.** Does candidate B2 make the PLp judges follow search rather than solution length? B2
says only choices that could go wrong add to planning demand, and adds one contrasting pair of
examples.

**Answer.** No. On the same 54 river-crossing states, B2's labels still follow length (+0.37,
p = 0.0002) and not search (+0.13, p = 0.22). That is essentially what the current text gave (+0.33 and
+0.10). The judges read and use the new examples: 154 of 162 answers cite them. But they use them as a
type label. Any river-crossing state with an interacting constraint is matched to the Level 3
sliding-block example, whatever the amount of search.

**Status.** B2: complete (2026-09-30). All three pre-registered tests failed. Candidate S, the structural
change (amendment 1), passed the exit criterion narrowly on the same 54 states: search bits +0.23
(p = 0.002) against length +0.21 (p = 0.004). It still fails E3. On the SWE-bench gate tasks (amendment 2), S's labels track solve rate more
strongly than the current text's: ρ = −0.73 against −0.55 on 37 tasks. All three sanity checks hold. Next
comes the lab regression, in a fresh session. Nothing changes in `src/` yet.

## Design

See `PREREGISTRATION.md`, pushed before any label (`d207da2`). The 54 states, prompt builder and judge
are those of `rivercross-v2` amendment 2 (run `rc-search`). Only the rubric text differs. Opus low
judged each state three times, and the label is the median. All 162 answers were written by
`claude-opus-5-5` and parsed; the protocol check was clean.

## Pre-registered results

From `results/b2_search.json` (`analysis/analyse.py`).

| test | B2 | current text | holds |
|---|---|---|---|
| E1 (exit). PLp ~ bits + ctg: bits > 0, p < 0.05, and above ctg | bits +0.13 (p = 0.22), ctg +0.37 (p = 0.0002) | bits +0.10, ctg +0.33 | no |
| E2. ctg coefficient below the current text's | 0.366 | 0.328 | no |
| E3. Spearman with Opus 5.5's non-optimal share ≥ 0.3 | 0.19 | −0.02 | no |

Pre-registered probabilities: E1 0.35, E2 0.6, E3 0.3.

**Reading, as fixed in advance: both E1 and E2 fail, so the wording does not change behaviour.** The
choice is now between a structural change to the levels and accepting that PLp, as judged, is a
length-weighted difficulty measure.

## Exploratory results

- **Why it failed.** 154 of 162 answers cite the new examples, and 17 quote the new sentence. A typical
  answer, for a state 8 crossings from the goal with high search bits, says no ready-made routine "like
  the Hanoi recursion" fixes the moves, so it matches the sliding-block example at Level 3. The judges
  sort puzzles by kind: routine (Hanoi) against constrained search (sliding block). Within the kind
  "search", nothing in the levels grades how much search there is. So nearly every state lands at 3,
  and the few below 3 are the shortest.
- **Levels.** B2 gives 35 states at 3, 14 at 2, 3 at 1 and 2 at 0. The current text gives 30, 20, 3
  and 1. So B2 lifts labels slightly (mean +0.06) and matches the current text on 80% of states.
- **The short, trappy cell** (2–3 crossings, high bits) rises from 2.33 to 2.50, and the short, easy
  cell falls from 1.50 to 1.17. This is the intended direction, but small. The correlation with Opus
  5.5's non-optimal share rises from −0.02 to 0.19.
- All three repeats agreed on 67% of states under B2, and on 59% under the current text.

## What this implies

PLp's levels are kinds of planning: given, retrieved, assembled, searched, constructed and invented.
They are not amounts. Every river-crossing state is the same kind, "searched", so the rubric has no
place to put more or less search. The judges fall back on how long the solution looks. A sentence or
an example cannot fix this, because the scale itself lacks the axis. The options:
1. **Structural:** grade Levels 2–4 partly by how much search is needed, meaning how many choices can
   go wrong and how far ahead they must be looked at, not only by the kind of planning.
2. **Accept:** keep PLp as a kind-of-planning scale that predicts difficulty well on benchmarks, and
   state openly that it does not measure the amount of search within a kind. Leave amount-of-search
   to a separate measure.

This is a methodology decision for Pablo and the team.

## Amendment 1: candidate S, the structural change

Pre-registered before any of its labels (`f22cf47`). S is B2 plus a placement rule: the level is the higher
of the kind of planning and the size of the search. It adds a small, moderate or large search at Levels 2,
3 and 4, a Level 4 example of a large pure search, and a Level 5 note that search size alone does not
reach 5. From `results/s_search.json` (`analysis/analyse.py --run s-search --out s_search.json`). All 162
answers were written by `claude-opus-5-5` and parsed; the protocol check was clean.

| test | S | B2 | current text | holds (S) |
|---|---|---|---|---|
| E1 (exit). bits > 0, p < 0.05, and above ctg | bits +0.23 (p = 0.002), ctg +0.21 (p = 0.004) | +0.13 / +0.37 | +0.10 / +0.33 | **yes** |
| E2. ctg coefficient below 0.328 | 0.213 | 0.366 | — | yes |
| E3. Spearman with Opus 5.5's non-optimal share ≥ 0.3 | 0.05 | 0.19 | −0.02 | no |

Pre-registered probabilities: E1 0.45, E2 0.55, E3 0.35.

**Reading, as fixed in advance: E1 holds, so the SWE-bench gate sanity check and the lab regression come
next.** The pass is narrow. The search coefficient only just exceeds the length coefficient, and both
remain significant.

**Mean PLp by cell under S** (current text in brackets):

| crossings left | bits low | bits mid | bits high |
|---|---|---|---|
| 2–3 | 1.50 (1.50) | 2.00 (2.33) | 2.33 (2.33) |
| 4–6 | 2.00 (2.33) | 2.33 (2.50) | 2.17 (2.67) |
| 7+ | 2.17 (3.00) | 2.50 (2.67) | 2.83 (2.83) |

Exploratory:
- **Where the gain comes from.** S mostly brings long, easy states down: 7+ crossings with low bits
  fall from 3.00 to 2.17. It does not lift short, trappy states: 2–3 crossings with high bits stay at
  2.33. So the length effect shrinks, but S does not yet see the states strong solvers find hardest
  (E3 fails).
- **Labels compress to 2.** S gives 38 states at 2, 14 at 3, 1 at 1 and 1 at 0. The current text gives
  20, 30, 3 and 1. The mean shift is −0.26, and S matches the current text on 63% of states. No state
  reaches 4.
- **Repeats agree much more.** All three repeats agreed on 83% of states under S, against 59% under
  the current text. The rule seems to make judgements more consistent.
- **The judges use the rule sparingly.** 33 of 162 answers cite the size of the search. A typical
  answer places a small puzzle at 3 because "the plan still has to be found by a small search that
  looks a few steps ahead". It keeps it below 4 because "the state space is tiny, only a few choices
  could go wrong".

Caveats:
- The pass is narrow on 54 states, with one judge.
- Compressing labels to 2 could reduce the benchmark correlations. The SWE-bench sanity check exists
  to test that.

## Amendment 2: SWE-bench sanity check for S

Pre-registered before any of its labels (`e60bfc8`). The run covers PLp on the 44 SWE-bench Verified
gate tasks, one Opus-low call each, with the v2 prompt. The baseline is the current text with the same
builder and judge (`natural-prompt`, `npb-gate-opuslow`); prompts were hash-checked. All 44 answers
were written by `claude-opus-5-5` and parsed; the protocol check was clean. From
`results/s_swe_gate.json` (`analysis/swe_gate.py`).

| test | result | prediction (p) | holds |
|---|---|---|---|
| G1. S vs solve rate < 0, p < 0.05 (37 solvable tasks) | ρ = −0.73, p = 2 × 10⁻⁷ | 0.75 | yes |
| G2. at most 0.15 weaker than the current text (−0.55) | 0.18 stronger | 0.6 | yes |
| G3. most common level at most 85% | 68% (30 of 44 at 2) | 0.75 | yes |

**Reading, as fixed in advance: all three hold, so the lab regression comes next,** in a fresh session
and pre-registered first.

Exploratory:
- **Levels.** S gives 13 tasks at 1, 30 at 2 and 1 at 3. The current text gives 18 at 1 and 26 at 2. S
  matches the current text on 77% of tasks, with a mean shift of +0.14. So on SWE-bench, S moves a few
  bug fixes from 1 to 2 and sharpens the ordering. Unlike on the puzzles, it does not compress labels
  to 2.
- **The gain may partly be noise.** It rests on one call per task and 37 tasks. The 95% intervals of
  the two correlations overlap widely. The safe conclusion is that S does not weaken the benchmark
  link, and it may strengthen it.

## Deviations and caveats

- No deviations.
- The test uses one judge and one testbed, with small puzzles. On real tasks, kinds of planning may
  vary more than on these puzzles.

## Reproduce

```
python experiments/benchmarks/plp-b2/analysis/analyse.py
```

## Amendment 4 — candidate S-q (search size as odds): fails the exit test; S is frozen

Pre-registered before any label (`77603b2`). S-q is S with the size of the search defined by odds
(how rarely a plan works when built with the usual methods but without looking ahead), with
thresholds of one in four and one in a hundred.

**Rivercross, run `sq-search`** (`results/sq_search.json`). 162/162 answers, all by Opus 5.5.

| | S-q | S | current text |
|---|---|---|---|
| bits coefficient | +0.18 (p = .024) | +0.23 (p = .002) | +0.10 (ns) |
| ctg coefficient | +0.25 (p = .003) | +0.21 (p = .004) | +0.33 |
| E1: bits > 0, significant, and above ctg | **fails** | holds | fails |
| E2: ctg below the current text | holds | holds | — |
| E3: Spearman with Opus non-optimal share ≥ 0.3 | fails (0.05) | fails (0.05) | — |
| levels 0/1/2/3 | 2/0/38/14 | 1/1/38/14 | — |
| all three repeats agree | 74% | 83% | 59% |

Mean PLp by cell (crossings left × search bits): the 2–3 crossing, low-bits states sit at 1.33. Every
other cell lies between 2.17 and 2.67. The odds wording is read: 106 of 162 answers (65%) quote it.
But the levels barely move. S-q labels the grid almost exactly as S does, with a little more weight
on length.

**SWE-bench gate, run `sq-swe-gate`** (`results/sq_swe_gate.json`; run alongside, as pre-registered).
44/44, all by Opus 5.5. ρ = −0.724 with solve rate (S −0.729, current text −0.554); levels 1/2 = 14/30.
G1–G3 hold.

**Lab regression:** not run, as pre-registered (E1 failed).

**Decision (Pablo's rule, 2026-10-01): S-q is not accepted. S is frozen** as the PLp candidate, with its
narrow lab-regression loss (the covering letter, 1 → 2) on record.

**Predictions.**

| prediction | p | outcome |
|---|---|---|
| E1 holds | 0.5 | failed |
| bits coefficient above S's (0.230) | 0.45 | failed (0.179) |
| ctg coefficient below S's (0.213) | 0.5 | failed (0.246) |
| E3 holds | 0.25 | failed |
| fewer states at Level 2 than S (38) | 0.55 | failed (38) |
| G1–G3 hold | 0.75 | held |
| SWE Spearman stronger than S's | 0.35 | failed (−0.724 against −0.729) |
| S-q accepted | 0.25 | failed |
| odds quoted in 30% or more of rivercross answers | 0.6 | held (65%) |

**Reading.** Telling the judges how to measure the search does not make them measure it better. They
quote the odds, but they estimate them from how long and involved the state looks, so the length
signal persists. The gain from S over the current text came from the structural rule (place the task
at the higher of the two), not from how the size of the search is worded. Two cautions. With 54 states
and three repeats, the S and S-q coefficients are within noise of each other (both have SEs near 0.07).
And E1 is a strict test: S-q's bits effect is still significant.

## Amendment 5 — candidate O (odds as the single driver): fails narrowly, on the same item as S

Pre-registered before any label (`ba00f4f`). Every answer was written by Opus 5.5, with no classifier stop.

**Decision rule: O does not replace S.** The lab regression fails on one confirmed loss, the covering letter
(Level 1 example), as it did for S. The SWE gate holds. Under the rule, S stays frozen.

**1. Lab regression** (`../plp-candidate/lab-regression/results/regression_o.json`).

| | O | S | reference (current text) |
|---|---|---|---|
| checks holding (of 101) | 86 | 83 | 83 |
| pass-1 losses | covering letter | covering letter | — |
| confirmed in pass 2 | yes: O 2, 2, 2 against current 2, 1, 1 | yes | — |
| moves of two levels | none | none | — |
| Mars-landing PLe example (a leak) | 3 | 4 | 3 |
| all three repeats agree | 82% | 82% | — |

- **Format pairs (set U): no split.** All 18 labels are 3, open and multiple choice alike.
- Gains over the reference: the Level 2 city-day example now lands at 2; two MSc examples stop leaking
  (lease 3 → 2, MSc L5 3 → 2); battery M04 moves off the diagonal as registered. Five PLs examples drop by one.
- The new Level 4 timetabling example lands at 4. Route (`B-P01`) and van packing (`M-A2`) go to 4. Exam
  timetabling (`D-PLp2`) stays at 3.
- O's text is quoted (odds, undoing, step by step) in 246 of 324 answers (76%).

**The covering letter.** Judges under every text agree on the facts: a template, some selection of CV
points, choices that do not interact, a plan that almost always works first time. They split only on
whether selecting evidence is assembling subtasks (2) or lies inside the routine (1). Levels 1 and 2 both
have odds near one, so O's odds cannot decide it. Pooled Opus v2 labels: current text 2 of 6 at Level 2,
S and O 10 of 12 (Fisher p = 0.11). S and O share B2's scope sentence ("Only choices that could go wrong
add to this demand"), which the current text lacks, and judges under O start from that framing ("the only
real decisions are which CV items…"). That sentence is the likely common cause. Untested.

**2. SWE gate** (`results/o_swe_gate.json`). ρ = −0.706 with solve rate (S −0.729, current −0.554); levels
1/2/3 = 13/30/1. G1–G3 hold.

**3. Rivercross levels** (`results/o_search.json`; descriptive). Bits +0.216 (p = .005), ctg +0.218
(p = .005); current text ctg +0.328. E2 holds; E1 is a tie. Spearman with Opus's non-optimal share 0.29
(S 0.05, S-q 0.05): the closest any text has come to E3. Levels 0/1/2/3 = 1/4/39/10, no Level 4.

**4. Odds elicitation** (`results/o_odds.json`; exploratory). Judges put nearly every state at "one time in
1 to 3" (10th–90th percentile). Spearman with bits 0.24 (ns), with ctg 0.36. Q1 and Q2 fail. This test is
weak, as flagged before it ran: bits count random non-undo sequences, but O's agent puts a slip right as
soon as it shows, and on these puzzles an unsafe crossing shows at once. For O's agent the true odds may
well be high. The run shows that judges do not see rivercross states as sparse searches. It does not show
they misjudge O's quantity.

**Predictions.**

| prediction | p | outcome |
|---|---|---|
| lab regression passes | 0.45 | failed (covering letter) |
| covering letter at Level 1 in pass 1 | 0.65 | failed (2) |
| format pairs all equal in pass 1 / no confirmed split | 0.45 / 0.7 | held / held |
| timetabling example at 4 / `D-PLp2` at 4 | 0.5 / 0.4 | held / failed |
| O's text quoted in 30% or more of lab answers | 0.7 | held (76%) |
| G1–G3 hold / Spearman stronger than S's | 0.75 / 0.3 | held / failed (−0.706) |
| rivercross ctg below current / E1 / any state at 4 | 0.6 / 0.35 / 0.2 | held / failed (tie) / failed |
| odds elicitation Q1 / Q2 | 0.5 / 0.4 | failed / failed |
| O replaces S | 0.35 | failed |

**Reading.** O behaves at least as well as S everywhere the lab measures, and better on leaks (86 against 83
checks, the Mars-landing leak gone). It fails on the same single item as S, which is a 1/2 boundary that
O's odds by design do not reach. The rule treats O and S alike, so both carry the same loss.

## Amendment 6 — O′ screen (O without "Only choices that could go wrong…"): fails

Pre-registered before any label (`a4afbcb`); details in `../plp-candidate/lab-regression/results/screen_o2.json`.
75 calls, all parsed, all by Opus 5.5.

- **(a) fails.** The covering letter is at Level 2 in 6 of 6 O′ labels (O: 5 of 6). Removing the sentence does not
  bring it back to 1. The sentence is not the cause.
- **(b) fails narrowly.** Set P examples at their own level: O′ 16 of 23, O 17. The template webpage (Level 2) drops to 1.
- **(c) holds.** No set-P median moves by two levels. One example moved by one.
- Misses shared by O and O′: temperature conversion and real-time translation (Level 0, read 1 and 3), the
  covering letter, the unclimbed face (4, read 3), synthesis route and research programme (5, read 4). These
  misses predate both candidates (see the C run's exploratory section).

**Predictions.** (a) 0.45: failed. (b) 0.7: failed. (c) 0.95: held. Screen passes 0.35: failed. The letter's O
labels in r4 to r6 mostly 2: 0.75, held (2, 2, 2).

**Reading.** The covering letter's move to Level 2 is not caused by that sentence. With examples stripped, the
letter now reads 2 under S, O and O′ alike. Under the current text it read 2 in 2 of 6 v2 labels and in the C
run's three-judge median. It is a 1/2 boundary item that every candidate tested here tips to 2, and no wording
tested isolates why. By the rule, S stays frozen. Whether to accept O with this one-item loss on record is Pablo's
decision.

## Decision (Pablo, 2026-10-01): O is adopted

Pablo accepted O despite its one-item lab loss (the covering letter, a 1/2 boundary item no tested wording fixes).
`src/adele/rubrics/data_v2/Paolo_Pablo/PLp.txt` is now `PLp_O.txt` (sha256 `322674ef…`, MANIFEST updated); the change
record is in `docs/rubric-provenance/PLp.md`. S is superseded. Next: the real-task PLp relabel, pre-registered first.
