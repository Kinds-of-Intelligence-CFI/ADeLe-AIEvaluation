# Where the evidence for these rubrics lives

This PR ships the rubrics, the loader and the tests. It does **not** ship the lab record —
36 rounds of pre-registered measurement, roughly 7 MB of item sets, judge labels, preregs
and round write-ups — because that is a research notebook, not something a reviewer should
have to page through to assess the change.

**The record is preserved on the branch `rubrics/v2-lab-record`**, at the same commit as this
PR's head. Every `labs/rubric-qa/...` path cited in the docs and commit messages resolves
there, unchanged:

```
git show rubrics/v2-lab-record:labs/rubric-qa/README.md          # the 36-round record
git show rubrics/v2-lab-record:labs/rubric-qa/battery-v1/README.md
git show rubrics/v2-lab-record:labs/rubric-qa/r33/README.md      # the PLs x MCu measurement
git checkout rubrics/v2-lab-record -- labs/                      # or pull the whole thing
```

## What is worth reading there, if a claim in this PR is in question

| claim in this PR | where it was measured |
|---|---|
| the four dimensions separate | `battery-v1/` — 36 items, all four dimensions on every item, 11/12 directions at gap 3+ |
| each demand is driven by its stated factor | `r36/` — six minimal pairs, each moving one driver |
| examples are high on one dimension and low on others | `r34/` — all 77 examples cross-scored, 95% clean |
| `MSm` no longer double-counts `MSc` | `r31/` — ten items built to separate them |
| `PLs` × `MCu` overlap is structural | `r33/` — and summarised in `docs/note-PLs-MCu-overlap.md` |
| three pre-PR audit findings, two refuted | `r32/` |

Negative results are in there too, deliberately: `r30/` holds the narrowed `MSm` draft that
failed its pre-registered test, and `r34/` records a round invalidated by a blinding mistake
of my own. Both are cited in the commit history, so both need to remain reachable.
