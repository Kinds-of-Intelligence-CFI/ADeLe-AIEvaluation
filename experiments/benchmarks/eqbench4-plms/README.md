# eqbench4-plms

Planning (PLp, PLe, PLs) and social (MSm, MSc) labels on the 120 EQ-Bench 4 persona scenarios, tested against a new,
absolute outcome: whether the role-played person openly disclosed their hidden core issue. See `PREREGISTRATION.md`.
Data and sources: `../eqbench4-data/` (`NOTES.md`). Labels via `adele mass` (spec
`../mass-annotation/specs/eqbench4-plms.toml`). Outcome judging: `make_outcome_prompts.py` → `relays.py` (agents
`eq-outcome-judge.md`, `eq-outcome-dispatcher.md`, installed in `~/Developer/ADELE/.claude/agents/`) →
`collect_outcome.py` → `labels/eq4-outcome/outcomes.csv`. Analysis: `analysis/analyse.py` → `results/analysis.json`.
Log: `RUNLOG.md`.

Task text, persona briefs and transcripts stay in the gitignored `data/` tree and `judge-io/` (the EQ-Bench site
repository has no licence).
