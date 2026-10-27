# MSm — provenance and change record

Moved out of the rubric's `#!` line on 2026-08-25. Rounds are in `labs/rubric-qa`.

- ADeLe v2 (agentic) — DRAFT for team review
- version: v2-draft
- source: Paolo_Pablo
- revised: 2026-08-20
- derived: data_v1/MSm.txt + L4/L5 carve-out only
- differentiation section made catalogue-independent (no named sibling dimensions)
- 2026-08-20: L2 knights-and-knaves anchor replaced with behavioural-association example + deduction routing note; L5 re-keyed on an interlock of ≥3 mutually constraining attributions (nested or distributed) — deep dyadic recursion now reaches L5; anti-count guard added; second-order false belief pinned at L4; L4 stated-stance carve-out gains sincerity condition. BEHAVIOUR CHANGE vs v1: transparent many-party coordination (independent knowledge-state reads) demotes from L5 to ≤4 (both external-review findings, team-approved; wording revised after adversarial pass)
- 2026-08-25 v1-voice pass, at Pablo's direction: the opener inherited from data_v1/MSm.txt ("This criterion assesses the level of cognitive demands... progresses from...") is not v1-typical, appearing in no other v1 file, and was the phrasing wrongly copied into PLs. It now follows the v1 pattern used across the PL family. Em-dashes and semicolons removed. Two parenthetical rationale glosses moved into their level statements, where the knights-and-knaves routing note is now preserved as a second Note under Level 2. No operative clause changed. CORRECTION TO AN EARLIER CLAIM OF MINE: data_v1/MSm.txt is NOT a modified file. Commit c5130dc was a pure rename of data_v1/MS.txt and the old blob is byte-identical, so the v1 text is authentic and untouched; only this v2 draft inherited the atypical opener.


## Appended 2026-08-26: the three-deep nested route measured (r69)

The turned-agent item (three mutually constraining attributions in one exchange) scored 5/5/5;
r60's two-attribution item had correctly held at 4. Both directions of the L4/L5 boundary are now
measured: single nesting stays at 4, a three-way interlock reaches 5, dyadic or not. The last
untested operative claim in MSm is closed. Still OPEN: no human label on any MSm item.

## 2026-10-04 — examples review

Example bullets only; no level statement, Note or scope text changed. Reviewed against the rubric's own clauses and the
desiderata (`experiments/benchmarks/examples-review/MSm/REVIEW.md`); each new or reworded bullet was placement-checked
with itself removed from the rubric (run `exrev-1`; all within one level of target). Adopted under Pablo's standing
approval for example-only changes. Flagged items are listed in the review.

## 2026-10-04 — seller example shortened

Pablo's decision on a flagged item of the examples review. The Level 5 seller's "final offer" bullet (the dyadic Level 5
route, ruling of 2026-08-20) is cut from 69 to 47 words: the closing gloss ("Only two parties are involved, and …") is
removed and "knows" is used only for the stated fact. The three interlocking attributions are kept (her real limit,
what she thinks he already suspects, what she wants him to conclude). Relabelled in `experiments/benchmarks/relabel-v3`.

## 2026-10-25 — back toward v1 MS (ms-candidate)

At Pablo's direction (keep MSm as close to the original as possible). Three edits: the v1 opener restored (the
2026-08-25 rewording rested on a false claim that no other v1 file opens "This criterion assesses"; AS and QLq do);
the "does not cover" Note gains the sincerity condition ("…unless the task gives reason to doubt it"); the Level 4
stated-stance passage removed, since the Note says it, so Level 4 is v1 word for word. Level 2 (truth-teller routing)
and Level 5 (interlock rule) keep their tested v2 text.
Measured (experiments/benchmarks/ms-candidate, runs mscand-1 and mscand-nr): every MSm lab check that held still holds,
with reasoning and bare digit (bare digit against reasoning: 90% exact, 100% within one); F-on-MSm fails under both
texts on the two PLs Level 5 examples, the overlap Pablo accepted on 2026-10-02. No human MSm labels yet.
