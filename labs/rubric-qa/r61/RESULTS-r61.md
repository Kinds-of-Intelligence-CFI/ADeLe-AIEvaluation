# Round 61 — MSc's first round (2026-08-25)

Judges h/s/o, one item per call, median of three, never Fable. Seal: `sealed_predictions_r61.md`.
No item appears in MSc; two first drafts were discarded at seal time for being near-paraphrases of
existing examples.

## 9 of 9 exact. 26 of 27 judge-item cells exact. All five rules pass.

| id | item | h | s | o | median | predicted |
|---|---|---|---|---|---|---|
| M1 | eigenvalues of a 4 by 4 matrix | 0 | 0 | 0 | **0** | 0 ✓ |
| M2 | report a meter reading by phone | 1 | 1 | 1 | **1** | 1 ✓ |
| M4 | take a witness statement, following up on each detail | 2 | 2 | 2 | **2** | 2 ✓ |
| M5 | bring a worried neighbour to agree to a loft conversion | 3 | 3 | 3 | **3** | 3 ✓ |
| M6 | supplier wanting a three-year lock-in, would rather walk | 4 | 4 | 4 | **4** | 4 ✓ |
| M7 | three unions whose claims exceed the pot, each hearing the others' offers | 5 | 5 | 5 | **5** | 5 ✓ |
| M8 | brief eight team leads on a change that suits all of them | **3** | 1 | 1 | **1** | 1 ✓ |
| M10 | write a eulogy | 1 | 1 | 1 | **1** | 1 ✓ |
| M11 | from a transcript, was the buyer bluffing | 0 | 0 | 0 | **0** | 0 ✓ |

1. Ladder monotone and separating — **PASS**, one clean step per level, 0 through 5.
2. Party-count carve — **PASS** (M8 = 1). Both stronger judges cited the exclusion by name.
3. Expression carve — **PASS** (M10 = 1). Opus: the exclusion "bars raising the demand for
   expression quality, audience fit, or the stakes involved."
4. Understanding-not-steering carve — **PASS** (M11 = 0), cited verbatim.
5. 9 of 9 exact — **PASS**.

## The one disagreement is diagnostic

Haiku put the eight-team-lead briefing at **3**, reasoning that the leads "do not yet hold the view
the task requires". Sonnet and opus both read the phrase *"that suits all of them"* and applied the
number-of-parties exclusion. Haiku ignored the compatibility of the positions and counted heads,
which is precisely the failure mode M8 was built to detect. The text is not at fault; the weakest
judge is. Same pattern as r58, where haiku sat a level low across the PLs top band.

**Implication for the annotation run: a small model will misplace MSc's carves.** Median-of-three
absorbs it. A single-judge run with a small model will not.

## What this round does not establish

MSc now has a measured ladder and three working carves on its first attempt, which is a better
first round than PLe or PLs had. But **no human has labelled an MSc item.** Every number here is
model agreement with my construction, which is the same weakness the whole stream carries. A pass
means the text does what it says, not that what it says is right.
