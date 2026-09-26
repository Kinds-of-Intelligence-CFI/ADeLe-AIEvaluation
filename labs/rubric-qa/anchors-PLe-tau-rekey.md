# PLe tau-* anchor re-key: 2 → 1 (2026-08-26, for Pablo's sign-off)

The r39 doctrine (adopted 2026-08-22) anchors PLe to who supplies checking. τ-bench tool
calls return success/failure per action, so the checking is FORCED and per-action, which is
the L1 clause ("something the environment returns settles, after essentially each action,
whether that action did what it was for"). The July label of 2 predates that doctrine and was
derived from the r38 candidate's checkpoint wording. r39 recorded the recommendation to
re-anchor; this sheet executes it, flagged post-hoc, pending sign-off.

| item | old anchor (Pablo, 2026-08-21) | new anchor | basis |
|---|---|---|---|
| tau-0007 | 2 | **1** | MEASURED: r39 median 1 |
| tau-0146 | 2 | **1** | MEASURED: r39 median 1 |
| tau-0106 | 2 | **1** | same family, extrapolated (not re-judged) |
| tau-0089 | 2 | **1** | same family, extrapolated (not re-judged) |
| tau-0094 | 2 | **1** | same family, extrapolated (not re-judged) |

Notes.
- The historical record is untouched: r38/label_sheet_r38.md keeps the 2s as given. This
  sheet is the value any FUTURE set must consume for these five items.
- All five old-vs-new deltas are within-1, so no past round's gate outcome changes.
- The deciding phrase attached to the old 2s ("checked at checkpoints and corrected")
  described the r38 candidate text, not the adopted r39 text.
- One caveat for annotation-run design: a τ-bench instance where the user's own confirmation
  is the only return (no tool echo) is not settled per-action, since the rubric excludes "an
  interlocutor's acknowledgement". None of these five is of that kind, but the distinction
  should be kept in view when tau2 is annotated at scale.

Sign-off: ADOPTED 2026-08-26 — Pablo delegated the conflict resolution ("thoughtfully implement the best choice"); option (a) implemented as PLe v2-r45 and measured in r76 (labs/rubric-qa/r76). The 1s are active.

## CONFLICT FOUND WHILE PREPARING THIS SHEET — decision needed, not made

The 2026-08-25 example pass added a Level 2 example to PLe.txt built on the old tau labels:
"Change a customer's order through a tool interface, where each call reports whether it
succeeded and the order state can be read back after each change." Read against the adopted
text, "each call reports whether it succeeded" is checking forced after essentially every
action, which is L1's clause, not L2's junctures. If the re-key above is right, this example
sits one level high in the rubric itself; if the example is right, the re-key is wrong.
The two cannot both stand. Options: (a) move the example to L1 as written; (b) rewrite it so
checking lands at junctures only; (c) reject the re-key and keep the 2s.
RESOLVED 2026-08-26: option (a), on Pablo's delegation. Rationale: the re-key direction is
measured (r39) and (a) only relocates text whose placement the judges had already measured,
where (b) would introduce new unmeasured text and (c) would contradict the adopted doctrine.
Implemented as v2-r45; measured in r76 (T3 held at 2, tau at 1, minimal pair separated).
