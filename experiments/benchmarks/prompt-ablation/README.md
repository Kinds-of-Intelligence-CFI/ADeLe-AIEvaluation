# prompt-ablation: which prompt difference moves the v1 labels? (pre-registration, 2026-11-02)

**Why.** On the 60 battery items, the paper's prompt (B, `v1-published`) reads a little higher than our production
prompt (A, `v2-noreason`). B − A is +0.08 on average and up to +0.23 per rubric (`v1-prompt-bridge`). The two prompts
differ in four ways. This ablation changes them one at a time, from A to B:

| arm | run | builder | layout | reasoning | tie rule | length clause |
|---|---|---|---|---|---|---|
| A | `gate-v1-bridge-h` (exists) | `v2-noreason` | v2 tags | no | yes | yes |
| A′ | `abl-a2` | `v2-noreason` (repeat) | v2 tags | no | yes | yes |
| S1 | `abl-s1` | `v2-noreason-notie` | v2 tags | no | **no** | yes |
| S2 | `abl-s2` | `v2-noreason-notie-noclause` | v2 tags | no | no | **no** |
| S3 | `abl-s3` | `v1-layout-noreason` | **v1** | no | no | no |
| B | `gate-v1-bridge-pub` (exists) | `v1-published` | v1 | **yes** | no | no |

Each step's effect: tie rule = S1 − A, length clause = S2 − S1, layout = S3 − S2, reasoning = B − S3. Noise = A′ − A.

**Cells.** The 60 bridge items × 8 rubrics = 480 cells per new arm:
- the six that moved most from A to B: AS, KNc, MCt, MCu, QLq, CEc;
- two controls that didn't: KNa, CL.

Same judge for every arm: the API with the subagent harness, Opus 5.5 at effort low.

**Analysis.** For each step: the mean level change over the 480 cells, with a 95% bootstrap CI that resamples the 60
items. A step **moves the labels** if |mean change| ≥ 0.10, its CI excludes 0, and it beats noise: |change| > |A′ − A|
+ 0.05. Per-rubric changes are reported descriptively. If the effects are additive, the four steps sum to B − A
(about +0.10 on these rubrics); the gap shows the interaction.

**Cost:** about $23 from the December grant.

## Result (2026-11-02)

All four arms: 480 of 480 labelled by `claude-opus-5-5`. `analyse.py`, 60 items × 8 rubrics:

| step | mean change | 95% CI | cells changed (up / down) |
|---|---|---|---|
| noise (A′ − A) | +0.00 | [−0.02, +0.02] | 5% (2 / 2) |
| **tie rule** (S1 − A) | **+0.08** | [+0.06, +0.11] | 9% (9 / 1) |
| length clause (S2 − S1) | +0.01 | [−0.01, +0.03] | 6% (3 / 3) |
| layout (S3 − S2) | −0.02 | [−0.04, +0.01] | 8% (3 / 5) |
| **reasoning** (B − S3) | **+0.05** | [+0.03, +0.09] | 12% (9 / 4) |
| all (B − A) | +0.13 | [+0.09, +0.16] | 18% (15 / 3) |

**By the pre-set rule, no single step "moves the labels":** none reaches |0.10|.
- **Two steps have real, one-directional effects,** with CIs that exclude 0:
  - the **tie rule**, about two thirds of the A-to-B difference. It is largest on AS +0.17, MCu +0.13 and QLq +0.13.
  - **written reasoning**, the other third. It is largest on KNc +0.13 and MCt +0.10.
- **The length clause and the layout do nothing.**
- **The steps add up:** their sum is +0.124, against +0.125 for B − A, so there is no interaction.

**In context:** all prompt effects together are +0.13 on these rubrics. The gap with GPT-4o is −0.26 overall, and
−0.6 to −0.9 on KNa, KNc and CL, where the prompt does almost nothing. The prompt is a minor part; the model is the
major one.
