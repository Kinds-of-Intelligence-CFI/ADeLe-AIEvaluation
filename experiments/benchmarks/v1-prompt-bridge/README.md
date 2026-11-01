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
