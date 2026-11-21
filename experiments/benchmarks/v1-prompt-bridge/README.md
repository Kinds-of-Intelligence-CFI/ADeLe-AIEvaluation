# v1-prompt-bridge: why our v1 labels read lower than the published ones (pre-registration, 2026-11-02)

**Finding to explain.** `gate-v1-bridge` compared our judge with the published GPT-4o levels on 60 battery items
× 18 v1 rubrics. Eight rubrics were not comparable (within 1 < 0.85 or |shift| > 0.3): AS, AT, CL, KNa, KNc, KNf,
KNn and MCu. All eight read lower, by up to one level. That gate used:
1. the **plain API**, which reads PLp lower than the subagent judge (`GATE-API-BRIDGE.md`);
2. our **v2 bare-digit prompt**. It asks for the lower of two adjacent levels, and says to ignore how long or easy the
   work looks.

The published labels used another prompt: delean-batch-manager's, which has chain-of-thought and no tie rule. Our
repo's `v1` builder is not that prompt either: it gained a tie rule on 2026-07-26 (`fe3bae4`). The published prompt
is now builder `v1-published`, verbatim.

**Arms.** Both use the API with the subagent harness, Opus 5.5 at effort low, and the same 60 items and 18 rubrics.
- **A** (`gate-v1-bridge-h`): the v2 bare-digit prompt. This is today's production judge.
- **B** (`gate-v1-bridge-pub`): the published v1.0 prompt.

**Bar** (per rubric, against the GPT-4o levels, as in `PLAN.md` §3): **comparable** if within 1 ≥ 0.85 and
|shift| ≤ 0.3. Also reported: exact agreement and Spearman ρ. The "eight" are the rubrics not comparable in
`gate-v1-bridge`.

**Readings, fixed before any label:**
- **The plain API explains the gap** if A makes ≥ 6 of the eight comparable.
- **The prompt explains the gap** if B makes ≥ 6 of the eight comparable, and A makes ≤ 3.
- **The model explains the gap** if neither A nor B makes more than 3 of the eight comparable.
- **Mixed** otherwise.

**Then:**
- **Prompt:** Pablo decides between relabelling the v1 rubrics with `v1-published` (about 41,000 cells) and a
  per-rubric bridge to the v1 scale.
- **Plain API:** nothing changes, since all production labels are subagent or harness labels.
- **Model:** a small human check on MCu, KNc, KNa and CL.

**Cost:** about $13 per arm. Arm B writes chain-of-thought, so it has more output.

## Result (2026-11-02): the model explains the gap

Both arms: 1,080 of 1,080 labelled by `claude-opus-5-5` (`analyse_gates.py v1 <run>`).

| rubric | gate (plain API, v2) shift / within 1 | A (harness, v2) | B (harness, published v1) |
|---|---|---|---|
| AS | −0.33 / 0.88 | −0.25 / 0.90 ✓ | −0.02 / 0.92 ✓ |
| AT | −0.32 / 0.83 | −0.30 / 0.80 | −0.23 / 0.87 ✓ |
| CL | −0.78 / 0.70 | −0.60 / 0.77 | −0.57 / 0.73 |
| KNa | −0.95 / 0.70 | −0.88 / 0.70 | −0.88 / 0.72 |
| KNc | −1.00 / 0.62 | −0.92 / 0.65 | −0.72 / 0.73 |
| KNf | −0.38 / 0.85 | −0.32 / 0.88 | −0.32 / 0.87 |
| KNn | −0.32 / 0.92 | −0.28 / 0.93 ✓ | −0.22 / 0.95 ✓ |
| MCu | −0.75 / 0.67 | −0.45 / 0.87 | −0.32 / 0.80 |

(✓ = comparable.) Of the eight, A makes 2 comparable and B makes 3. **Reading: the model explains the gap.**
- **The published prompt helps** on AS and MCu.
- **The core shifts stay under either prompt:** KNa, KNc, CL, KNf.
- **MCr now reads higher** than GPT-4o: +0.35 in A, +0.43 in B. It is not comparable in either arm.

**Rank agreement** with GPT-4o stays modest for AT, KNc and MCu (ρ 0.31–0.43). **Next, per the rule:** a small human
check on MCu, KNc, KNa and CL, to see which judge humans side with. No relabel.

## Why Opus reads differently (exploratory, 2026-11-02)

Production judge (arm A) against GPT-4o over all 18 rubrics: **57% exact, 88% within 1**.

**Opus's written reasoning (arm B) on the cells 2+ levels below GPT-4o** shows one pattern per rubric:
- **KNa:** Opus files chemistry, meteoritics and similar under the natural sciences, and gives applied sciences 0.
  GPT-4o gave up to 5 on the same items.
- **KNc:** everyday framing a solution does not need ("could be worded with any substances") scores 0–1.
- **CL:** applying known procedures or templates (IUPAC naming, retrosynthesis, deduction) scores 1–2. Higher levels
  are kept for forming new concepts.
