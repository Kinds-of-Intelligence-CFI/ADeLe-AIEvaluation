# Seal — Pablo's blind PLp labels on Terminal-Bench 4.0.0 (2026-09-28)

Written and committed before the first label. Pablo should not read this file until his last label.

**Question.** Is PLp's Level 3/4 boundary too strict for Terminal-Bench tasks? The judge (Opus 5.5,
low effort, run `tb4pl-r1`) put 26 of the 33 analysis-set tasks at Level 3. Its reasoning applies the
boundary as written: recognising the task type supplies the outline of a plan, so the task is Level 3.

**Frame and draw.**
- Frame: the Terminal-Bench analysis-set tasks with a registered PLp label.
- Excluded: tasks whose judge label was stated in chat before this round (`retro-console-soc`,
  `kv-live-surgery`, `heat-pump-warranty`, `coq-block-bound`, `formal-crypto`, `gsea-proteomics`)
  and `uefi-bootkit`, which has no registered label. That leaves 28 tasks: 3 at Level 2, 24 at 3,
  1 at 4.
- Drawn with `numpy.random.default_rng(20260928)`: 10 of the 24 at Level 3, 1 of the 3 at Level 2,
  and the one at Level 4. The presentation order was also drawn with that generator.

Order: 1. `html-js-filter`, 2. `ctr-optimization`, 3. `cad-model`, 4. `biped-contact-dynamics`, 5. `layout-config-recreation`, 6. `photonic-waveguide-routing`, 7. `risk-scorer-replay`, 8. `sound-change-cascade`, 9. `pretrain-shard-corruption`, 10. `satb-audio-transcription`, 11. `payments-pipeline-fix`, 12. `mp-checkpoint-consolidation`.

**Procedure.**
- Pablo sees each task's judged text: `instruction.md` without its canary comment lines, exactly as
  in the judges' prompts.
- He applies `src/adele/rubrics/data_v2/Paolo_Pablo/PLp.txt` (sha256 de98ab35d80c7984…)
  under the judges' instruction: an integer from 0 to 5, and when in doubt between two adjacent
  levels, the lower one unless the higher level's requirement is clearly met.
- One task at a time. Each label is written to `pablo_plp.csv` before the next task is shown.
- The judge's labels, solve rates, expert-time estimates and Epoch flags are not shown until all 12
  are labelled. The judge's labels are fixed in the committed `labels/tb4pl-r1/labels_long.csv`.

**Decision rule.** Let k be the number of the 10 judge-3 tasks that Pablo places at Level 4 or 5.
- k ≥ 3: the boundary is too strict for tasks of this kind. Claude drafts an edit with its own
  decidable test, and it goes through the lab's regressions. No label of this study changes.
- k ≤ 1: the boundary stands. Pending the incremental test, Terminal-Bench's difficulty is taken to
  lie outside planning.
- k = 2: inconclusive, decided on Pablo's stated reasons.

**Also reported.**
- Exact and within-one agreement on all 12, against the lab's PLp human anchor (94% exact).
- Pablo's levels against solve rate, descriptive only (n = 12).
- A flag on the 2/3 boundary if he puts 3 or more judge-3 tasks at Level 2.

**Claude's sealed prediction.**
- k ≤ 1, probability 0.7.
- Exact agreement on at least 9 of 12, probability 0.6.

**Blinding caveat.** The judge labels of the other tasks appeared once in this session, inside a
tool output (a 150-row CSV of hashes) that was not stated in chat.
