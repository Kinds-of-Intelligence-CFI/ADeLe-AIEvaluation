# Examples review — shared brief (2026-10-04)

Pablo asked to fix the example bullets of every active v2 rubric so that each one is accurate and meets the
rubric desiderata. This brief is the common bar. Each reviewer covers one or more rubrics.

## Paths (repo R = ~/Developer/ADELE/ADELE_v2/ADeLe-AIEvaluation)

- Rubrics: `R/src/adele/rubrics/data_v2/Paolo_Pablo/{PLp,PLe,PLs,MSm,MSc}.txt`, `R/src/adele/rubrics/data_v2/Marko/{MMe,MMp,MMs}.txt`.
  Read only; never edit anything under `src/`.
- v1 rubrics (the style and accuracy reference): `R/src/adele/rubrics/data_v1/*.txt`.
- Provenance and Pablo's rulings: `R/docs/rubric-provenance/<DIM>.md` (PLp, PLe, PLs, MSm, MSc; none for MM),
  `R/docs/PL-family-close-out.md`, `R/docs/rubric-provenance/JUDGING.md`.
- How the desiderata are audited: `R/docs/PL-desiderata-audit.md`, `R/docs/PL-family-final-desiderata-check.md`.
- A worked example of the accuracy check (PLs): `R/experiments/benchmarks/pls-computer/EXAMPLES_REVIEW.md`.
- Output: `R/experiments/benchmarks/examples-review/<DIM>/REVIEW.md` and `<DIM>/<DIM>_candidate.txt`.

Rules: never `cd` in Bash (use absolute paths). Never read `.env`. No judge calls, no commits, no pushes.

## The nine desiderata (what they mean for examples)

1. Taxonomy fit — not about examples.
2. Disentangles from siblings — an example should not demand a sibling dimension (PLp, PLe, PLs, MSm, MSc, MMe,
   MMp, MMs) at a high level unless the rubric accepts that co-load (e.g. chess on PLp and PLs is accepted).
3. Single driver — examples at different levels should differ in the rubric's driver, not in volume, length or
   domain difficulty. A long or hard task is not higher on a dimension unless its driver is higher.
4. Intuitive — a reader agrees with the placement on reading it.
5. Usable by an annotator — the example shows how to apply the level, not a hairline case only an expert can place.
6. Examples disentangle — each example is a clean instance of its level for this dimension, with neutralising
   detail where a sibling dimension would otherwise load.
7. v1 shape and voice — see "Style" below.
8. Thoughtful — no trivial, contrived or self-contradictory examples.
9. Criterion validity — not about examples.

## The accuracy bar

Each example must be correct under its own rubric's clauses: level statements, Notes, the "does not cover" paragraph
and any carve-outs. Derive the placement explicitly. Typical failures found in PLs:
- a stated rule fully determines the course, so the answer is arithmetic or an invariant, not the driver;
- the feature named by the level (coupling, feedback, sensitivity, hidden state, deception, stance...) does not
  actually change the answer;
- the best answer is a standing rate or base rate;
- the question can be settled by a shortcut the rubric places lower;
- the example relies on a cue (one repeated phrase) that would teach the judge a surface pattern;
- the example contradicts a carve-out (e.g. knowledge, perception, another dimension's territory).

Keep examples that encode a ruling recorded in the provenance or close-out files. If such an example looks wrong,
flag it for Pablo; do not change it.

## Style (desideratum 7, measured on the 18 v1 files)

- Natural, realistic tasks someone would actually set or meet, as in v1 (a vase knocked off a table; scaling a
  recipe). Not puzzles engineered to sit on a boundary.
- Example length: v1 mean about 26 words per bullet (most 10–45). Keep new or rewritten bullets near that; trim long
  ones only if accuracy survives.
- No glosses or parenthetical rationales explaining the level; no cross-references to other levels; no em dashes;
  no semicolons. Include the quantities that decide placement (v1 carries concrete detail at a flat rate).
- Vary domains within a level and across the file. Avoid one stock phrase across several examples.
- Keep roughly the current number of bullets per level (v1 has three; current files have three to six).

## Minimal change

Fix only what fails. Prefer a small rewording to a replacement. Never change level statements, Notes, preambles or
the "does not cover" paragraph: only example bullets. The candidate file must equal the current file except for
bullet lines (added, removed or reworded). Check this mechanically before finishing.

## Deliverables per rubric

`REVIEW.md`:
1. A table of every bullet: level, short name, verdict (keep / fix / replace / drop / flag), why (the clause it
   meets or breaks), confidence that a problem is real.
2. The proposed wording for every changed bullet, with a one-line derivation of its placement.
3. Style numbers for the current and candidate bullets: count, mean words, max words.
4. Open questions for Pablo, including any flagged ruling-based examples.

`<DIM>_candidate.txt`: the current file with only the proposed bullet changes.

Report in your final message: the counts (kept, fixed, replaced, dropped, flagged), the three most important
problems, and anything you were unsure about.
