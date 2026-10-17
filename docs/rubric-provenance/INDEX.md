# Rubric provenance — full metadata moved out of the rubric files (2026-08-25)

The `#!` line in each rubric had grown into a changelog. Two judging rounds were contaminated by
a judge reading it (r58, r64), and although `catalog.py` already strips `#!` lines when loading a
rubric, anything that reads the raw `.txt` sees the whole record. The changelogs now live here.
The short metadata line left behind was removed on 2026-09-02 (see `docs/02-rubrics.md`), so the
rubric files carry no version marker; the labels below are the last revision each file records.

- [PLe](PLe.md) — v2-r45, 2026-08-26
- [PLp](PLp.md) — v2-r43, revised 2026-08-22 (example pass 2026-08-25)
- [PLs](PLs.md) — v19, 2026-08-26
- [MSm](MSm.md) — v2-draft, revised 2026-08-20 (r69 appended 2026-08-26)
- [MSc](MSc.md) — v2-draft, revised 2026-08-16 (r70 and r75 appended 2026-08-26)
- [SPv](SPv.md) — v2-r70, 2026-08-26 (deferred from the active set)
- [SPa](SPa.md) — v2-r70, 2026-08-26 (deferred from the active set)
- [JUDGING](JUDGING.md) — the judging protocol for rubric rounds
