# Pablo's blind PLp labels on Terminal-Bench 4.0.0 — results (2026-09-28)

**Question** (`SEAL-plp-tb4.md`). Is PLp's Level 3/4 boundary too strict for Terminal-Bench tasks?

**Answer.** No. Of the five judge-3 tasks Pablo labelled, he put none at 4 (k = 0), so by the
seal's rule the boundary stands. The disagreement runs the other way:
- he put three of the five at Level 2, which triggers the seal's 2/3 flag;
- after unblinding, Claude's reading agrees with his on all three;
- exact agreement with the judge is 3 of 6 labelled tasks, and within one level 6 of 6.

**Deviation.** The round ended after 7 of the 12 sealed tasks. After seven labels Pablo reported low
confidence, and he chose to compare his answers against the rubric and the judge. The checklist
re-check of amendment 1 was therefore not carried out. The decision rule is read on 5 of the 10
sealed judge-3 tasks. On `cad-model`, Pablo abstained: the schematic the task depends on is not in
its text.

| # | task | Pablo, blind | judge | Claude, after unblinding | Claude's reason (confidence) |
|---|---|---|---|---|---|
| 1 | html-js-filter | 2 | 3 | 2 | The one real choice, a real HTML parser plus removing dangerous elements, attributes and URL schemes, has a standard answer, and the task allows parser normalisation. The other steps do not constrain one another. (0.65) |
| 2 | ctr-optimization | 3 | 3 | 3 | An experiment budget and a hard deadline couple the probe schedule and the final commit. (0.8) |
| 3 | cad-model | abstained | 2 | abstain | The text leaves the demand undetermined. The judge's 2 is a default for the task class. |
| 4 | biped-contact-dynamics | 4 | 4 | 3 | Established methods (trajectory optimisation over contact modes) supply the outline. The judge placed it between 3 and 4 and went up, against the tie-break. (0.6) |
| 5 | layout-config-recreation | 2 | 3 | 2 | Layer order and fonts are read off the target, not chosen by look-ahead. The coupling the judge cites is shared pixel accuracy, which is perception and execution. (0.6) |
| 6 | photonic-waveguide-routing | 3 | 3 | 3 | Net order and the corridors each net claims interact. Standard routing methods supply the outline. (0.8) |
| 7 | risk-scorer-replay | 2 | 3 | 2 | Probing the black box is finding things out, and the judge's own reasoning says so. The fixes are largely independent. (0.65) |

**Sealed predictions.**
- k ≤ 1 (0.7): held.
- Exact agreement on at least 9 of 12 (0.6): failed in effect. The count stood at 3 of 6, so all
  six remaining tasks would have had to match.

**Descriptive only, as sealed** (n = 6 or 7).
- PLp against solve rate: Pablo +0.28, judge −0.27, Claude +0.29.
- PLp against expert hours: Pablo +0.55, judge +0.48, Claude +0.40.

**What it means.**
- The 3/4 boundary is not the problem on this evidence. If anything, the judge over-applies
  Level 3: three times it counted as interacting decisions what the rubric excludes (perception,
  investigating a black box, a one-off method choice with a standard answer). On one task it went
  up despite the tie-break.
- PLp as written does not track Terminal-Bench difficulty here either. Two of the hardest tasks
  (solve rates 0.13 and 0.23) are Level 2 on both Pablo's and Claude's reading. This supports the
  view that Terminal-Bench's difficulty lies outside planning.
- Human–judge exact agreement on real Terminal-Bench instructions (3 of 6) is far below the lab's
  PLp anchor on designed items (94% exact). That is evidence under desideratum 5: the rubric is
  harder to apply to real agentic tasks from their instructions alone.
- Claude's reading is one more annotator from the judge's model family, not ground truth.

**Follow-up at max effort** (`../RESULTS.md`, run `tb4pl-max`):
- Opus at max effort keeps the three disputed tasks at 3 and moves `biped-contact-dynamics` to 3.
- The 2/3 disagreement is a reading of the gate, not an effort artifact.
- Claude revises its own reading: `html-js-filter` and `layout-config-recreation` are borderline
  at 2/3, and `risk-scorer-replay` is still more likely 2.

Files: `pablo_plp.csv` (blind labels as given), `unblinded.csv` (with judge and Claude columns).
