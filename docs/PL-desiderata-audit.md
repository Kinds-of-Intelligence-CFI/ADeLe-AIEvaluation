# PL family — audit against the 9 desiderata (2026-08-22)

Reading only; no judge calls. Verdicts: ✅ met · ⚠️ met with a named caveat · ❌ not met ·
◻️ not assessable by reading. Texts audited: `PLp.txt` (committed), `PLe.txt` (v2-r39,
committed), `PLs_r41_candidate.txt`.

| # | Desideratum | PLp | PLe | PLs |
|---|---|---|---|---|
| 1 | Taxonomy fit | ✅ | ⚠️ | ❌ |
| 2 | Disentangles from siblings (measured) | ❌ | ⚠️ | ❌ |
| 3 | Single driver | ✅ | ✅ | ⚠️ |
| 4 | Intuitive | ✅ | ✅ | ✅ |
| 5 | Usability / annotatability | ⚠️ | ✅ | ⚠️ |
| 6 | Examples disentangle | ✅ | ⚠️ | ⚠️ |
| 7 | v1 shape and style | ✅ | ❌ | ❌ |
| 8 | Thoughtful | ✅ | ✅ | ✅ |
| 9 | Empirical grounding | ❌ | ❌ | ❌ |

## The failures, in the order I would fix them

**D2 · PLp does not disentangle from PLs (text-level, found in Stage 0).** PLp's L3 and L4
are defined through lookahead ("consequences several steps later", "fail only once
explored"), which is PLs's driver, and PLp excludes execution but never anticipation. The
two dimensions therefore co-vary by construction wherever PLp is highest. Fix drafted
(`PLp_stage0_candidate.txt`); needs PLp's regression, i.e. plan Stage 4.

**D7 · PLe and PLs both break the v1 shape constraint.** v1 preambles run 66–217 words but
the house target is the low end; PLp sits at 73. PLe is 151 and PLs 147, with
does-not-cover paragraphs of 168 and 165 words on top. PLe's L4 (140 w) and L5 (135 w)
level definitions are roughly double PLp's mean. This was already the one recorded
exception in the July freeze note, and both rewrites since have made it worse, not better.
It is a real desideratum and the fix is compression, not argument — but note that every
long clause in PLe was added *because a round measured a defect it fixes*, so compression
must not silently drop a tested clause. Recommended: a compression pass that preserves
every clause with a measurement behind it, then a cheap re-run of the existing traps to
confirm nothing broke.

**D1 · PLs has no taxonomy-provenance entry.** `docs/taxonomy-provenance.md` closes
desideratum 1 for the dimensions that existed when it was written. PLs post-dates it and
has no entry; PLe's entry describes the old driver and is now stale. Both are writing
tasks, not measurement.

**D9 · No criterion validity for any PL dimension.** All 41 rounds are internal. No
labels→solver-success study, and the human anchor is thin: PLe has Pablo's labels on 11
items, PLs has none at all. This is the same "only substantively open desideratum" recorded
in July; nothing since has changed it, and no further internal round can.

## The caveats behind the ⚠️s

- **PLs · D3** — the driver is fused (interacting change × precision-as-yardstick). r40
  showed the fusion behaves as designed under all three falsifiers, so this is a met-with-
  caveat rather than a failure; but a fused driver needs its evidence quoted whenever the
  dimension is described, or it reads as two drivers concatenated.
- **PLs · D5, D6** — α 0.97 across r40/r41 is strong, but the one open boundary
  (constitutive vs sequential coupling, r41's failed rule) is a level boundary, and the
  examples at L3/L4 have not been tested for cross-dimension loading.
- **PLe · D2** — PLe↔PLp is clean in both directions; PLe↔PLs has never been measured
  (Stage 3). **PLe · D6** — its examples were rewritten wholesale at r38 and never
  placement-tested.
- **PLp · D5** — the July residual stands: L3/L4 is judge-capability-relative and
  median-of-3 absorbs it.

## What this audit changes about the plan

Two stages of the completion plan are now better justified, and one new item appears:
- Stage 3 (family discrimination) is what closes **D2** for PLe↔PLs and **D6** for both.
- Stage 4 (PLp) carries the **D2** fix for PLp↔PLs.
- Stage 5 (collinearity) is a screen, not criterion validity; **D9 needs solver outcomes**,
  which is a data-pipeline job outside this workstream.
- NEW: a **D7 compression pass** on PLe and PLs, plus **D1 provenance entries** for PLs and
  a refresh for PLe. Both are writing, cost no judge calls, and are the cheapest open items
  on the board.
