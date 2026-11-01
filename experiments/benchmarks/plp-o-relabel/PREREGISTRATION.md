# plp-o-relabel — pre-registration

Committed and pushed before any label of this study. Pablo adopted PLp text O on 2026-10-01 (`92f28fc`; see
`../plp-b2/RESULTS.md` and `docs/rubric-provenance/PLp.md`) and asked for the real-task relabel.

**Question.** With O, does PLp keep (or strengthen) its links to difficulty on SWE-bench Verified, tau2 and
Terminal-Bench 4.0.0?

## Design

- **Only the rubric changes.** Same judge (Opus low via `adele-judge-v2-low`, relayed by `judge-dispatcher-v2-low`,
  one call per cell), same v2 prompt, same task texts as `pl-relabel-v2`. `make_prompts.py` rebuilt every
  `pl-relabel-v2` PLp prompt from the previous text (`062c5af`) and matched its stored hash, then built the O prompt.
- **Runs.** `o-swe` (398 tasks), `o-tau2` (232), `o-tb4` (66): 696 calls. The 44 SWE gate tasks reuse `plp-b2`'s
  `o-swe-gate` (same text, prompt and judge; prompts checked identical).
- **Writers.** Answers by another model are set aside and the cell is judged once more; if that fails too, the cell
  has no label (as before; `uefi-bootkit` is expected to fail).
- **Analysis** (`analysis/analyse.py`). The studies' own pre-registered functions (`swebench-pl` questions on the
  435 solvable tasks; `tau2-tb4-pl` analyse on tau2 and Terminal-Bench), with PLp from O and PLe/PLs from
  `pl-relabel-v2` (unchanged rubrics). `pl-relabel-v2`'s results sit beside them, with O-against-current agreement
  and PLp level counts. Tested by feeding the current labels in as O: both reproduce `pl-relabel-v2` exactly.

This is a re-measurement of an adopted text, not a test with a pass mark.

## Predictions (sealed)

Current-text values (`pl-relabel-v2`) in brackets.
- SWE-bench, PLp against solve rate negative with p < 0.05 (−0.58): 0.97. More negative than −0.58: 0.55. Within
  ±0.10 of it: 0.7.
- SWE-bench, PLp against time to fix stays positive with p < 0.05 (+0.48): 0.95.
- tau2, PLp against solve rate within domain negative with p < 0.05 (−0.38): 0.85. More negative than −0.38: 0.45.
- Terminal-Bench, PLp against solve rate not significant (+0.25, ns): 0.75. Negative: 0.4.
- O against current PLp labels, exact agreement: SWE ≥ 0.75: 0.6; tau2 ≥ 0.7: 0.55. Mean shift on SWE within ±0.15: 0.7.
- More Terminal-Bench tasks at Level 4 or above under O than under the current text: 0.5.

## Cost

696 Opus-low calls, about 4 weekly points (now 37%) and about 28% of a 5-hour window (now 50%), in relays of about
100 cells, at most four at once.
