# ms-benchmarks — run log

## 2026-10-02 — set built, pre-registered

`make_subset.py`: 1,070 single-read tasks + 13 long ProgramBench tasks. `adele mass plan`: 2,140 + 26 cells. Analysis tested
on synthetic labels (deleted).

## 2026-10-02 — amendment 1

Rivercross dropped (no other agents). `make_subset.py` rerun: 1,016 single-read + 13 long tasks. Run held until the MS lab regression.

## 2026-10-02 — labelled, analysed

After the MS lab regression: `ms-benchmarks` (2,032 cells, 11 rounds plus retries) and `ms-benchmarks-long` (26 cells,
chunked judge; one protocol rejection relabelled). 2,054 of 2,058 labelled by `claude-opus-5-5`; protein-active-learning
and zip-password-finder unlabelled (classifier fallbacks). Round 1 collect stopped on two answers written via
`prompts/../responses/`; the runner now normalises paths (test added), then collect and check passed. `check` OK on
both runs. Ran `analysis/analyse.py`; results in RESULTS.md.
