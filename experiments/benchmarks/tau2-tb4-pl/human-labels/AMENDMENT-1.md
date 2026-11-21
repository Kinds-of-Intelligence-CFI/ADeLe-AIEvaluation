# Amendment 1 to SEAL-plp-tb4.md (2026-09-28, after 7 of 12 labels, before any unblinding)

After seven blind labels, Pablo reported low confidence in several of them and asked to look back.
To keep the round blind, he chose to have the rubric put as its own tests in decision form:
- five yes/no gates, quoted in the round transcript and below;
- no judge labels, and no views from Claude on any task.

- Tasks 1–7 are re-checked with the gates. The re-check goes in `checklist_level`,
  `checklist_gate` (the gate where the walk stopped) and `checklist_note`. The blind label in
  `pablo_level` is kept unchanged.
- Tasks 8–12 are labelled with the gates from the start. `pablo_level` then equals
  `checklist_level`, and `note` says so.
- The decision rule of the seal is reported twice, on the blind labels (tasks 1–7) and on the
  checklist labels (all 12). The checklist result is the one that decides; the blind result is
  reported beside it.

Gates, as given to Pablo:
1. Is the plan given (one action or retrieval, or explicit steps)? Yes: 0.
2. Does one standard routine cover the whole task and decide the actions, with no split into
   subtasks? Yes: 1.
3. Must it be split into subtasks whose choices constrain each other, so that a sensible early
   choice can need revising because of a later one? No: 2.
4. Does recognising what kind of task it is already give the outline of a workable plan (known
   methods, subtasks listable at the start)? Yes: 3.
5. Does any established procedure exist for this kind of work? Yes: 4. No, and a workable plan
   is a discovery: 5.

Not counted: execution length or effort, finding things out about the environment, checking or
debugging, unless they make the plan itself harder to find. In doubt between two levels: the
lower one.
