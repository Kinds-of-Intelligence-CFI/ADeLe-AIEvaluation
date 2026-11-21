# MSc examples review (draft for Pablo, 2026-10-04)

All 20 example bullets of `src/adele/rubrics/data_v2/Paolo_Pablo/MSc.txt`, checked against MSc's own clauses
under the shared brief (`../BRIEF.md`). No judge calls. Candidate file: `MSc_candidate.txt`.

Evidence used, besides the text:
- `ms-lab-regression` (2026-10-02): each bullet judged on MSc with every Examples block stripped (set P), and on MSm
  (set S). 19 of 20 exact, 20 within 1. The one miss: the market trader (L3) scored 4, 4, 4.
- `plp-candidate/lab-regression`: MSc examples judged on PLp. Level 5 examples score PLp 3. r34 accepted this
  co-load ("negotiation genuinely involves search over concession sequences").
- Human anchors: Pablo's r70 labels are on the r61/r75 items (eigenvalues, meter reading, witness statement, loft
  conversion, supplier lock-in, three unions, eight team leads). r61 records that no item appears in MSc, and r75's
  4-gram check found 0 hits against the bullets. **So no bullet encodes a human anchor.** The changed bullets share
  no 4-gram with the r75 item texts either.
- Recorded design decisions that bullets encode (kept): the column (expression carve, redesign §4.2), the doctor
  (stakes do not raise demand, redesign §2.2), the hostage neutraliser (r34).

## 1. Verdicts

| level | example (short) | verdict | why | confidence a problem is real |
|---|---|---|---|---|
| 0 | infinitely many primes | keep | logical work, no one's stance shaped | — |
| 0 | transcribe a lecture | keep | procedural | — |
| 0 | cheapest flights | keep | factual search | — |
| 1 | coffee and sandwich | keep | standard script | — |
| 1 | librarian, which shelf | keep | fact asked for and given | — |
| 1 | move a dental appointment | keep | request made and met | — |
| 1 | 1,100-word carbon-tax column | keep | one-way message plus the expression carve. Encodes the redesign's §4.2 fix | — |
| 2 | patient's history | keep | cooperative, next question set by the last answer | — |
| 2 | job candidate interview | **fix** | "rather than reading out fixed questions" contrasts with Level 1. It is a level gloss. It also adds a third paraphrase of the Level 2 driver | 0.5 |
| 2 | support chat, which product | **fix** | "each follow-up question depending on what they have just said" restates the level statement. Three L2 bullets now carry the same phrase, a surface cue. Make the adaptation come from the task | 0.55 |
| 3 | colleague's section rewritten | keep | open stance, "will hear you out". Merely displeased belongs below 4 (L4 Note) | — |
| 3 | doctor, serious illness | keep | stakes carve. Encodes a recorded design decision | — |
| 3 | two flatmates, cleaning rota | keep | two parties, compatible required positions ("both will accept whatever they come to see as fair"), so below 5 by the L5 Critically clause. Open to persuasion, so 3 | 0.2 |
| 3 | market trader | **move to L4 and fix** | a trader who opens far above your price is pursuing a different outcome. L3's Importantly clause says the exchange steers by doubts "rather than by anything they are trying to do". Haggling is the opposite. The closing clause "the work is finding the figure that suits you both" is a gloss added to hold it at 3. Measured: 4, 4, 4 with examples stripped | 0.75 |
| 4 | landlord, early lease release | keep | single counterpart pursuing a different outcome. PLp 2 to 3, accepted co-load (r34) | — |
| 4 | refusing a refund | keep | contested, counter-moves. "Shouting" could cue self-control, but the demand is steering ("without the exchange breaking down") | 0.15 |
| 4 | co-founder's launch date | keep | "staked their reputation on" makes them pursue an outcome. Near the L3 colleague, but measured 4, 4, 4 | 0.3 |
| 5 | hostage release | **fix (trim)** | last sentence "What is in question is what to say, to whom, and in what order" is a rationale gloss. "In what order" also invites PLp. 63 words, the file's longest. Keep the r34 neutraliser sentence | 0.5 |
| 5 | treaty, three red lines | keep | incompatible stated positions, chaired. PLp 3 accepted (r34) | — |
| 5 | custody | **fix** | "Settle" does not say who you are. If you are one parent, the opposition comes from a single counterpart, which the L4 Note places at 4. Only as a third party is it a cross-read conflict | 0.5 |

