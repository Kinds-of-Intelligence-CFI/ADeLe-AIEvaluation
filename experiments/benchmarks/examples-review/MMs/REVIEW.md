# MMs (Working and short-term memory) examples review (draft for Pablo, 2026-10-04)

Source: `src/adele/rubrics/data_v2/Marko/MMs.txt` (Marko). No provenance file. The rubric text was used in the
rivercross MMs pilots (v3–v6, `experiments/rivercross/memory/`), but its examples were never tested. So the bar here
is conservative: fix only clear problems. Nothing has been judged. Confidence is how sure I am that a problem is real.

MMs's driver, from its own text: how much must be held once it is out of view, and how much must be done to it.
L1 one item held, L2 a small set held for under 30 seconds with no manipulation, L3 more items or manipulation
(reverse, rotate, reorder, integrate with new input), L4 a substantial amount with complex manipulation or updating,
L5 an exceptionally large amount with several layers of manipulation.

## Verdicts

| level | example (short) | verdict | why | confidence |
|---|---|---|---|---|
| 0 | read a word in front of you | keep | perception | — |
| 0 | features of a visible object | keep | perception | — |
| 0 | say "dog" at a picture of a dog | keep | automatised recall | — |
| 1 | copy "elephant" after a brief view | keep | one item held | — |
| 1 | add a full stop after reading the instruction once | keep | one instruction held | — |
| 1 | two-digit number that has disappeared | keep | one item held | — |
| 2 | two 3-digit codes after 30 seconds | keep | small set, no manipulation | — |
| 2 | hold one number to check against another sheet | **fix** | one number is L1's "single piece". Checking it against a new figure is L3's "integrated with new input". It fits L2 by neither clause | 0.6 |
| 2 | three words after 20 seconds | keep | small set, short delay | — |
| 3 | reverse a 2–4 digit code | **fix** | 2–4 digits is less than L2's six digits held forward. L3 asks for "a larger amount" with manipulation. The en-dash range is also odd | 0.55 |
| 3 | which shape matches after rotation | keep | rotation is named in L3. Spatial co-load is accepted by the text | — |
| 3 | compare seven names with a list in another document | **fix** | nothing says the first list is out of view. If both documents can be open, nothing is held, which is L0 | 0.5 |
| 4 | 20 names, typed "with their ages" in alphabetical order | **fix** | the ages appear from nowhere. If the list had only names, the ages need other knowledge or memory | 0.45 |
| 4 | redraw a scene from a new angle as if 30 seconds had passed | **replace** | running each element's trajectory forward is PLs's territory, and the new viewpoint is spatial transformation. No one sets this task. Nor does it say the image is removed | 0.6 |
| 4 | 5-minute description of a five-generation family tree | keep | a structure built up from new input and queried. Sits near MMe (see level-statement point 1) | — |
| 5 | single read of a 10-page legal document, then answer questions | **replace** | answering questions about content is retention with no manipulation, below L5's "highly sophisticated operations". It nearly copies MMe L5 (50-page legal document, weeks later), so it teaches judges that "legal document read once" means 5 on both | 0.7 |
| 5 | tour a large building once, then give directions and recall details | **flag** | directions between any two places is real manipulation, so it fits L5's text. But a tour of many minutes and recall of wall colours is long-term spatial and episodic memory (MMe L4's hidden items). The rubric's statements do not draw the line | 0.5 |
| 5 | 15 function prototypes, then check a 25-line snippet | keep | many detailed items held and compared against new input. Natural for code | — |

Counts: keep 11, fix 4, replace 2, drop 0, flag 1.

## Proposed wordings

- **L2, spreadsheet:**
  > Hold four figures from one spreadsheet in memory long enough to type them into another sheet that must be opened afterward.

  A small set, a delay of seconds, no manipulation. L2.
- **L3, reverse code:**
  > Repeat a five-digit code in reverse order, 30 seconds after hearing it.

  About as many digits as L2's two codes, plus a reordering. L3. Five is at the usual backward span, so not L4.
- **L3, seven names:**
  > Read a list of seven names, close it, then open a second list and state which name from the first is missing.

  Seven names held out of view and compared with new input. L3.
- **L4, twenty names:**
  > View a list of 20 names with their ages in one document, close it, then open another document and type them out in alphabetical order.

  The ages are now in the list. Forty bound items held out of view and reordered. L4.
- **L4, replaces the moving scene:**
  > Without a board, follow a chess game as its moves are read out, then say where every piece stands after move 20.

  Thirty-two positions held out of view and updated with each of 40 moves. That is L4's "updating and revising
  earlier memories in light of new input". The moves are given, so PLp is 0. The chess rules supply the model, so
  PLs is at most 2. This is the same construct as the rivercross history-only pilot (object-location updates).
- **L5, replaces the legal document:**
  > Multiply two four-digit numbers in your head, with nothing written down, and state the result.

  Four partial products of up to five digits each, plus carries, held and combined in several layers with no record.
  L5's "multiple layers of manipulation". MMp L3 (long multiplication on paper) is the matching low-memory case.

## Style numbers

| | count | mean words | max words |
|---|---|---|---|
| current | 18 | 19.4 | 34 |
| candidate | 18 | 18.2 | 34 |

v1: mean 25.6 words per bullet. No em dashes or semicolons in the bullets.

## Disentanglement

- **MMe.** The L5 legal document duplicated MMe L5. Replaced. The building tour (flagged) and the family tree (kept)
  still sit near MMe because MMs's levels set no upper bound on delay.
- **MMp.** Mental multiplication carries the long-multiplication routine (MMp L3, intermediate). That co-load is
  below the high band and is the point of the pair.
- **PLs.** The moving-scene example asked for trajectories to be run forward. Replaced. Nothing else loads PLs.
- **PLp, PLe, MSm, MSc.** No load. Blindfold chess asks only to track given moves, not to choose them.

## Problems in the level statements (not changed, reported only)

1. **No upper bound on delay, so no line to MMe.** L2 says "under 30 seconds". L4 and L5 say only "recently presented
   information that is no longer perceptually available". Material held for minutes (a building tour, a 5-minute
   description, a 10-page read) fits both MMs and MMe. MMe's preamble puts the line at "beyond immediate working
   memory", but MMs never states it.
2. **Two drivers at L3 joined by "or".** L3 is "a larger amount or more detailed information", which "may need" to be
   manipulated. A small amount with manipulation, or a large amount without it, has no clear level. Desideratum 3.
3. **No reading for model tasks.** For an LLM, "no longer perceptually available" is undefined. Is text earlier in
   the context available? The rivercross pilot made it workable by hiding the current state and showing only the
   move history. That reading is not in the rubric.
4. **No "does not cover" paragraph.** Nothing separates holding information from finding it (v1 AS, flagged in
   `docs/taxonomy-provenance.md`) or from reasoning over it.
5. **v6 pilot note:** the top of the scale saturated at 4 for two judges, and the L5 anchor was used by one judge
   only. The L5 examples matter more than usual here.

## Open questions for Pablo

1. Point 1 above. Where does MMs end and MMe begin: 30 seconds, "while the task is under way", or something else?
   The building-tour flag depends on it.
2. The L5 replacement could be judged 4 rather than 5. Four-digit mental multiplication is beyond most adults but
   is routine for trained mental calculators. Five digits would be safer for L5 but less natural. I chose four.
3. The blindfold-chess example could be judged 5. I used move 20 to keep it at L4.
4. Marko should see these changes. None of them has been placed by a judge.
