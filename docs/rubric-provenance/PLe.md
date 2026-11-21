# PLe — provenance and change record

Moved out of the rubric's `#!` line on 2026-08-25. Rounds are in `labs/rubric-qa`.

- ADeLe v2 (agentic) — v2-r44 voiced and styled to v1 (subject 'The task', guards marked Critically/Importantly/Note, no em-dashes or semicolons; no operative clause changed)
- ADOPTED r44 (labs/rubric-qa/r39, r44)
- version: v2-r44
- source: Paolo_Pablo
- revised: 2026-08-22
- driver re-anchored to the availability and difficulty of progress/correctness checking; irreversibility and impact of failure removed as placement keys (v1 comparability: tasks formerly at L5 through irreversibility alone now score by their checking structure)
- 2026-08-25 example pass: v1 carries concrete detail in about 45 per cent of its examples at a flat rate across all six levels, and the PL family did not, so quantities that decide an example were filled in. A benchmark-shaped Level 2 example was added carrying Pablo's own tau-bench labels. No cross-references or rationale glosses were present in this file. No operative clause changed.


## Appended 2026-08-26: tau anchor re-key sheet, and a conflict it exposed

The r39 recommendation to re-anchor tau-* from Pablo's 2s to 1 is executed as a proposal in
labs/rubric-qa/anchors-PLe-tau-rekey.md (two items measured at 1 in r39, three extrapolated;
historical r38 sheet untouched; all deltas within-1, no past gate flips). Preparing it exposed
a conflict: the Level 2 tool-interface example added in the 2026-08-25 example pass encodes the
OLD tau reading (per-call success reports placed at L2), which the adopted L1 clause reads as
forced per-action checking. Example and re-key cannot both stand; the options are in the sheet.
Awaiting Pablo on both.


## Appended 2026-08-26: v2-r45 — conflict resolved by option (a), measured (r76)

Pablo delegated the resolution. The tool-interface example moved L2 → L1 verbatim; no other
clause changed; meta line reduced to the minimal judge-safe style. Basis: r39's tau medians of 1
under the forced-per-action clause. r76 measured the move: tau items 1, the forced arm of the
commissioning minimal pair HELD at 2 unanimously, the elected arm at 3 — the example move did not
drag juncture-checking into L1. The tau re-key sheet is adopted; the five tau-* PLe anchors are 1.
r76's own caveats (tau cells corroborative rather than independent; 4-gram check run post-hoc,
one against-prediction hit on T4) are in RESULTS-r76.md.

## 2026-10-04 — examples review

Example bullets only; no level statement, Note or scope text changed. Reviewed against the rubric's own clauses and the
desiderata (`experiments/benchmarks/examples-review/PLe/REVIEW.md`); each new or reworded bullet was placement-checked
with itself removed from the rubric (run `exrev-1`; all within one level of target). Adopted under Pablo's standing
approval for example-only changes. Flagged items are listed in the review.

## 2026-10-27 — frozen (Pablo's ruling)

PLe is frozen: `src/adele/rubrics/data_v2/Paolo_Pablo/PLe.txt` at `7acbcee`, sha256 `ab994dd7d70646f5…`. Change it
only with a new provenance entry and a relabel. Evidence at the freeze comes from the two production inputs, where the judge sees the goal but no tests,
solutions or expected actions (`docs/judge-input.md`): `experiments/benchmarks/tau2-goal` (242 clean tau2 tasks) and
`experiments/benchmarks/goal-visible` (six coding and terminal sets, 787 tasks). The freeze bar was set before the
goal-visible results (its PREREGISTRATION.md, amendment `97cda10`) and holds: every PL cell labelled or explained, PLp
negative on SWE-bench Verified, and no PL rubric significantly positive on any set.
Signals (Spearman with solve rate): tau2 −0.15 (p 0.02); SWE-bench Verified −0.31. No
significant link on the other five sets. Known limits: the evidence is weak; most tasks sit at one or two levels.
