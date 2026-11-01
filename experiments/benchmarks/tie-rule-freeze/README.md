# tie-rule-freeze: would dropping the tie rule unfreeze any rubric? (pre-registration, 2026-11-02)

**Why.** The production prompt says "If the task genuinely fits two adjacent levels, choose the lower one". The
published v1.0 prompt has no such rule. In `prompt-ablation`, the rule lowered v1 levels by 0.08 without changing
their order. Pablo would like the prompt as close to the original as possible, but only if dropping the rule leaves
the freeze decisions standing. This study re-runs, without the rule, every test that PLp, PLe, PLs, MSc v4b and the
MSm candidate were frozen on.

**Judge.** Builder `v2-noreason-notie`: the production prompt minus that one sentence. It runs through the API with
the subagent harness (`harness-emulation`), Opus 5.5 at effort low, bare digit. Inputs, rubric texts, items and
repeats are those of the original tests. The "tie" labels are the originals.

## Tests and pass rules (copied from the freeze decisions)

**PL** (goal-visible amendment, `97cda10`), run `notie-pl-goal`. PL on the 787 coding and terminal tasks, regular
and long inputs together:
- **PL1** every PL cell labelled, or each gap explained;
- **PL2** PLp's link with solve rate on SWE-bench Verified is negative, p < 0.05;
- **PL3** no PL rubric has a significant link in the wrong direction (p < 0.05) on any of the six sets.

**MSc v4b and the MSm candidate** (ms-candidate amendments 6 and 7, bare digit, three repeats, label = lower
median). Run `mscand-nt`, the lab prompts of `mscand-nr-v4b` (MSc) and `mscand-nr` (MSm, arm `msm_cand_nr`).
These are rebuilt by the study's scripts at the commits that made them, and each is checked against its recorded
sha256 before the rule sentence is removed.
- **R** every MSc and MSm lab check that holds with the tie rule still holds. A loss is confirmed only if a
  three-repeat re-judge of the failing items (pass 2) fails again, as in the original protocol.
- **M** the refusal rule (amendment 3) holds for MSc.
- **H1** exact agreement with Pablo's 15 agent-side tau2 labels (set H, full input) is ≥ 12. With the rule it is 13.
- **H2** no item lands 2+ levels from Pablo's label where the tie version was within one.

**MSc criterion** (tau2-goal), run `notie-msc-tau2`. MSc on the 242 tau2 tasks:
- **T1** MSc's link with solve rate (within domain, pooled as in tau2-goal) stays negative, p < 0.05. With the
  rule it is −0.27.

## Verdict

- **A rubric stays frozen without the rule** if every rule above that applies to it holds.
- **Any rule that fails** goes to Pablo before anything changes.

**Also reported:**
- the mean shift and exact agreement, notie against tie, per rubric and set;
- agreement with Pablo's manual labels: set H, his 7 Terminal-Bench PLp labels and his 7 battery MSc labels.

**Cost:** about $55 from the December API grant.

## Result (2026-11-02): every rubric stays frozen without the tie rule

All labels by `claude-opus-5-5` (`analyse.py`, `results.json`).

**PL** (`notie-pl-goal`, 2,359 of 2,361):
- **PL1 holds.** The 2 gaps are TB-Science `protein-active-learning` (PLe, PLs), refused as in the original run.
- **PL2 holds.** SWE-bench Verified PLp ρ = **−0.60** (p ≈ 1e-44); with the rule it was −0.59.
- **PL3 holds.** No PL rubric has a significant wrong-direction link. TB 4.0 PLp drifts to +0.23 (p 0.19, not
  significant), against +0.00 with the rule.
- **Other links barely move:** ProgramBench PLp −0.44 (rule: −0.47), SWE PLe −0.28 (−0.31), DeepSWE PLp −0.19 (−0.17).
- **Shift against the rule:** PLp +0.08 (88% identical), PLs +0.08 (89%), PLe +0.03 (93%).
- **Pablo's TB PLp labels** (6 tasks shared): exact 3 → 2, within one 6 → 6.

**MSc v4b and the MSm candidate** (lab, 260 items × 3):
- **R holds for both:** no lab check lost. MSc is 97% identical to the rule version (shift +0.01); MSm 88% (+0.08).
- **M holds:** refusal pairs B ≤ 3 on 4 of 5, as with the rule. The supplier and builder pairs are still at 4.
- **H1 holds:** 14 of 15 exact against Pablo (13 with the rule). H-08 moves from 2 to his 3.
- **H2 holds:** no new 2+ miss.

**MSc criterion** (`notie-msc-tau2`, 242 of 242):
- **T1 holds:** ρ = **−0.19** (p 0.004). This is weaker than with the rule (−0.27, p 3e-5).
- **Pablo's set H on the real tau2 input:** 14 of 15 (13 with the rule).
- **Shift:** +0.06, 85% identical.

**Verdict:** PL, MSc and MSm all stay frozen without the tie rule. Agreement with Pablo's labels improves on MSc
(13 → 14 of 15) and slips by one item on TB PLp. **Two links weaken but stay inside the bar:** the MSc–tau2 link
(−0.27 → −0.19) and TB 4.0 PLp (+0.00 → +0.23, not significant).
