# PL family — boundary consistency audit (Stage 0, 2026-08-22)

Texts audited: `PLp.txt` (v2-draft, rev. 2026-08-16), `PLe.txt` (v2-r39, adopted),
`PLs.txt` (v2-draft, rev. 2026-08-20, unvalidated). No judge calls; this is a reading of
the three texts against one another. Any contradiction found here would otherwise be
measured later as judge noise and misdiagnosed.

## The 3×3 table — does A's text exclude B's driver, against B *as it now stands*?

| A ↓ excludes B → | PLp (finding a plan) | PLe (keeping it on track) | PLs (anticipating what unfolds) |
|---|---|---|---|
| **PLp** | — | ✅ "sustained execution, keeping the work on track… do not raise this demand — though devising the revision does" — still carves correctly against the *new* PLe, which scores checking availability, not recovery | ❌ **NOTHING EXCLUDES IT.** See Finding 1 |
| **PLe** | ✅ "the deliberation that finds or chooses a step is the work of devising, not executing" | — | ⚠️ silent; see Finding 2 |
| **PLs** | ✅ "searching for or choosing among one's own actions is planning work… a candidate action enters here only as a stipulated change whose consequences must be traced" | ⚠️ silent, but L0 ("nothing has to be run forward") does the work; see Finding 3 | — |

Two of the six cells were the ones the plan flagged as at risk from PLe's driver change.
Both survive: PLp's exclusion of PLe reads correctly against checking-availability (it
names execution and staying-on-track, not recovery or propagation), and PLe's exclusion of
PLp is unchanged and reciprocal. **The defect is in a cell the plan did not flag.**

---

## Finding 1 (material) — PLp's upper ladder is built on lookahead, which is now PLs's driver

PLp excludes execution but says nothing about anticipation, and its own level definitions
lean on it:

- **L3**: "decisions interact, so an option that looks good locally can be wrong *because of
  its consequences several steps later*, and alternatives must be compared *by looking
  ahead* before committing."
- **L4**: "most approaches that appear viable *fail for reasons that only become evident
  when explored*."

Working out what a candidate course leads to is precisely what PLs scores. So on any item
where PLp is high, PLs is loaded too — **by construction, in the text, before a single
annotation**. The asymmetry we designed (planning may use an externally supplied world
model; simulating does not require planning) is stated one-directionally in PLs and left
unstated in PLp, so the carve only holds from one side.

Consequence if left alone: Stage 5's collinearity check would find PLp and PLs correlated
and we would not be able to tell a real construct overlap from a text artefact. Worse, the
PLp L3 chess example ("a natural-looking move can fail to a consequence several moves
deep") is close to double-loading — the same instance would score on both dimensions for
the same reason.

**Proposed fix** (drafted, NOT applied — see below), inserted into PLp's does-not-cover:

> Nor does it cover working out what a course of action would lead to: tracing the
> consequences of a given course through a situation's own workings is anticipation, not
> planning, and does not raise this demand — what counts here is the search among candidate
> courses, and consequences bear on it only as what makes candidates hard to tell apart
> before committing.

This preserves L3/L4's existing language (the *interaction of decisions* is still what
places them) while re-anchoring "consequences" as a property of the search rather than of
the world model.

**Why it is not applied yet.** PLp's meta line claims validation across rounds 1–21. An
edit to its does-not-cover invalidates that claim until re-tested, and Stage 4 is already
scheduled to regression-test PLp. Applying it now would mean Stages 1–3 run against a text
whose validation status is neither the old one nor a new one. The edit is therefore held as
`PLp_stage0_candidate.txt` and applied at Stage 4, where its regression is already paid for.
Stages 1–2 are PLs-only, so nothing downstream is blocked.

## Finding 2 (minor, no action) — PLe is silent on anticipation

PLe's exclusions cover devising, stakes, length, memory load and information-finding, but
not "working out what a check would reveal." A task could in principle demand hard
anticipation to know what being on track *looks* like. No edit is proposed: PLe closed at
α 0.967 with its exclusions measured, and re-opening a closed rubric to pre-empt a leak that
has never been observed is exactly the iteration-without-evidence this project has avoided.
Instead the risk is monitored: Stage 3's off-diagonal will show PLs↔PLe leakage if it exists,
and only a measured leak justifies text.

## Finding 3 (deliberate non-action) — PLs is silent on execution

PLs does not explicitly exclude execution and monitoring; its L0 ("nothing has to be run
forward") carries the weight. Battery item **B7** (reconcile a year's ledger — a pure
execution task) exists precisely to test whether that implicit routing holds. Adding an
explicit exclusion now would make B7 pass trivially and destroy the information the probe
was built to yield. **Left as-is on purpose**; if B7 scores above 1 in Stage 1, the
exclusion is written then, with a measurement behind it.

## Finding 4 (housekeeping) — shared example across PLp and PLs

PLp L0 and PLs L0 both open with the Darwin publication-date item. Harmless (both score 0,
for different stated reasons) but worth noting if the rubrics are ever printed side by side.

---

## Stage 0 verdict

One material defect found (Finding 1), fix drafted and deliberately deferred to the stage
that already pays for its regression. Two silences examined and left alone with the reason
recorded. No blocker to Stages 1–2, which concern PLs alone.
