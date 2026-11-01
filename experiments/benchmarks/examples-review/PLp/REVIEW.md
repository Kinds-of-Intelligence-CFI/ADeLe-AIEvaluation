# PLp examples review (draft for Pablo, 2026-10-04)

Text reviewed: `src/adele/rubrics/data_v2/Paolo_Pablo/PLp.txt` as adopted on 2026-10-01 (candidate O,
sha256 322674ef…). 23 example bullets. Reading only: no judge calls.

Each bullet was placed against the O driver: the search left for someone with the knowledge the task calls for,
who builds the plan step by step, takes the option that looks best and fixes slips as they show. The odds anchors
decide (Level 1 never undone; 2 hardly ever; 3 between one in two and one in a hundred, undoing a few steps back;
4 under one in a hundred, undoing far back; 5 no knowledge structures the search). The scope clauses applied:
only choices that could go wrong count; answer format adds nothing; knowing how tasks of a kind are done is
knowledge, not planning; execution and noticing a needed revision are out of scope.

Stripped placement below means the lab-regression result under O, one example per call with all examples
stripped (`plp-candidate/lab-regression/results/regression_o.json`, Opus low × 3, median). In production the
examples are shown, so a stripped miss says what the level text alone does not carry.

Confidence is how sure I am that the problem is real.

## Verdicts

| level | example (short) | verdict | why | stripped | confidence |
|---|---|---|---|---|---|
| 0 | Darwin year, four options | keep | a single retrieval; the format clause says the options add nothing | 0 | — |
| 0 | 38 °C to °F | keep | one computation, nothing to choose. Stripped reads 1, a 0/1 hairline, but the level text names a single action | 1 | — |
| 0 | one legal continuation left | keep | the partway clause: the remaining work is a single forced action | 0 | — |
| 0 | real-time translation | **fix** | "Implement" reads as building a translation system, which is an engineering task with real plan search. The original gloss ("the difficulty is linguistic") shows the intent was doing the translating. Stripped it reads 3 | 3 | 0.7 |
| 0 | 200-step protocol as written | keep | the plan is given; volume adds nothing | 0 | — |
| 1 | reply from a 60-page manual | keep | one routine, look up and reply; the page count is volume only | 1 | — |
| 1 | email summarising meeting notes | keep | one routine, never undone. See open question 5 on domain variety | 1 | — |
| 1 | covering letter | **flag** | the accepted loss recorded on 2026-10-01. The placement is right under the text (one genre routine, sensible defaults that never need undoing), but judges tip it to 2. Not changed | 2 | — |
| 1 | Tower of Hanoi, 255 moves | **flag** | placement right: the recursive routine fixes every move. But the second sentence ("so nothing has to be searched for") is a rationale gloss, which the style rule forbids. It came in with O's adoption, so not changed | 1 | 0.5 |
| 2 | one city day, 3 museums, 2 restaurants | keep | a slip (a museum closed on arrival) shows at once and is fixed by swapping; hardly ever undone | 2 | — |
| 2 | personal webpage from a template | keep | three standard steps, slips are local. The steps are listed in the task, which leans towards Level 1; not enough to change | 2 | 0.3 |
| 2 | 40,000-row data analysis | **fix** | "this standard pipeline" says one routine covers the whole task, which is the Level 1 statement, against Level 2's "no single routine covers the whole of it" | 2 | 0.45 |
| 3 | four cities, two visas, conference day 9 | **fix** | with no departure date, the visa time does not bind: apply now and order the cities freely, so the interaction need not change the plan. Adding the departure date makes it bind | 3 | 0.5 |
| 3 | club-level chess middlegame | keep | your accepted PLp/PLs co-load (close-out ruling); a natural move can lose four moves deep, undoing a few steps back | 3 | — |
| 3 | contest problem, several techniques | **fix** | placement right. The closing clause "so the options must be compared before committing" restates the Level 3 statement word for word: a rationale gloss and a surface cue | 3 | 0.5 |
| 3 | sliding block, four moves from solved | keep | adopted with O. The natural move blocks the only way out, so the greedy plan is undone a few steps back | 3 | — |
| 4 | ML paper replication, key details omitted | **flag** | reads 3 stripped since r25. Replication has a fairly standard decomposition (implement, sanity-check, compare to the reported numbers), so by the knowledge carve a reader may put it at 3. The odds would need several omitted details that interact and fail late. Construct question, not changed | 3 | 0.45 |
| 4 | contest problem, no standard technique | keep | the key idea must be found; without it the step-by-step plan almost never works, and the undoing reaches back to the approach itself | 4 | — |
| 4 | first ascent of an unclimbed face | **fix** | 63 words, the longest bullet in the file (v1 mostly 10–45). Also "candidate lines mostly turn out to be impassable" gives odds of perhaps one in a few, which is Level 3 by the anchor; "almost every line" matches Level 4. Drops one of four "fail only once worked through" phrasings | 4 | 0.55 |
| 4 | twelve exams, five slots | **flag** | adopted with O and placed at 4. Two concerns. Exam timetabling is graph colouring, with established heuristics (most-constrained exam first), so the knowledge carve may put it at 3 for a 12-exam instance. And its second sentence restates the Level 4 odds anchor ("almost no timetable built slot by slot comes out valid"), which stipulates the placement rather than showing it | 4 | 0.4 |
| 5 | synthesis route, unsynthesised natural product | **flag** | reads 4 stripped since r25. Retrosynthetic analysis is an established procedure, so the Level 5 note ("where … the kind of work is itself established, the task belongs at the level below") points to 4. Not a recorded ruling, but the fix is a construct call (see open question 3) | 4 | 0.6 |
| 5 | proof strategy, open conjecture | keep | the known methods have failed by definition, so no knowledge structures the search; the clean Level 5 case | 5 | — |
| 5 | multi-year research programme | **fix** | its difficulty sat in the execution ("lines of attack die only once explored", "which to abandon"), while the bullet says the programme is only written. Noticing on the way that a plan needs revision is out of scope. The fix states what makes it Level 5: every known line has failed, so no knowledge structures the search | 4 | 0.45 |

