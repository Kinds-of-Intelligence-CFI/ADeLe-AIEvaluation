# benchmarks — demand annotation on real agent benchmarks

Owner: Pablo.

The external-validity arm: annotate real benchmark instances on the active
agentic dimensions, join those demand vectors to per-instance success/failure for
many models, and test whether demand predicts success well enough to extrapolate
to a model not in the fit.

## Where things are

| | |
|---|---|
| procedure, step by step | `docs/runbook-benchmarks.md` |
| success-matrix loaders | `src/adele/results/` (SWE-bench, MathArena, ARC Prize, tau2, Inspect) |
| instance freezing | `src/adele/instances.py`, CLI `adele instances prepare` |
| judge | CLI `adele agentic judge` |
| partner data requests | `docs/partner-data-request.md` |
| pilot sample (4 benchmarks × 5 tasks) | `pilot/`, regenerate with `adele agentic pilot --seed 0` |

## Runtime data is not in the repo

Everything the pipeline downloads or produces at runtime lives under a gitignored
`data/` tree: `data/downloads/` raw dumps, `data/instances/` frozen annotation
inputs, `data/results/` success-flag parquets, `data/annotations/` judge output.

This is not only a size decision. Some benchmarks (Terminal-Bench among them)
carry no-training-corpora canary strings in their task text, which must never land
in a public repository.

`ADeLe_battery_data/` at the repo root is a different thing: the *published*
battery release, tracked and LFS-backed.

## Status

The pipeline is built; the tau2 instance sets are frozen. Production annotation
has not started — the runbook gates it behind a rubric regression check, which is
where the frozen rubric tag should be pinned.
