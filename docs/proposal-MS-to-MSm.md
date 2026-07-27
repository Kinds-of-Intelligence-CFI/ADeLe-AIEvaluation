# Proposal: rename v1 `MS` to `MSm`

**Status:** proposal. Requires sign-off from the v1 owners. Nothing has been renamed.
**Scope:** a rename only. **No change to the text of `MS` is proposed here.**

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
