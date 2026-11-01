# experiments/

One directory per experiment. They all have the same shape, so understanding one
is understanding all of them.

```
<experiment>/
  README.md          what this experiment claims, and what it does not
  preregistrations/  the protocol, committed BEFORE any label collection
  frames/            the items shown to judges, and the ground truth behind them
  prompts/           templates (dimension-agnostic) + the generated prompts
  labels/            raw judge output and the parsed CSVs
  analysis/          scripts that turn labels into numbers
  results/           the frozen output of those scripts — quote these, not prose
  figures/           generated only from the artifacts above
```

Not every experiment fills every folder, and an experiment that predates this
layout may still be organised by dimension. Where a subdirectory groups one
dimension's whole pipeline (`rivercross/memory/`, `rivercross/ple/`), that is the
older shape and is being kept because the analysis scripts anchor on it.

## Three conventions

**1. Pre-register before collecting.** The protocol, the judge panel, the gates
and the analysis script are committed before any labels are gathered. The commit
order in git is the audit trail. Deviations get reported as deviations, not
silently absorbed. If a judge panel or an inclusion criterion is chosen after
seeing the gate results, say so — that is a post-hoc choice and it changes what
the result means.

**2. Record the rubric version with every run.** Each annotation run records the
rubric tag it ran against *and* the sha256 of the rubric text it actually read.
A tag alone says what the repository held; the hash says what the judge saw. Two
experiments can only be compared when their hashes match.

**3. Figures come from frozen artifacts.** Never hand-drawn, never edited. If a
number in a README and a number in `results/` disagree, `results/` wins and the
README is wrong.

## A note on negative results

They stay in the tree. `rivercross/ple/labels/2/` holds the per-transition method
that collapsed to a near-constant label; the memory README records the two earlier
`MMs` prompts that failed before v3 worked. A protocol that failed its
pre-registered test is evidence, and removing it would misrepresent how much was
tried.