Counts: 14 kept, 5 fixed (one of them moved from L3 to L4), 0 replaced, 0 dropped, 0 flagged for a ruling.

## 2. Proposed wordings

**L2, job candidate**
> Interview a job candidate about a project on their CV, following up on what they actually say.

Cooperative party, and what to ask next comes from their answers: Level 2. Only the Level 1 contrast is removed.

**L2, support chat**
> Work out over a support chat which of six broadband plans suits a customer who is unsure how they use the internet at home.

The customer is helping but cannot state their need. So each question must build on the last answer: Level 2.
Nothing they want stands against the agent.

**L3 to L4, market trader**
> Agree a price with a market trader who opens far above what you will pay and gives ground only when you start to walk away.

The trader pursues a different outcome (a high price) and makes counter-moves. One counterpart: Level 4. Low
stakes, so it also shows that stakes do not raise the level. Level 3 keeps three bullets, Level 4 gets four.

**L5, hostage (trimmed)**
> Negotiate a hostage release in which the captor, the police commander pressing to storm the building, and the hostages' families each demand a different course, and each of them reads what is conceded to the others. The tactical plan for the operation is settled and not yours to make.

Incompatible demands, each read by the others: Level 5. The PLp neutraliser stays. 63 to 49 words.

**L5, custody**
> As mediator, settle the custody arrangement in a divorce where both parents want the child to live with them and each expects the other to exploit any concession.

Two parties whose demands cannot both hold, each reading what is conceded to the other, addressed by a third party:
Level 5.

## 3. Style numbers

| | bullets | mean words | max words |
|---|---|---|---|
| current | 20 | 22.0 | 63 (hostage) |
| candidate | 20 | 20.6 | 49 (hostage) |

v1 reference: mean about 26, most 10 to 45. No em dashes or semicolons in either file. Non-bullet lines are
identical (checked mechanically, 23 lines).

## 4. Open questions for Pablo

1. **The trader.** I move it to Level 4 rather than replace it. The alternative is to keep a fourth Level 3 bullet
   with a new open-stance case in another domain. Was the integrative-bargaining reading at 3 deliberate? r30 shows
   it was a conscious move up from the old "bargaining" at 2, but I find no ruling on it.
2. **MSm load of the top band.** MSc's Level 3 to 5 bullets score MSm 3 (Level 5: 4 to 5) even though the stances
   are stated. ms-lab-regression reads this as one-way and expected (steering needs modelling). I did not
   neutralise further: it would make the bullets artificial. Do you accept this co-load, as you did the PLs one on
   2026-10-02?
3. **PLp load of Level 5.** All three Level 5 bullets score PLp 3. r34 accepted it. I found no ruling of yours on
   it, only the round's note.
4. **Co-founder (L4) against colleague (L3).** Both are a colleague attached to their own work. They differ only by
   "will hear you out" against "staked their reputation on". It measures fine, so I kept it. A sharper version, if
   you want one: "...a launch date they have announced to investors and are pushing the team to meet."
5. **Re-measuring.** All five changed bullets are set-P items in ms-lab-regression. Three of them (trader, hostage,
   custody) are also set-S items there and set-F items in the PLp lab regression. Re-judging them would be 11 items
   (5 on MSc with examples stripped, 3 on MSm, 3 on PLp), 33 calls at three repeats. The trader's placement at 4 is
   already measured (4, 4, 4 under its current wording).
