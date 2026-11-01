# MSc Level 4 note — pre-registration

To be committed and pushed before any label of this study. Pablo's go: 2026-10-14 ("Pre-register and run the lab
regression for the Level 4 note, plus minimal pairs and fresh human items. Don't change the rubric until it passes.").

**Question.** Does a note that ties MSc Level 4 to sustained opposition fix the M04 case without breaking the lab's
results?

**Why.** On 2026-10-14 Pablo labelled six real tasks on MSc (worksheets/ms-human-2026-10-12). He put tau2-airline 0
at 2; the judge puts it at 4, the same in three runs. The customer pursues an outcome of their own, so the current
text says 4. But they object once and then give up. MSc's driver is how much of what must be said is set by the
other party, and a lone objection sets little of it. Level 4 is assigned by the kind of counterpart, not by how much
of the exchange they shape.

**The candidate** (`MSc_candidate.txt`): today's `MSc.txt` (sha256 `14b5e836…`) plus two sentences after Level 4's
Note:

> Importantly, the other party must keep pushing, so that move after move answers theirs. A single objection,
> answered once and then dropped, determines little of what is said, and belongs at the level the rest of the
> exchange calls for.

No example and no other level changes. **The rubric file in `src/` does not change in this study.** If the candidate
passes, adopting it is Pablo's decision.

## Design

- **Arms.** Every item is judged twice: with the current text and with the candidate. Same day, same prompt
  (`build_annotation_prompt_v2`), same judge (`adele-judge-v2-low`, Opus 5.5 at effort low, relayed by
  `judge-dispatcher-v2-low`), three repeats. The label is the lower median of the counted labels.
- **Why both arms.** The 2026-10-02 lab regression used an older MSc text: the examples review of 2026-10-04 changed
  it. So it cannot serve as a baseline. The current arm also re-runs the lab regression on today's text.
- **Blinding.** Opaque, shuffled file ids; both arms mixed in every relay.
- **Writers.** As in `../ms-lab-regression/`: only answers written by `claude-opus-5-5` count. Others are set aside and
  retried once.
- **Calls.** 126 items × 2 arms × 3 repeats = **756 calls** in pass 1 (`msc-l4-1`), plus pass 2.

## Items (`items.csv`, built by `make_prompts.py`)

| set | items | what | rule |
|---|---|---|---|
| R | 95 judged (+7 aliases, 3 void) | every MSc item of the MS lab regression, rebuilt from today's catalog: P (20), F (35), S (10), L (17 + r70's 7 human aliases), B (13) | R |
| M | 16 | eight minimal pairs written for this study (`pairs.csv`) | M1, M2 |
| H-fresh | 10 | real tau2 tasks, drawn once with a fixed seed: released MSc 4 (4 items), 3 (3), 2 (3); texts of at most 1,000 characters; none of the worksheet's | H1, H2 |
| H-dev | 5 | the five tau2 tasks Pablo labelled on 2026-10-14 (worksheet M01, M02, M04, M06, M07) | reported only |

**Minimal pairs.** Each pair has one scenario in which the other party pursues an outcome the solver must refuse.
- **A:** they object once, are answered, and let it go.
- **B:** they keep pressing, with a new argument after each reply.

Topic, policy, stakes and parties are the same in both versions. Four pairs are customer-service or helpdesk agents
bound by a policy (the tau2 shape). Four are everyday exchanges. No pair item shares a word 4-gram with an MSc example
or with the note.

**Human items.** Pablo labels H-fresh blind in chat, from the same summary of MSc's driver and levels he used on
2026-10-14. That summary describes the current text. He has seen the note, so he is not blind to the candidate.
His labels go to `human_labels.csv` (ids and levels only). The dev items carry his labels of 2026-10-14
(4, 2, 2, 2, 4). The candidate was drafted to fit them, so they are not evidence.

## Rules (`analysis/analyse.py`)

