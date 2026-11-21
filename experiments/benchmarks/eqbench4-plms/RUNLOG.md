# eqbench4-plms — run log

## 2026-10-03 — set up, pre-registered

Data fetched by `../eqbench4-data/` (agent, no judge calls). Pablo chose a new outcome after the published score
proved relative. `eqbench4` registered (120 instances). `adele mass plan`: 600 cells, longest prompt 34,512 chars.
`make_outcome_prompts.py`: 1,260 cells (1,200 + 60 repeats), median 13.6k chars, max 44.3k, longest line ≤ 1,010
chars. Analysis tested on synthetic labels (not kept). Not pinned.

## 2026-10-03 — labels and outcome collected, analysed

Runs `eqbench4-plms` (600 cells, 12 relays) and `eq4-outcome` (1,260 cells, 26 relays incl. a 5-cell dry run), Opus 5.5
low, pinned/started after the pre-registration was pushed (`c279564`). All checks OK: no rejections, no classifier
stops, every outcome answer matched to an Opus 5.5 Write call. Ran `analysis/analyse.py`; results in RESULTS.md.
