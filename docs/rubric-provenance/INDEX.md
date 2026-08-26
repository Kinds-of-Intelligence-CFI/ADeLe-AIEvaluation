# Rubric provenance — full metadata moved out of the rubric files (2026-08-25)

The `#!` line in each rubric had grown into a changelog. Two judging rounds were contaminated by
a judge reading it (r58, r64), and although `catalog.py` already strips `#!` lines when loading a
rubric, anything that reads the raw `.txt` sees the whole record. The changelogs now live here and
each rubric keeps a short, judge-safe metadata line that `catalog.py` can still parse for version.

- [PLe](rubric-provenance/PLe.md) — version: v2-r44, revised: 2026-08-22
- [PLp](rubric-provenance/PLp.md) — version: v2-r43, revised: 2026-08-22
- [PLs](rubric-provenance/PLs.md) — version: v2-draft, revised: 2026-08-25
- [MSm](rubric-provenance/MSm.md) — version: v2-draft, revised: 2026-08-20
- [MSc](rubric-provenance/MSc.md) — version: v2-draft, revised: 2026-08-16