Also, as a set: four bullets carried a "fails only once explored / worked through" phrasing (L4 contest, L4
ascent, L4 timetabling, L5 programme), echoing the Level 4 statement. That teaches a cue. The two fixes cut it
to two (contest, timetabling).

## Proposed wordings

- **Level 0, translation.**
  > Interpret a conversation between English and Spanish in real time, translating each turn accurately as it is spoken.

  Each turn is translated as it comes, in the speakers' order. Nothing is chosen that a plan could get wrong. Level 0.

- **Level 2, data analysis** (drop "of this standard pipeline").
  > Plan a small data analysis by downloading a 40,000-row dataset, cleaning it, running a statistical analysis and producing a chart. The stages do not constrain each other.

  Several standard stages, no single routine for the whole, slips fixed where they occur. Level 2.

- **Level 3, trip** (add the departure date).
  > Plan a trip through four cities, leaving in two weeks, where two require visas that take up to three weeks, and a conference on the ninth day cannot be moved. Nothing is reserved, and the deliverable is the itinerary.

  The visa cities cannot be entered before about day 7, and day 9 is fixed. Ordering the cities by route alone
  often has to be undone a few steps back. Between one in two and one in a hundred. Level 3.

- **Level 3, contest problem** (drop the gloss).
  > Solve a contest programming problem in which several standard techniques could apply. The data structure settled on early decides whether the later queries can be answered in time.

  Known options; an early choice can fail several steps later, and the undoing reaches back to it. Level 3.

- **Level 4, first ascent** (63 → 45 words).
  > Plan the first ascent of an unclimbed face. The line, the camp sites and the loads all depend on one another, and almost every line that looks good from the valley dead-ends high on the face. The deliverable is the route plan, not the climb.

  Mountaineering is an established kind of work, but no route exists to supply the decomposition. Almost every
  first choice fails late, and the undoing reaches back to the line. Under one in a hundred. Level 4 (the Level 5
  note keeps it below 5).

- **Level 5, research programme.**
  > Plan a multi-year research programme against an unsolved scientific problem on which every known line of attack has failed, and no one yet knows which sub-questions are worth posing. The programme is written as a proposal rather than carried out.

  No established procedure or knowledge structures the search. Level 5.

## Style numbers

| | bullets | mean words | max words | em dash / semicolon / parenthesis |
|---|---|---|---|---|
| v1 (18 files) | 18.6 per file | 25.9 | most 10–45 | 0.2 / 0.2 / — |
| current PLp | 23 | 25.3 | 63 | 0 / 0 / 0 |
| candidate PLp | 23 | 24.5 | 45 | 0 / 0 / 0 |

Per level: 5 / 4 / 3 / 4 / 4 / 3, unchanged. The candidate equals the current file except six bullet lines
(checked mechanically: same line count, every differing line starts with "* ").

## Open questions for Pablo

1. **Covering letter (Level 1).** Flagged only, per your 2026-10-01 acceptance. My reading: the placement is right
   under O. Nothing in the bullet needs fixing; it is a judge lean.
2. **Hanoi and timetabling (O's new examples).** Both carry a closing sentence that states why the level holds.
   Hanoi's is harmless but breaks the no-gloss rule. Timetabling's restates the Level 4 odds anchor and may teach
   it as a phrase. A possible trim, if you want one: "Timetable twelve exams into five slots under stated clashes
   and room limits, where the clashes leave room for very few valid timetables." Separately, is a 12-exam
   timetable Level 4 for someone who knows graph-colouring heuristics? I would put it at 3 unless the clashes are
   tight.
3. **Level 5 versus its own note.** The note says a task is Level 5 only where no established procedure exists at
   all. Synthesis has one (retrosynthesis); so, loosely, does proving theorems. Read strictly, the note empties
   Level 5 (close-out item 3). Options: (a) move synthesis to Level 4 and find another Level 5 bullet; (b) reword
   it so the key step has no known reaction ("whose core ring system no known reaction can form"), which then
   mirrors the Level 4 contest bullet; (c) keep it and read "established procedure" as one that structures this
   search. I did not change it because the choice is a construct call.
4. **ML replication (Level 4).** Reads 3 stripped since r25. If you want it firmly at 4, name the interacting
   unknowns, for example: "omits the reward scaling, the initialisation and the evaluation protocol, and most
   combinations of plausible guesses fail to learn at all". Not changed.
5. **Domain variety at Level 1.** Three of four bullets are writing tasks (manual reply, meeting email, covering
   letter). Swapping the email for another domain would vary it, but the email is a stable Level 1 anchor next to
   the weak covering letter. I kept it.
6. **Re-measuring.** All six fixes touch bullets in the lab's placement set P (translation, data analysis,
   trip, contest, ascent, programme are P-L0-4, P-L2-3, P-L3-1, P-L3-3, P-L4-3, P-L5-3). If you adopt them,
   rerun set P on the candidate (23 bullets × 3, about 70 calls, Opus low) and check that the translation drops from 3
   and the programme rises to 5 without anything else moving. Check item independence (4-grams) if any lab item
   reuses the new wording.
