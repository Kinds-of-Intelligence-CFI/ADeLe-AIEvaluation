# pls-relabel — PLs on the seven agentic benchmarks under the adopted text

Owner: Pablo. PLs gained three computer-world examples on 2026-10-04 (`../pls-computer`). This study redoes the PLs
labels of the PL studies' clean sets with that text, to replace the released ones. Judge: Opus 5.5 at effort low,
v2 prompt.

**Status.** Pre-registered 2026-10-04; running (launched the same day, at Pablo's request).

| | |
|---|---|
| design, predictions | `PREREGISTRATION.md` |
| tasks | `subset.csv`, `subset_long.csv` (copied from `../ms-benchmarks`) |
| runs | `../mass-annotation/runs/pls-relabel/`, `../mass-annotation/runs/pls-relabel-long/` |
| analysis | `analysis/analyse.py` → `results/analysis.json` |
| what happened | `RUNLOG.md` |

## Reproduce

```
adele mass pin experiments/benchmarks/mass-annotation/specs/pls-relabel.toml
adele mass pin experiments/benchmarks/mass-annotation/specs/pls-relabel-long.toml
# judging: /annotate pls-relabel and pls-relabel-long
python experiments/benchmarks/pls-relabel/analysis/analyse.py
```