- **R (no regression).** Every MSc check of `../ms-lab-regression/` that holds under the current text also holds under
  the candidate. The checks are: P-MSc placement, F-on-MSc no leak, r30 pairs, r36 pair, r75 ladder, r70 human labels,
  B MSc high, mid-band and anchors. A check that holds only under the current text goes to pass 2. Its items are
  judged again in both arms (`msc-l4-2`). The failure is confirmed if the candidate still fails with the pass-2 labels.
  A check that fails under both texts is reported, not ruled.
- **M1.** Candidate: B at 4 or more on at least 7 of 8 pairs.
- **M2.** Candidate: A below B on at least 6 of 8 pairs.
- **H1.** Fresh items: the candidate matches Pablo exactly at least as often as the current text does.
- **H2.** Fresh items: no item is two or more levels from Pablo under the candidate while within one under the current text.

**Verdict.** The candidate passes if R, M1, M2, H1 and H2 all hold. Then Pablo decides whether to adopt it. Adoption
means editing `MSc.txt`, a provenance entry and a relabel of MSc on the released sets.

**Also reported:**
- the current arm against the lab targets (the first full regression of today's MSc text);
- R items whose label changes between arms;
- in the current arm, how many pairs have A equal to B;
- the dev items under both arms.

## Predictions (sealed)

| | p |
|---|---|
| R holds (no confirmed candidate-only failure) | 0.8 |
| M1 | 0.8 |
| M2 | 0.75 |
| current arm: A equals B on at least 4 of 8 pairs | 0.6 |
| H1 | 0.65 |
| H2 | 0.85 |
| the candidate passes overall | 0.45 |
| fresh items: the candidate moves at least 2 of the 4 released-4 items down | 0.5 |
| the current arm passes every MSc lab check except the r36 pair | 0.6 |

## Caveats

- Ten fresh items is a small human test. H1 can pass or fail on one item.
- Pablo is not blind to the candidate.
- The minimal pairs are written by the same author as the candidate. They test whether the text works as intended,
  not whether the intent is right.
- tau2 texts are the simulated user's script. The judge sees how the customer will behave; the agent does not.
- The r36 pair failed under the 2026-10-02 text (a rebuilt item). It is expected to fail under both arms here.

## Cost

756 Opus-low calls, plus up to about 60 in pass 2. Past runs: about 0.04% of a 5-hour window per call, so about 30%
of a window and 5–6 weekly points.

## Amendment 1 (2026-10-14, after the results): the C check

**Context.** The candidate failed because battery M01 says nothing about how the colleague will respond, and the
note read that silence as low demand. Two ways forward were considered:
- **Rule B:** state the behaviour if the task gives it; otherwise assume the party pursues its aim.
- **Skipping** tasks with too little information.

Pablo ruled (2026-10-14):
- **Keep a level for every task, plus an "underspecified" flag.** No skipping. Analyses run with and without
  flagged tasks. The first flag is free: cells whose three repeats disagree.
- **Run a cheap check first.** Does the current text already treat unstated behaviour as contested?

**Rule B is shelved, not run.** It is built as `MSc_candidate_b.txt`, `make_prompts_b.py`, `analysis/analyse_b.py`,
`human_items_b.csv` and `human_labels_b.csv` (510 calls).

**The C check.** `pairs_c.csv` holds each pair's shared scenario, with nothing on how the other party responds. The
8 C items are judged under the current text, with three repeats, in run `msc-l4c-1` (24 calls, `make_prompts_c.py`).
No C item shares a 4-gram with an MSc example, the note or rule B.

**Rule.** Count the C items whose median is 4 or more:
- 6 or more of 8: the current text already applies rule B. Keep it, and add the flag.
- 3 or fewer: it does not. An explicit clause is worth testing.
- 4 or 5: mixed. Pablo decides.

Also reported: A below C, using A's current labels from `msc-l4-1`.

**Prediction (sealed).** At least 6 of 8 C items at 4 or more: 0.6.

**Labels after calibration.** Pablo discussed his labels with Claude after the results. He mostly accepts three
revisions: H-02 to 4, H-06 to 4, H-07 to 2. His blind labels stay in `human_labels.csv` as pre-registered. Revised
labels, once he confirms them, go in a separate column and are reported only.
