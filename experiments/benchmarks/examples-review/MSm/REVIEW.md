# MSm examples review (draft for Pablo, 2026-10-04)

Every example bullet of the current `data_v2/Paolo_Pablo/MSm.txt` (19), checked against the rubric's own
clauses and against `data_v1/MSm.txt`. Nothing here has been judged. Confidence is how sure I am that the
problem is real.

You said you would not change MSm further, so the bar here is high. A bullet changes only if it is clearly wrong
under a clause or clearly fails a desideratum. v1 bullets stay unless they contradict a v2 carve-out. Bullets
that encode a recorded ruling are flagged, not changed.

## Where the v2 bullets come from

- Levels 0, 1, 3 and 4: all twelve bullets are byte-identical to v1.
- Level 2: two v1 bullets kept. The knights-and-knaves bullet was replaced by the dog bullet (provenance,
  2026-08-20, with the routing note now under Level 2).
- Level 5: two v1 bullets kept. The negotiation bullet's last clause was rewritten for the interlock re-key. The
  seller bullet is new and illustrates the dyadic route (provenance, 2026-08-20; r60, r69).

## Verdicts

| level | example (short) | origin | verdict | why | confidence |
|---|---|---|---|---|---|
| 0 | Sudoku | v1 | keep | no agent | — |
| 0 | dishwasher manual | v1 | keep | no agent | — |
| 0 | reading with others present | v1 | keep | others present but not needed, per the level text | — |
| 1 | mimicking gestures | v1 | keep | imitation, named by the level | — |
| 1 | following gaze to the keys | v1 | keep | detection and joint attention, no attribution | — |
| 1 | copying vending-machine buttons | v1 | keep | imitation | — |
| 2 | rock and coconut | v1 | keep | goal read off the action. Sits near Level 3's "want a glass of water", but v1 places it here and no carve-out touches it | — |
| 2 | scrunched nose, spoiled milk | v1 | keep | response tied to its stimulus | — |
| 2 | dog, thunder and fireworks | v2, ruling | keep | stimulus-response association, generalised. Encodes the knights-and-knaves replacement | — |
| 3 | friend's new job | v1 | keep | attributes a knowledge state. MSc at most 1 (one-way news) | — |
| 3 | hide-and-seek | v1 | keep | attributes where the seeker will look | — |
| 3 | checking the watch | v1 | keep | attributes a desire | — |
| 4 | Sally and Anne | v1 | keep | first-order false belief. Consistent with the L5 clause that pins a single belief-about-a-belief at 4 | — |
| 4 | own reaction vs friend's feeling | v1 | keep | self-other distinction, named by the level | — |
| 4 | manager's spelling mistake | v1 | keep | emotional state and personality inferred, not stated, so the stated-stance carve-out does not apply. Choosing silence is not steering, so MSc stays low | — |
| 5 | romance novel, dinner party | v1 | keep | the quoted chain interlocks: Steve's disbelief turns on his reading of Jane's motive, which turns on what she saw. Long (60 words) and has an "e.g." gloss, but both are v1 | — |
| 5 | team misreading | v1 | **flag** | "and managing the situation" adds a steering task (MSc about 3, as a mediation). The v2 carve-out says steering does not raise MSm. Also, once the misreading is described, the core is one belief about another's intention, which the L5 text pins at 4. v1 bullet, so not changed | 0.5 |
| 5 | multi-stakeholder negotiation | v1, edited in v2 | **fix** | "Leading a negotiation" is steering across parties in conflict. That is MSc's Level 5 construct, and MSc's own L5 anchors are negotiations of this kind (treaty chair, custody). The "does not cover" paragraph says steering does not raise MSm. The L5 placement rests only on the last clause, which is modelling. One word changes | 0.6 |
| 5 | seller's "final offer" | v2, ruling | **flag** | encodes the dyadic L5 route (r69). Three problems: a gloss sentence ("Only two parties are involved, and ... can each be settled only through the other two"), 69 words against v1's mean of 26, and "knows" used both for a stated fact and for the hidden variable. r60's paraphrase split 5/5/4, so it is also the hardest case in the file. r69 flagged its last phrase as a diagnostic cue. Not changed, per the brief | 0.7 |

## Changed bullet

**Level 5, negotiation.** One word: "Leading" becomes "Understanding".

> Understanding a negotiation between multiple stakeholders where each party has different beliefs about others'
> intentions and bottom lines, and what any one party will concede can only be worked out through what they
> believe the others believe.

Placement: what each party concedes depends on their belief about the others' beliefs, for several parties at
once. That is at least three attributions constraining one another, so Level 5. No one is steered, so MSc is 0.
"Understanding" was chosen over "Predicting the outcome", which would invite a Simulating reading.

## Style numbers

| | bullets | mean words | max words |
|---|---|---|---|
| current | 19 | 22.9 | 69 |
| candidate | 19 | 22.9 | 69 |
| v1 reference (18 files) | 18.6 per file | 25.9 | — |

Per level: 3, 3, 3, 3, 3, 4. The one bullet above 45 words that is not v1 is the flagged seller bullet.

Mechanical check: the candidate equals the current file on every non-bullet line. The only diff is line 41.

## Open questions for Pablo

1. **The negotiation fix (L5).** Do you accept the one-word change? It is the only MSm bullet that names a
   steering task as its activity, and it mirrors MSc's own L5 anchors. If you prefer to treat multi-party
   negotiation as an accepted MSm/MSc co-load (r30 and r31 found such tasks genuinely load both), keep it as is.
2. **The team bullet (L5), flagged.** If you want it cleaner, the smallest fix deletes the steering clause:
   > Appreciating the behaviour of individuals within a work team in which one employee has misinterpreted
   > another's actions as deliberately unhelpful, which has created tension that affects the whole group's
   > dynamics.

   This removes the MSc load. It does not settle whether the bullet still reaches 5 under the interlock rule. That
   depends on whether the misreading must be worked out or is given. I would leave it as v1 unless the MSc overlap
   matters to you.
3. **The seller bullet (L5), flagged.** It encodes the dyadic route you approved. If you want it in v1 shape, a
   46-word version without the gloss that keeps three interlocking attributions (her real limit, what she thinks
   he already suspects, what she wants him to conclude):
   > Working out, from a described exchange, whether a seller's "final offer" is a bluff, when she knows the buyer
   > has another option and words each reply by what she thinks he already suspects and what she wants him to
   > conclude about how far she can go.

   Any change here needs re-measuring. JUDGING.md rule 2 says examples move the top band by up to three levels,
   and r69's 5/5/5 was scored with the current wording present.
4. **No human label on any MSm item** (provenance, r69 note). Unchanged by this review.

Nothing else in MSm fails. Levels 0 to 4 are v1 bullets that no v2 carve-out contradicts, plus the ruling-based
dog bullet, which is accurate.
