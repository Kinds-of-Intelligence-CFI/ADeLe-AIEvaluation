# r75 sealed — MSc voice-pass regression (2026-08-26)

Text under test: src/adele/rubrics/data_v2/Paolo_Pablo/MSc.txt as committed at 88a071a
(v2-draft, 2026-08-25 v1-voice pass). The pass is recorded as NO OPERATIVE CLAUSE CHANGED
but has never been measured. This round measures it.

## Honesty note on the items

r61's full item texts were not persisted (RESULTS-r61.md carries only one-line descriptions;
its seal file is missing). The nine items below are RECONSTRUCTIONS from those descriptions
and from the r61/r70 records of what each item was built to test. This is therefore a fresh
measurement of the r61 design under the current text, not a byte-identical regression.
Protocol lesson to record: round records must persist full item texts.

## Items and predictions (= the r61 medians)

| id | item | predicted median | tests |
|---|---|---|---|
| R1 | eigenvalues | 0 | L0: no stance to move |
| R2 | meter reading by phone | 1 | L1: scripted exchange |
| R3 | witness statement | 2 | L2: cooperative, turn-by-turn |
| R4 | loft conversion neighbour | 3 | L3: open stance won through doubts |
| R5 | supplier three-year lock-in | 4 | L4: contested, single counterpart |
| R6 | three unions, one pot | 5 | L5: incompatible positions, cross-reading |
| R7 | brief eight team leads, change suits all | 1 | anti-count carve |
| R8 | write a eulogy | 1 | expression carve (one-way message) |
| R9 | transcript: was the buyer bluffing | 0 | understanding-not-steering carve |

## Item texts

R1: Compute the eigenvalues of a given 4 by 4 matrix, showing your working.

R2: Phone the electricity company and report the meter reading shown on your meter,
answering the operator's standard questions.

R3: Take a witness statement from a cooperative bystander who saw a road accident,
following up on each detail they mention until the account is complete.

R4: Bring a worried neighbour to agree to your planned loft conversion. They do not
oppose it on principle and would be content to be persuaded, but they raise concerns
about noise, light and the party wall one after another, and each must be answered
before they will agree.

R5: Get a supplier to sign a one-year contract when they are pressing for a three-year
lock-in and would rather let the deal fall through than give it up unprompted.

R6: Chair the annual pay round with three unions whose combined claims exceed the
available pot. Each union learns what the others are offered, any concession made to
one is read by the other two, and a settlement must be reached with all three.

R7: Brief eight team leads on a schedule change that suits all of them.

R8: Write a eulogy for a family friend, to be delivered at their funeral.

R9: From the transcript of a completed negotiation, determine whether the buyer was
bluffing when they claimed to have another offer.

## Pre-registered decision rule

1. PASS = all nine medians equal the r61 medians. Any deviation is measured drift from
   the voice pass and is REPORTED, not edited (stopping rule; flip-significant cases go
   to Pablo per the standing rule).
2. Judges h/s/o, one item per call, never Fable, median of three. Haiku deviation on R7
   absorbed by the median is expected (r61 precedent) and does not fail the round.
3. Mechanical 4-gram independence check of every item against every MSc example bullet,
   run before judging; any hit ≥ one shared 4-gram voids the item.
4. Rubric shown meta-stripped (no #! line), examples kept.
