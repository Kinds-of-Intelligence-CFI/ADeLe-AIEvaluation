# PLe examples review (draft for Pablo, 2026-10-04)

Every example bullet of the current `PLe.txt` (v2-r45, 20 bullets), checked against the rubric's own clauses.
No judge calls were made. Confidence is how sure I am that the problem is real.

Sources read: `BRIEF.md`, `docs/rubric-provenance/PLe.md`, `docs/PL-family-close-out.md`, `JUDGING.md`, both
desiderata audits, the PLs worked example, and the PLe rounds in `labs/rubric-qa` (r34, r38, r39, r59, r62, r63,
r76, the tau re-key sheet).

## The clauses that decide placement

- **Check vs observation.** A check settles, without further work, whether an action did what it was for.
  An observation from which success must still be worked out is not a check.
- **Input vs outcome (r63).** Confirming an input (reagent, temperature) is not a check when the action is
  for an outcome. Where procedural compliance *is* what the action is for, the log is a check (your E2 = 3).
- **Forced vs elected (r39, r76).** L2 checks come with the structure of the work. L3 checks are easy but the
  agent must choose to run them. Whether the task names the check does not matter, in either direction.
- **Ready-made vs constructed.** L3 has easy, adequate checks to hand. L4 has none; the agent must build them.
  L5 has none and none can be built.
- **Rulings kept as they are:** the tool-interface bullet at L1 (tau re-key, r45/r76); the winning-move bullet
  at L0 (your own edit, r38 deployment note).

## Verdicts

| level | example (short) | verdict | why | confidence |
|---|---|---|---|---|
| 0 | checkmate in one, say whether | **drop** | second chess example at L0. Same shape as the winning-move bullet, which is yours and stays. Brings L0 to v1's three | 0.5 |
| 0 | one search-engine query | keep | single act | — |
| 0 | figure that fits the pattern | keep | single act | — |
| 0 | find the winning move | **flag** | your edit. Its second sentence ("All the difficulty is in finding it…") is a rationale gloss, which the style bar excludes | 0.6 |
| 1 | reset a password by prompts | keep | each prompt settles the previous step | — |
| 1 | turn-by-turn directions | keep | every wrong turn is flagged at once | — |
| 1 | recipe, each outcome apparent | keep | outcome is stipulated as plain after each step | — |
| 1 | change an order through tools | keep (ruling) | tau re-key, measured r39 and r76 | — |
| 2 | flat-pack wardrobe | keep | sub-assembly fit is a forced juncture check | — |
| 2 | transformer tutorial, "will not run until correct" | **fix** | running is an observation, not a check. A transformer with a wrong mask or scaling still runs. The bullet teaches "it runs, so it is right", which the check definition and the L4 codebase example both contradict | 0.6 |
| 2 | 40-field form, validates each section | **fix** | validation checks format and completeness, not whether the entries are right. Content would then be self-checked against one's documents, which is L3 | 0.4 |
| 3 | introduction of a paper | keep | re-reading is easy, elected | — |
| 3 | summarise a 60-page report | keep | comparing against the source is easy, elected | — |
| 3 | patent claims, no examiner | **replace** | all three L3 bullets are writing-from-a-source. The brief asks for varied domains. Patent drafting is also the most specialist bullet in the file (D5) and loads knowledge | 0.45 |
| 4 | ledger across twelve monthly statements | **fix** | twelve statements give twelve closing balances, a ready-made monthly check. So "no visible sign until the final totals" is false, and the task reads as L2 or L3. Its stated reason, "checks the task never calls for", is the wrong criterion: L3 says naming a check does not matter. 49 words | 0.65 |
| 4 | codebase with no test suite | **fix** | placement is right. The tail ("can only be established through tests and probes the agent devises for itself") restates the L4 statement. It is a gloss and a surface cue. 49 words | 0.45 |
| 4 | legal contract with supplied glossary | **fix** | the tail is the same gloss pattern. Also, if the supplied glossary covered the term, checking against it would be a ready-made L3 check. "General glossary" plus "a term the contract defines for itself" removes that reading | 0.4 |
| 5 | Mars landing from the control room | keep | open-loop; r63 A2 (probe 12 light-minutes away) measured 5/5/5 | — |
| 5 | synthesis with no intermediate assay | keep | measured in r63 (A3 = 5). Confirming reagents is an input, not a check | — |
| 5 | sealed nine-month fermentation | **fix** | as written, the actions are "temperature and timing held to the schedule". Under r63 and your E2 = 3, holding a schedule a thermometer can confirm is a check, so the bullet reads as mid-scale. The fix says what each action is for: moving the culture on, which nothing shows | 0.5 |

As a set, all three L4 bullets ended with the same move ("only checks the agent sets up can catch it"). That
repeats the level text and teaches a phrase. The fixes remove it from all three.

## Proposed wordings

