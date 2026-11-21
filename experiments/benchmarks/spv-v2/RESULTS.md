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

## Phase B: real images (run `spv2-b`, 2026-10-05) — FAIL on one rule (B4), kill rule passes

Pre-registration: `phaseB/PREREGISTRATION_B.md` (commit 23712f8). There were 391 calls. All 391 were answered and
parsed and all were written by `claude-opus-5-5`. There were no classifier stops. A one-cell smoke test confirmed the
image judge loads the image. Analysis: `analysis/analyse_b.py`.

**The candidate tracks severity on images; the current text does not.**

| | pooled ρ | size | contrast | blur | noise | occlusion | overlay |
|---|---|---|---|---|---|---|---|
| current | +0.36 | flat (all 1) | flat (all 1) | +0.73 | +0.71 | +0.71 | +0.71 |
| candidate | **+0.79** | +0.87 | +0.85 | +0.88 | +0.87 | +0.71 | +0.87 |
| candidate + answer key | +0.81 | +0.87 | +0.85 | +0.89 | +0.91 | +0.71 | +0.85 |

Under the current text, every size and contrast stimulus scores 1. That includes 6-pixel glyphs and ink at grey 240
on white, which is barely visible. This is the fineness carve on real images.

Candidate medians, step 0→4 (both codes agree unless shown):

| sweep | step 0 | step 1 | step 2 | step 3 | step 4 |
|---|---|---|---|---|---|
| size | 1 | 1 | 1 | 2 | 2 |
| contrast | 1 | 1 | 1 | 2 | 2 |
| blur | 1 | 1 | 1 | 2 | 3 |
| noise | 1 | 1 | 3 | 3 | 3 |
| occlusion | 1 | 3 | 3 | 3 | 3 |
| overlay | 1 | 1 | 2 | 2 | 2 |

Views were 4 on both codes. All four traps were 1 (search, counting, ARC-like grid, rotation). P-meter was 333.

| rule | result |
|---|---|
| B1 pooled ρ ≥ 0.6 (kill rule) | holds, +0.79 |
| B2 each sweep ρ ≥ 0.5 | holds, +0.85 to +0.88 |
| B3 occlusion | holds |
| B4 overlay: steps 1–4 at 2 or 3 | **fails**: step 1 is 1 on both codes (all four labels) |
| B5 views at 4 | holds |
| B6 traps ≤ 1 | holds |
| B7 meter example at 3 | holds, 333 |

**The B4 failure: as registered, phase B fails.** The cause is my stimulus prediction, not the text.
- At step 1 (60 strokes), most strokes fall in the empty margin. A few thin lines cross the thick glyphs.
- Every answer says the code still reads at a glance and cites Level 1's note that a busy image stays at 1 while the
  content is plain. That is the rubric doing what it says.
- Steps 2–4 are 2, as intended.
- So I make no change to the text. The rule was miscalibrated at its lightest step. I record this as a failed
  pre-registered rule rather than re-scoring it.

**Answer key.** Key and no-key medians agree on 58 of the 62 stimuli that have both arms (94%). The key arm is higher
on 1 and lower on 3. The differences are at single middle steps (noise steps 1–2, overlay step 2). The judge reads the codes itself; on
synthetic stimuli the key adds almost nothing. **For ZeroBench I use no key.** That matches the evidence and keeps
answers out of prompts.

**Sealed predictions.**
- B1 (0.7): held. Current text ρ lower (0.8): held. Current size ρ below 0.3 (0.6): held, flat.
- Current blur reaches 3 by step 2 (0.6): failed; it reached 3 only at step 4.
- Key agreement ≥ 80% (0.65): held (94%). Key higher on the hardest steps (0.6): failed; the key was mostly lower, at middle steps.
- B2 (0.55), B3 (0.75), B5 (0.75), B6 (0.85), B7 (0.8): held. B4 (0.6): failed.
- Candidate passes (0.4): failed, on B4.
- Per-step medians: the candidate is more conservative than I predicted. Size and contrast reach 2 one step later,
  and noise reaches 3 one step earlier.
