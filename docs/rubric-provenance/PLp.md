# PLp — provenance and change record

Moved out of the rubric's `#!` line on 2026-08-25. Rounds are in `labs/rubric-qa`.

- ADeLe v2 (agentic) — validated, voiced and styled to v1 (subject 'The task', guards marked Critically/Importantly/Note, no em-dashes or semicolons; no operative clause changed)
- version: v2-r43
- source: Paolo_Pablo
- revised: 2026-08-22
- validated: labs/rubric-qa rounds 1-21 (incl. solver oracle) + r42 family discrimination (diagonal 3/3; PLp-high/PLs-low on seating, timetabling, approach-choice) + r43 (a drafted lookahead exclusion changed no score and was withdrawn under the stopping rule; the chess co-load with Simulating is a property of chess, not a text defect)
- text unchanged since 2026-08-16 apart from the 2026-08-25 example pass: one cross-reference to another level and six parenthetical rationale glosses were removed, against a v1 rate of zero cross-references and one gloss in 335 example bullets. Each gloss restated something the level statement or the exclusions already say, so nothing operative was lost. Quantities that decide an example were filled in, following v1's flat rate of about 45 per cent concrete detail across all six levels. No operative clause changed.

## 2026-10-01 — candidate O adopted (Pablo's ruling)

- **What changed.** The preamble now names one driver: the search that remains for someone who has the knowledge
  the task calls for ("knowing how tasks of a kind are done is knowledge, not planning"). It rises with how rarely a
  plan built step by step, taking the option that looks best and fixing slips as they show, comes out workable
  without undoing an earlier step, and with how far back the undoing reaches. Each level keeps its description and
  ends with one odds anchor (Level 1 never undone; 2 hardly ever, at any length; 3 between one in two and one in a
  hundred; 4 under one in a hundred; 5 no knowledge structures the search). Where description and odds disagree,
  the odds decide. The scope paragraph adds: only choices that could go wrong count; answer format adds nothing (UG
  carries guessability); for a task scored partway through, the plan is the one still to be made. New examples:
  Tower of Hanoi (Level 1), a trappy sliding-block puzzle (Level 3), exam timetabling (Level 4).
- **Why.** PLp followed task length rather than search on rivercross (`experiments/benchmarks/rivercross-v2`). The
  path B2 → S → S-q → O is recorded in `experiments/benchmarks/plp-b2` (amendments 1 to 6). Rejected on the way:
  levels named in the preamble (desideratum 7), "two things set the level" (two drivers, desideratum 3), and odds of
  success read as a guessing floor (overlap with UG).
- **Evidence.** Lab regression (`experiments/benchmarks/plp-candidate/lab-regression`, Opus low × 3, v2 prompt): 86 of
  101 checks hold (current text 83); no two-level move; open and multiple-choice versions of the same planning
  task never split; the Mars-landing PLe leak is gone. SWE-bench gate: ρ = −0.71 with solve rate (current −0.55).
  Rivercross: crossings-left weight 0.22 (current 0.33).
- **Known loss, accepted.** The Level 1 covering-letter example reads 2 with examples stripped (5 of 6 labels). It is a
  1/2 boundary item: the current text puts it at 2 about a third of the time, and no wording tested (S, O, O
  without the "could go wrong" sentence) brings it back. Pablo accepted O with this loss on record.
- **Open.** Judges' odds estimates were not validated (the rivercross proxy does not match O's agent). Real-task
  relabel and incremental prediction (desideratum 9) are next.
- version: v2-o (2026-10-01); sha256 322674ef…
