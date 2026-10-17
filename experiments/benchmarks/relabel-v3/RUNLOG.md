# relabel-v3 — run log

## 2026-10-04

Seven runs pinned after `d6cc9ca` (456 cells), started at Pablo's go with weekly usage at 85%. Relays of up to 100,
at most four at a time, mixing runs. `relabel-v3-plp-long`: the orchestrator mistyped one cell id in the first relay
(`v2PLp-0dba79f32c926f16`, a cell of `relabel-v3-plp`, instead of `v2PLp-0dbdf1c3d7670be8`). That judge found no
prompt and wrote nothing; the protocol check flags its transcript ("prompt file is not a cell of this run") and will
keep doing so. The real cell was sent in the next relay and labelled. One other long-task answer missed the prompt's
last line and was re-judged (runner retry). All 456 cells labelled by Opus 5.5; all other checks pass.
