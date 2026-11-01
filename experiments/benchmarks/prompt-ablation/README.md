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
