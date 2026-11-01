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
