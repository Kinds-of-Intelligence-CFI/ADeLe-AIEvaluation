# spv-v2 — results

## Phase A: text-only lab regression (run `spv2-1`, 2026-10-05) — PASS

Pre-registration: `PREREGISTRATION.md` (commit dd7148a). There were 222 calls. All 222 were answered and parsed and
all were written by `claude-opus-5-5`. There were no classifier stops and no pass 2 was needed.
Analysis: `analysis/analyse.py`.

| rule | result |
|---|---|
| 1. Placement: ≥19 of 22 exact, none off by two | 21/22 exact, all within one |
| 2. Ladder and carves: ≥13 of 16 at prediction, none off by two, carves bind | 15/16, none off by two, all six carves bind |
| 3. Fineness items at 2 | 4/4 |
| 4. Pairs hold | 5/5 |

**The current text fails on size.** Under the current text, small-but-sharp content reads as Level 1 on every
label: L-V2s gets 111 and M1b gets 111, so pair M1 fails. The candidate puts both at 2 (222). This is the carve the
audit named.

**Faint content was already Level 2 under the current text.** L-V2f got 221 and M3b got 222. I had predicted 1. So
the current text's carve bit on size but not on contrast.

**The two misses are both item problems, not rubric problems.**
- **L-V0** ("a table gives the monthly rainfall") got 011 under the candidate, against 000 under the current text.
  All three answers say the task does not state whether the table is text or an image. The item is underspecified.
  The candidate's chart and screenshot examples make an image reading more likely. Recorded; no change to Level 0.
- **M2a** (soft blur, every digit distinct) got 111 under both texts. I had predicted 2. The answers say nothing is
  lost and nothing needs bringing out, so it reads at a glance. That is the rubric working; the prediction was wrong.
  The pair still holds (M2b = 333).

**Placement miss.** The cracked-meter example (Level 3) placed at 2 (322). The answers read cracks as lines laid over
whole digits, which is Level 2. That is a fair reading. The example was replaced after the run with a splash of paint
covering the lower half of two digits. The new bullet is re-placed in phase B.

**Sealed predictions.**
- Placement ≥19 exact (0.6): held. None off by two (0.8): held.
- Ladder ≥13 (0.75): held. L-V5 at 5 (0.6): held. Carves bind (0.85): held.
- All four fineness items at 2 (0.5): held.
- Current text, size items at 1 (0.6 each): held.
- All five pairs hold under the candidate (0.35): held.
- Current text: M1 fails (0.55) held; M3 fails (0.55) did not; M2 fails (0.4) did not.
- Candidate passes (0.45): held.

Answers cite an example or a Note on 177 of 222 calls.

**What this does not show.** Phase A is text descriptions written by me. It shows the candidate is self-consistent and
fixes the size carve. It says nothing yet about real images. That is phase B.
