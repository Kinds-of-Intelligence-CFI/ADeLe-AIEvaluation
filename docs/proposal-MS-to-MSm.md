# Proposal: rename v1 `MS` to `MSm`

**Status:** **decided (Pablo, 2026-07-27) and implemented on the v2 side.** `MSm` now exists as
an active v2 dimension: `rubrics/data_v2/v1/MSm.txt`, carrying v1 `MS`'s text unchanged. The four
agentic rubrics' routing resolves, and the annotation pipeline has a rubric under the code.
**v1 itself is untouched** — `data_v1/MS.txt`, `DEMAND_ORDER`, and the published `MS` label column
all stay exactly as they are, so paper reproduction is unaffected. A test asserts the judged text
of `MSm` is byte-identical to v1 `MS`.

**Scope:** a rename only. **No change to the text of `MS` is proposed here.**

**Two sub-decisions deliberately deferred**, because both are text changes and the standing rule is
that no text changes without a measured reason to change it:

1. **The header.** `MSm.txt` still reads `# Mind Modelling and Social Cognition`, so the judge
   prompt still says *"Score the level of Mind Modelling and Social Cognition…"*. Shortening it to
   "Mind Modelling" is what makes the `MSm` / `MSc` sibling split legible in the prompt itself, but
   it changes what the judge reads and could move labels. Settle it with a paired annotation of one
   battery under both headers, not by assertion.
2. **Whether v1 should follow.** Renaming `data_v1/MS.txt` and the `MS` label column is a v1-owner
   decision and would touch paper reproduction. The v2-side carry above makes it unnecessary for
   the agentic PR to land.

## What

`src/adele/rubrics/data_v1/MS.txt` — "Mind Modelling and Social Cognition" — becomes
`MSm.txt`, code `MSm`, title "Mind Modelling". Every reference to the code `MS` in loaders,
manifests and label columns follows.

## Why

v1's `MS` covers two separable things: **modelling** what another agent believes, intends
and feels, and **acting on** that model to steer an interaction. v2 splits the second half
out as `MSc` (Communication and Social Interaction). With the parent still called `MS`, the
pair `MS` / `MSc` reads as parent and child when they are siblings, and a reader has no way
to tell that `MS` is now the narrower of the two.

There is also a concrete double-count. `MS`'s own Level 5 example is:

> *"Leading a negotiation between multiple stakeholders where each party has different
> beliefs about others' intentions and bottom lines, while managing the complex emotional
> dynamics between opposing personalities."*

That is `MSc` Level 5's construct — several parties whose required positions are mutually
exclusive. Whatever the codes are called, one item is being scored twice. Renaming does not
fix that; it makes it visible. (Whether that example should move is a **separate** question,
deliberately not bundled here.)

## What it unblocks

All four new v2 rubrics route mind-reading demand to "Mind Modelling (`MSm`)" — five
occurrences across `PLp`, `PLe`, `PLs`, `MSc`. **No `MSm` file exists**, so the routing
currently resolves to nothing and the annotation pipeline has no rubric under that code.
This is the one item blocking the agentic PR.

## Cost

- One `git mv`, plus the code and manifest references.
- Existing label sets carry an `MS` column. They stay valid — the construct is unchanged —
  but need a column rename or an alias in the loader. Published results are unaffected in
  substance; anything quoting the code by name needs a footnote.
- v1 is otherwise untouched.

## Alternative considered

Point the v2 rubrics back at `MS` instead. Cheaper and needs no v1 change at all, but it
leaves the sibling relationship unreadable and leaves the Level 5 negotiation item scored by
two dimensions with no signal that anything is odd. Recommended only if the v1 owners decline
the rename — in which case the four v2 rubrics need a one-line edit each, which is trivial.

## Recommendation

Rename. If sign-off is slow, land the agentic PR with the rubrics routing to `MS` and switch
to `MSm` when the rename lands; do not merge with a dangling `MSm`.
