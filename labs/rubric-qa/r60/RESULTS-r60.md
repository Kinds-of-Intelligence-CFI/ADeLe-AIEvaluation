# Round 60 — the PLs floor move, and the two MSm cases (2026-08-25)

Judges h/s/o, one item per call, median of three, never Fable. Seal: `sealed_predictions_r60.md`.

## 1. The floor moves cleanly. Rule 1 passes.

| id | item | h | s | o | median | predicted |
|---|---|---|---|---|---|---|
| A1 | forecast the yield on a linked notebook page that no longer exists | 1 | 1 | 1 | **1** | 1 ✓ |
| A2 | count snow days in a supplied table of records | 0 | 0 | 0 | **0** | 0 ✓ |

Pablo's call was right and the change is safe. A fresh absent-referent item lands at 1 from all
three judges, each citing the new Level 1 Note, and the static-record case does not move. The
anchored zeros are untouched.

## 2. MSm case 1: the stated-stance carve is not over-firing

| id | item | h | s | o | median |
|---|---|---|---|---|---|
| B1 | a colleague states her venue preference and her reasons | 0 | 0 | 0 | **0** |
| B2 | a supplier's "final offer" against a full warehouse, a Friday quarter-end, and two prior reopenings | 5 | 5 | 4 | **5** |

The carve does what it should and stops where it should. Opus quoted the guard that makes the
difference, from the Level 4 statement: *"A statement whose sincerity the task itself puts in
question hands nothing over."* So the exclusion zeroes out a sincere stated stance and does not
touch an insincere one. **No text change needed.**

One thing worth Pablo's eye. B2 split 5/5/4 on the L4/L5 discriminator, and the reasoning shows
why. Opus enumerated three attributions and judged them *independently settleable* from the
warehouse, the quarter-end and the reopening history, so no interlock, so 4. Sonnet judged the same
three as mutually constraining, so 5. **The same three attributions were read both ways.** That is
the hardest boundary in MSm and it is not a wording slip on either side.

## 3. MSm case 2: the anti-count guard holds; the nested route is still untested

| id | item | h | s | o | median |
|---|---|---|---|---|---|
| B3 | five department heads, each constraint written down, find one slot | 1 | 0 | 0 | **0** |
| B4 | does the pupil think the teacher already knows | 4 | 4 | 4 | **4** |

B3 is clean: opus quoted the anti-count guard verbatim, *"several parties whose positions are each
stated outright demand no more mind modelling than one, however hard they are to reconcile."* Five
minds, no demand. The guard works.

**B4 does not test what I sealed it to test.** I described it as three nested attributions and then
wrote an item with two: the pupil's belief about the teacher's belief. All three judges correctly
routed it to 4, citing the clause that excludes exactly that case. So the single-nesting exclusion
is confirmed, and the three-deep dyadic route to Level 5 that the rewrite claimed remains untested.

## 4. My item-independence check failed again, on the round where I added it

The seal for this round introduced an explicit item-independence check and asserted it had been
run. It had not been run properly. **B2 is a paraphrase of MSm's own Level 5 example** (a seller's
"final offer" as a bluff), which is why haiku and sonnet both matched it by name.

The directional finding survives, because contamination could only pull B2 *up* and the question
was whether the exclusion pulled it to 0. But the level is unreliable, and this is the eighth
instance of the same failure. The check has to be mechanical rather than asserted: diff every
sealed item against the example bullets of the file it will be scored under, before running.

## Rules

1. Floor moves cleanly — **PASS** (A1 = 1, A2 = 0).
2. Stated-stance carve not over-firing — **PASS** (B1 = 0, B2 = 5), item contaminated.
3. Anti-count guard holds — **PASS** (B3 = 0).
4. Nested dyadic route works — **NOT TESTED**, my item had two attributions, not three.