- **MCu:** low unless the task makes the solver weigh their own uncertainty. A clear-cut answer, or no confidence
  asked for, scores 1–2.

**Inter-rubric correlations** (`inter_rubric.py`, 2026-11-02). This repeats the paper's Figure 4 analysis: the
Spearman matrix of levels over every rubric pair. Figure: `inter_rubric.png`. Numbers: `inter_rubric.json`.
- **Reproduction.** GPT-4o on the full battery (16,108 items) gives the paper's picture. The pairs above 0.8 are
  CL–MCt 0.83, CL–QLl 0.82 and MCt–QLl 0.81. The paper reports two above 0.8, both on CL; the third pair is 0.81.
- **The 60 items stand in well.** GPT-4o's 60-item matrix tracks its full-battery matrix (r = 0.94).
- **CEe is dropped** for every judge. Opus A gives it 0 on all 60 items, so its correlations are undefined.

| judge (60 items, 17 rubrics) | mean ρ | mean \|ρ\| | first-eigenvector share | reasoning block | AS, CEc, AT, VO × block |
|---|---|---|---|---|---|
| GPT-4o | +0.26 | 0.34 | 0.41 | 0.82 | 0.59 |
| Opus A | +0.09 | 0.26 | 0.26 | 0.58 | 0.32 |
| Opus B | +0.10 | 0.26 | 0.27 | 0.63 | 0.31 |

Reasoning block = CL, MCr, MCt, MCu, QLl (mean ρ within it). GPT-4o minus Opus A, bootstrap over items (95%): mean
ρ +0.17 [0.12, 0.21]; mean |ρ| +0.08 [0.03, 0.12]; first-eigenvector share +0.15 [0.07, 0.19]. Arm B is the same.

- **Same structure, weaker.** The two matrices correlate at r ≈ 0.8. GPT-4o's ρ is higher on 110 of 136 pairs.
- **Where they differ.** For GPT-4o, AS, CEc, AT and VO rise with the reasoning block. For Opus they mostly do not.
- **Not the spread.** Opus's levels spread less on every rubric. Squeezing GPT-4o's levels into Opus's per-rubric
  distribution, keeping its item order, leaves mean ρ at +0.24 and the eigenvector share at 0.36–0.37.
- **Knowledge double-counting** (separate count): items with 2+ knowledge rubrics at ≥ 2 are 68% for GPT-4o,
  20% for Opus A and 27% for Opus B.

**Reading.** GPT-4o's levels share more of a common factor, mostly through attention, comprehension, atypicality and
volume moving with reasoning. Two explanations fit:
1. GPT-4o has a halo: one overall-difficulty impression leaks into several rubrics.
2. Opus under-links demands that really do go together.

The paper itself says such correlations depend on which benchmarks are chosen. Two cautions: the data cannot tell
the two explanations apart, and lower reliability would also weaken correlations (we know Opus's test-retest, 0.93–0.95
exact, but not GPT-4o's). Only 60 items. The human check on MCu, KNc, KNa and CL decides.

## rWG: does the paper's agreement index tell judges apart? (exploratory, 2026-11-02)

The paper validated GPT-4o with rWG (Table 7): Delphi consensus vs GPT-4o 0.86, humans among themselves 0.83. Opus vs
GPT-4o on our 60 items and 18 rubrics is also 0.86. To see whether that means anything, we ran Sonnet 5.5 low and Haiku
5.5 low (`rwg-sonnet-low`, `rwg-haiku-low`, API with the subagent harness, ~$4) on the 8 rubrics of `abl-s3`, with the
same prompt as Opus (`v1-layout-noreason`). Script `rwg.py`, numbers `rwg.json`.

| judge (60 items, 8 rubrics) | labelled | rWG | exact | within 1 | shift vs GPT-4o |
|---|---|---|---|---|---|
| Opus 5.5 low (`abl-s3`) | 480 | 0.82 | 0.47 | 0.86 | −0.34 |
| Sonnet 5.5 low | 480 | 0.81 | 0.47 | 0.83 | −0.35 |
| Haiku 5.5 low | 452* | 0.79 | 0.46 | 0.77 | −0.50 |

\* 28 cells unparsed after one retry (Haiku re-calls Read, as in judge-choice).

- **rWG does not tell the judges apart.** The three differ by at most 0.03. So Opus matching the human level (0.86)
  is weak evidence: Sonnet and Haiku would likely match it too.
- **All three Claude models read lower than GPT-4o.** The downward shift is not specific to Opus.
- Per rubric, no judge wins everywhere. Sonnet is closest to GPT-4o on KNa and KNc; Opus on CL and MCu.
- Telling judges apart needs other evidence: human labels with exact agreement and shift (the paper's Delphi labels
  are not public), or validity checks such as judge-choice's.
