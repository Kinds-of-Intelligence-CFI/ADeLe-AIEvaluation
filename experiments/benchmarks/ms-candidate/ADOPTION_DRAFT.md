# Adoption draft (not applied): provenance entries and team note

Drafted 2026-10-17 for Pablo. Nothing here is applied. Adoption means copying `MSc_candidate_v4.txt` to
`src/adele/rubrics/data_v2/Paolo_Pablo/MSc.txt` and `MSm_candidate.txt` to `.../MSm.txt`, appending the entries below
to `docs/rubric-provenance/MSc.md` and `MSm.md`, and relabelling both rubrics on the released sets. It waits for
Pablo's OK, his 15 agent-side labels (set H) and the no-reasoning check (amendment 6).

## Entry for `docs/rubric-provenance/MSc.md`

```
## 2026-10-?? — one driver: what the task needs from the other party (ms-candidate, v4)

OPERATIVE CHANGE. Pablo's framework (2026-10-17): the demand is how hard it is to get from the other party what the
task needs. A task needs something from them only if its success depends on it, as the task states it or as it is
judged; the kind of obstacle sets the level (0 no one; 1 nothing in the way, including a request turned down; 2 a
willing party guided; 3 doubts to be overcome; 4 opposition to be overcome; 5 parties whose needs cannot all be met).
New intro and level statements; the Level 4 refund example states the needed stance ("…to accept the store credit it
does offer"); a new Level 1 example (a refused library patron, "answering their objections with the rule"). The "does
not cover" paragraph is unchanged.
Why: the old levels graded the counterpart's disposition, so judges placed every refusal of a persistent party at 4,
reading the refusal as something the party must accept (msc-l4-note, ms-candidate amendments 1 to 3).
Measured (experiments/benchmarks/ms-candidate, Opus 5.5 low, v2 prompt, three repeats): every MSc lab check holds
(r36 D2 noisy: 3, 3, 5 then 5, 5, 5); battery M01 rises to 4 (the old text placed it at 3); the five refusal pairs score
1; supplier and builder pairs stay at 4. Bare digit: [amendment 6 result]. Human, agent-side tau2: [set H result].
Known limit: an ungraded task whose purpose needs the party's buy-in but whose position rests on authority or a rule
(the curfew pair) is placed at 1; a purpose clause (v5) did not fix it and made the supplier pair worse.
Superseded attempts: v1 to v3 (amendments 1 to 3), v5 (amendment 5).
```

## Entry for `docs/rubric-provenance/MSm.md`

```
## 2026-10-?? — back toward v1 MS (ms-candidate)

Three edits, at Pablo's direction (keep MSm as close to the original as possible): the v1 opener restored (the
2026-08-25 rewording rested on a false claim that no other v1 file opens "This criterion assesses"; AS and QLq do);
the "does not cover" Note gains the sincerity condition ("…unless the task gives reason to doubt it"); the Level 4
stated-stance passage removed, since the Note says it, so Level 4 is v1 word for word. Level 2 (truth-teller routing)
and Level 5 (interlock rule) keep their tested v2 text.
Measured (ms-candidate, mscand-1): every MSm lab check that held still holds; F-on-MSm fails under both texts on the
two PLs Level 5 examples (the overlap Pablo accepted on 2026-10-02). Bare digit: [amendment 6 result]. Human: [set H].
```

## Team note (for Pablo to send; plain text)

```
Subject: MSc rewritten around one question; MSm back to v1

Hi all,

Short update on the two social rubrics.

MSc (Communication and social interaction). The old levels graded how the other party behaves (helpful, hesitant,
opposed). Judges then put every refusal of a pushy customer at Level 4, as if the customer had to accept the refusal.
The new text asks one question: what does the task need from the other party, and what stands in the way of getting
it? Only what the task's success depends on counts, as the task states it or as it is graded. The level is the kind of
obstacle: none, a willing party to guide, doubts, opposition, or several parties whose needs cannot all be met.
A refusal that only needs answering is Level 1; bringing someone to accept an alternative they resist is Level 4.

It keeps every result of our lab regression, fixes one battery item the old text got wrong, and places refusals as
intended. One known limit: a task whose purpose needs buy-in but rests on authority (a parent setting a curfew) can be
placed too low.

MSm (Mind modelling). Brought back close to the original v1 text: the v1 intro and Level 4 are restored; the tested
v2 changes at Levels 2 and 5 stay. It keeps every lab result.

Both texts, the runs and the pre-registration are in experiments/benchmarks/ms-candidate on agentic-v2.

Best,
Pablo
```
