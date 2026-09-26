# Round 75 — MSc voice-pass regression (2026-08-26)

Seal: `sealed_predictions_r75.md` (sha256 135294dc, written before judging). Text under test:
src/.../MSc.txt at 88a071a (post 2026-08-25 voice pass). Judges h/s/o, one item per call,
median of three, never Fable. Mechanical 4-gram independence check vs every MSc example
bullet: 0 hits on 9 items. Items are RECONSTRUCTIONS of the r61 designs (r61's full item
texts were never persisted — see the seal's honesty note).

## PASS: 9 of 9 medians equal the r61 medians. 26 of 27 cells exact.

| id | item | h | s | o | median | r61 median |
|---|---|---|---|---|---|---|
| R1 | eigenvalues | 0 | 0 | 0 | **0** | 0 ✓ |
| R2 | meter reading by phone | 1 | 1 | 1 | **1** | 1 ✓ |
| R3 | witness statement | 2 | 2 | 2 | **2** | 2 ✓ |
| R4 | loft conversion neighbour | 3 | 3 | 3 | **3** | 3 ✓ |
| R5 | supplier lock-in | 4 | 4 | 4 | **4** | 4 ✓ |
| R6 | three unions, one pot | 5 | 5 | 5 | **5** | 5 ✓ |
| R7 | brief eight team leads | **3** | 1 | 1 | **1** | 1 ✓ |
| R8 | eulogy | 1 | 1 | 1 | **1** | 1 ✓ |
| R9 | transcript bluff | 0 | 0 | 0 | **0** | 0 ✓ |

## The one deviant cell replicates r61 exactly

Haiku put the eight-team-lead briefing at 3 by the same route as in r61: it read "do not yet
hold the view" and counted heads past the compatibility condition. Sonnet and opus both cited
the anti-count carve ("the number of people addressed do[es] not by itself raise the demand")
and the one-way-message clause. Same failure, same judge, same item design, absorbed by the
median both times. This is judge-capability, not text.

## Carves under the new text, all confirmed by citation

Expression carve (R8): opus quoted the vocabulary/genre/register exclusion verbatim.
Understanding-not-steering carve (R9): all three judges quoted "raises this demand only
insofar as what is inferred must shape what is said next". Anti-count carve (R7): cited by
both stronger judges. The r70 underspecification note on the briefing item also replicates:
judges read it as one-way (1), Pablo read it as fielding responses (2) — both
rubric-consistent, neither near 3.

## Conclusion

The 2026-08-25 voice pass changed no measured behaviour. The "NO OPERATIVE CLAUSE CHANGED"
claim is now measured rather than asserted. MSc's remaining gap is desideratum 9 only.

## Protocol lesson

r61 persisted only its results table; its seal and item texts are gone. From r75 on, the seal
file carries full item texts (done here). Judges ran as fresh single-item subagent calls
(current h/s/o tier) with the meta line stripped and examples kept.
