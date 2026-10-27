# MMp (Long-term procedural memory) examples review (draft for Pablo, 2026-10-04)

Source: `src/adele/rubrics/data_v2/Marko/MMp.txt` (Marko). No provenance file, never lab-tested. So the bar here
is conservative: fix only clear problems. Nothing has been judged. Confidence is how sure I am that a problem is real.

MMp's driver, from its own text: the structure of the learned procedure that must be recalled. L1 one or two steps,
L2 a fixed sequence of 3–5 steps, L3 a longer or branching sequence, L4 hierarchical or cue-switching sub-routines
and nested loops, L5 schemas that adapt to probabilistic cues and novel contexts over many sub-goals.

## Verdicts

| level | example (short) | verdict | why | confidence |
|---|---|---|---|---|
| 0 | capital of Japan | keep | a fact | — |
| 0 | water liquid at 25 °C | keep | a single judgment | — |
| 0 | define photosynthesis | keep | a fact | — |
| 1 | describe logging in to a website | keep | over-learned. It is about three steps, a little over L1's "one or two", but intuitive | — |
| 1 | bold a word in Markdown | keep | one step | — |
| 1 | passive voice of a short sentence | keep | over-learned rule | — |
| 2 | Markdown table, with the steps listed | **fix** | the task spells out the steps (header, separator, two rows), so the procedure is given rather than recalled. Reads as a gloss of "3–5 ordered actions" | 0.5 |
| 2 | APA 7th reference | keep | short fixed sequence | — |
| 2 | set a digital clock | keep | short fixed sequence | — |
| 3 | long multiplication with partial products | keep | longer sequence, errors propagate. QLq co-load is low | — |
| 3 | Euclid's algorithm on 42 and 70 | keep | a short loop with a stop condition | — |
| 3 | Git init, add, commit, remote, push | **replace** | five linear commands with no branch. That is L2's "short, fixed sequence of 3–5 ordered actions with minimal branching" exactly | 0.65 |
| 4 | Cessna 172 pre-flight checklist in order | **replace** | a flat list recalled in order. No hierarchy, loop or cue switching, so L3 at most. It is also serial recall of a list that pilots read from a card, closer to declarative knowledge than to a practised procedure | 0.6 |
| 4 | 4×4 Rubik's last-layer corners "at competition speed" | **fix** | case recognition and switching fits L4. But a description cannot be given "at competition speed". The phrase invites a speed or execution reading | 0.4 |
| 4 | electrician replaces a three-phase distribution board | keep | coordinated sub-procedures with verification. Heavy domain knowledge, like the L5 set | — |
| 5 | Crew Dragon rendezvous and docking commands | **flag** | Dragon docks autonomously, with ground teams monitoring and giving go/no-go. "Mission-control commands" is loose but not wrong. Mostly tests specialist knowledge few people hold. See open question 1 | 0.4 |
| 5 | PWR startup from cold shutdown | keep | many sub-goals, monitored criticality | — |
| 5 | multi-extruder 3D-printer calibration | keep | many sub-goals, tuning loops that adapt to what is observed | — |

Counts: keep 13, fix 2, replace 2, drop 0, flag 1.

## Proposed wordings

- **L2, Markdown table:**
  > Write the Markdown for a table with two columns, a header row and two data rows.

  The solver must recall the header, separator and row syntax in order. A short fixed sequence, not given. L2.
- **L3, replaces Git init:**
  > Give the Git commands to rebase a feature branch onto the latest main, what to run if a conflict stops the rebase, and how to update the remote branch.

  A longer routine with a conditional branch (a conflict) and order dependence (the push must be forced after the
  rebase). L3. It is still a known routine, so PLp stays at 1.
- **L4, replaces the Cessna checklist:**
  > Describe the adult cardiac-arrest algorithm, switching between the shockable and non-shockable branches as the heart rhythm changes at each two-minute check.

  A repeating loop with cue-driven switching between two sub-routines. That is L4's "nested loops, or switching
  sub-routines based on cues". It is a drilled protocol, so recall rather than planning.
- **L4, Rubik's:**
  > Describe the hierarchical algorithm, case recognition and finger-trick sequence that solves all four last-layer corners on a 4×4 Rubik's Cube.

  Only "at competition speed" removed.

## Style numbers

| | count | mean words | max words |
|---|---|---|---|
| current | 18 | 17.3 | 33 |
| candidate | 18 | 16.7 | 33 |

v1: mean 25.6 words per bullet. No em dashes or semicolons in the bullets.
Minor, not changed: "Outline the complete" opens two L5 bullets, and "step by step" appears twice at L1.

## Disentanglement

- **PLp.** Every example asks for a known procedure, so PLp stays at 1 (retrieval) throughout. That is a clean
  separation: MMp high, PLp low. The Git and cardiac-arrest replacements keep this.
- **PLe.** All examples ask to describe or give a procedure, not to carry it out, so PLe stays low. PLe already
  routes "a routine run off by rote" away from itself.
- **MMs.** MMp L3 long multiplication is done on paper ("showing each partial product"). The MMs review puts mental
  four-digit multiplication at MMs L5. The pair separates the two rubrics well.
- **MMe.** None of the examples needs a specific past episode.
- **MSm, MSc, PLs.** No load.
- **Not a listed sibling, but large:** knowledge (v1 KN). From L3 up, every example is "describe the procedure for X",
  and the hard ones are hard mainly because few people know X (reactor startup, Dragon docking, three-phase boards).

## Problems in the level statements (not changed, reported only)

1. **Practice points both ways.** L1 asks for an "over-learned" routine. L2 asks for steps "not routinely
   practised". L5 asks for schemas "honed by extensive practice". So it is unclear whether practice lowers or raises
   the level. Desideratum 3.
2. **"Known or inferable" at L2.** Steps that are inferred are reasoning, not memory. A task whose steps can be
   worked out on the spot makes no procedural-memory demand by MMp's own preamble.
3. **"Recognising and extending a hidden stimulus sequence" at L4** is pattern induction. That is another construct
   (v1 reasoning dimensions), not recall of a practised routine.
4. **No "does not cover" paragraph.** Nothing separates (a) knowing that a procedure exists or what its steps are
   (knowledge) from having it automatised, (b) retrieving a routine as a plan (PLp L1), and (c) carrying it out
   (PLe). `docs/taxonomy-provenance.md` flags MMp vs PLe as never measured. PLe has a routing clause, MMp has no
   matching one.
5. **Text tasks.** The rubric is about automatised skill, often "executed implicitly". A text task can only ask for a
   description, which is declarative. The rubric does not say how to score "describe the procedure". So the scale
   may in practice track how specialised the knowledge is. This is probably the main validity risk.
6. Em dashes in the preamble and L4 (desideratum 7). Not changed.

## Open questions for Pablo

1. Point 5 above. Should "describe the procedure for X" score on MMp at all, or only tasks where a routine is run?
   If it should, the L4–L5 examples are fine. If not, most of the examples need rethinking, and that is Marko's call.
2. The Crew Dragon example (flagged). Keep it, or swap it for a task whose difficulty is the routine rather than rare
   knowledge? I left it.
3. In swebench-30, Sonnet and Opus agreed exactly on MMp for only 0.43 of the 30 tasks (κ 0.42, all within one).
   So judges already split on how much coding tasks load MMp (recalling Git, test or build routines). Point 5 may be
   part of the reason.
4. Marko should see these changes. None of them has been placed by a judge.
