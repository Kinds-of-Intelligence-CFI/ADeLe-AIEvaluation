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
