# tbsci-pl — run log

## 2026-10-01 — set built, pre-registered

Set and analysis scripts built and tested on synthetic labels (not kept).

## 2026-10-01 — labels collected, analysed, released

Run `tbsci-pl` (`adele mass`, subagent backend, Opus 5.5 low): two rounds. 207 of 210 cells labelled.
`protein-active-learning`: PLe and PLs answered by Opus 5 on both attempts (classifier fallback; no label). PLp's first
answer was also a fallback and was written twice (`check` flags it); its retry was not run (Pablo's OK). Ran
`analysis/analyse.py` and `export.py` (release/). Results in RESULTS.md.