**L0, drop:** "Say whether checkmate can be delivered in one move in a given chess position."

**L2, transformer tutorial (fix):**
> Follow a course notebook to implement a small transformer network, where each of its five stages is marked
> automatically and the next stage opens only once it passes.

Automatic marking settles each stage. It arrives at every stage whether or not the agent looks. So L2.

**L2, form (fix):**
> Complete a 40-field online tax return whose figures are checked against the tax office's own records each
> time a section is submitted.

The section check now settles whether the entries are right, not just well-formed. It comes every few fields. So L2.

**L3, patent claims (replace):**
> Tile a bathroom wall with a spirit level and tape measure to hand, and nobody to inspect the rows until the wall
> is grouted.

Nothing outside checks the work. An adequate check is easy and ready to hand, but the tiler must choose to use it.
So L3. Not writing, low on PLp and PLs.

**L4, ledger (fix, same domain):**
> Keep a small business's books by hand for a year, following the given procedure. An entry posted to the wrong
> expense account does not upset the monthly bank reconciliation, and shows only as an odd figure in the year-end
> accounts.

The ready-made check (bank reconciliation) passes despite the error. The error is silent where it occurs and shows
far from its cause. A review of each account's movements would catch it, so a check can be built. So L4, not 5.
"Following the given procedure" keeps the r34 neutraliser against PLp.

**L4, codebase (fix, trim):**
> Add a feature, specified in advance, to a large codebase that has no test suite. A subtle bug surfaces only much
> later, deep in components built on top of it.

No ready-made check, silent error, symptom far from cause. Tests can obviously be written, so L4, not 5. The PLp
neutraliser ("specified in advance") is kept.

**L4, translation (fix, trim):**
> Translate a long legal contract using the supplied general glossary and brief. A term the contract defines for
> itself, mistranslated early on, reads naturally in every later clause that uses it.

Re-reading each clause shows nothing, and the glossary does not cover the term. A term list or back-translation
can be built. So L4. The r34 neutraliser (glossary and brief supplied) is kept.

**L5, fermentation (fix):**
> Run a nine-month fermentation in a sealed vessel that cannot be opened or sampled without spoiling the batch.
> Each scheduled change of temperature is meant to move the culture on a stage, and whether it did is unknowable
> until the end.

Each action is for the culture's state, which nothing reveals and no probe can reach. The thermometer confirms an
input only, as in the r63 synthesis reading. So L5.

## Style numbers

| | bullets | mean words | max words | em dash | semicolon |
|---|---|---|---|---|---|
| current | 20 | 24.6 | 49 | 0 | 0 |
| candidate | 19 | 24.5 | 41 | 0 | 0 |
| v1 reference | ~19 per file | 25.9 | — | 0.2 | 0.2 |

Per level, current → candidate: L0 4 → 3, L1 4, L2 3, L3 3, L4 3, L5 3.

Mechanical checks done:
- The candidate equals the current file on every non-bullet line (diff of non-bullet lines is empty).
- No new bullet shares a word 4-gram with any bullet in the other v2 rubrics or with a battery-v1 item.

## Open questions for you

1. **Winning-move gloss (flagged, not changed).** Your bullet ends "All the difficulty is in finding it, and the
   execution is a single act." That is a rationale gloss. Trim it to "Find the winning move in a given chess
   position."? If you would rather keep the checkmate bullet instead, swap the drop.
2. **L3 replacement: tiling or a coding task?** L3 is where the SWE items sit (swe-0090, swe-0461, r59 A1, all 3).
   A bullet such as "Fix a reported bug in a repository, given a script that reproduces it and a test suite that
   can be run at any time" would help annotators most. I chose tiling because a near-copy of the benchmark's own
   shape would make SWE relabels partly measure recall of the example. Your call.
3. **Three L4 bullets lose their rationale tails.** They were measured with the tails (r34 placement 77/77; r59 A4
   verbatim). Without them a judge might drift to 3 (codebase: "just run it") or to 5 (translation: "no check
   exists"). This needs a placement round before adoption.
4. **Fermentation rests on the r63 input-vs-outcome line.** That line is correct but fine (D5). If you think it is
   too fine for an annotator, the alternative is a third open-loop domain instead of a reword.
5. **Your E1 = 1 (hand-copy, source sealed).** If you read "compare each copied record with the source" as a per-
   action check, a reader could argue the new ledger bullet is lower than 4, since postings can be compared with
   statements. I placed it at 4 because the error is a wrong account, which the source does not show. Worth a
   sentence from you.
6. **Testing.** Six bullets fixed, one replaced, one dropped. Suggested: a placement round on the seven new
   bullets as blind items against the stripped candidate, plus the r39 minimal pair (L2forced / L3elected) and
   r63 A1–A4 as regressions, three judges, sealed predictions, 4-gram independence at seal time.
