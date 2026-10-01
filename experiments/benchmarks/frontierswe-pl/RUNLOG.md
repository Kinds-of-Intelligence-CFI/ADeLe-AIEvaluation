# frontierswe-pl — run log

## 2026-10-01 — set built, pre-registered

Prompt changed to instruction + cited README (`../frontierswe-data/fetch_tasks.py`, re-registered: sha256
`af62cb1bf63e…`, median 3,100 chars, max 9,824). The success threshold was first set at 0.5 (3 tasks dropped), then
changed by Pablo to 0.9 (15 dropped, 19 kept) before any label. Set and analysis scripts built and tested on synthetic
labels (not kept). `adele mass plan`: 57 cells (19 tasks × 3 rubrics), ~0.19M input tokens. Not pinned.

## 2026-10-01 — labels collected, analysed

Run `frontierswe-pl` (`adele mass`, subagent backend, Opus 5.5 low), pinned after the pre-registration was pushed (`1175f15`).
All 57 cells labelled in one round, `check` OK. Ran `analysis/analyse.py`; results in RESULTS.md.
