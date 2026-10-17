# MSc and MSm candidates of 2026-10-17 — pre-registration

Drafted 2026-10-17 at Pablo's request. Approved by Pablo on 2026-10-17. Pushed before any label; prompts built (`make_prompts.py`, run `mscand-1`). See
amendment 1 for the order of work.

**Question.** Do the two candidates keep every lab result the current texts hold, and do they match Pablo's
agent-side labels on real tau2 tasks at least as well?

## The candidates (`make_candidates.py`)

Both are built from the current `src/` files. The script checks that nothing else differs. `src/` does not change here.

- **`MSc_candidate.txt`: one driver, in MSm's style.** The driver is what the task needs the other party to understand,
  accept or do. New intro (assesses / covers / ranges, as in MSm). New level statements, at most one marker each. One
  example reworded: the Level 4 refund example now states the stance the task needs ("…and keep them talking until they
  accept the store credit it does offer"). The "does not cover" paragraph and every other example are unchanged.
- **`MSm_candidate.txt`: back toward v1 MS.**
  1. The v1 intro is restored. The rewording of 2026-08-25 rested on a false claim: AS and QLq also open with "This
     criterion assesses".
  2. The "does not cover" Note gains the sincerity condition: a stated stance "does not have to be modelled unless the
     task gives reason to doubt it".
  3. The Level 4 stated-stance passage is removed, because the Note already says it. Level 4 is v1 word for word.

  Level 2 (truth-teller puzzles score 0) and Level 5 (the interlock rule) keep their v2 text. Both change labels and
  were tested.

## Design

- **Arms.** Every item is judged under the current text and under the candidate of its rubric, on the same day. The
  stored baselines cannot be reused: the examples review of 2026-10-04 changed both texts after the 2026-10-02
  regression, and msc-l4-1 (2026-10-14) covers MSc only.
- **Judge.** `adele-judge-v2-low` (Opus 5.5, effort low), relayed by `judge-dispatcher-v2-low`. For prompts too long
  for one Read call, `adele-judge-v2-low-chunked` instead. The v2 prompt with reasoning, as in every rubric round
  (production will be bare digit; the lab tests the text). Three repeats; the label is the lower median of the counted
  labels.
- **Blinding.** Opaque, shuffled file ids. Both arms are mixed in every relay.
- **Writers.** Only answers written by `claude-opus-5-5` count. Others are set aside and retried once
  (`writers.py --set-aside`).

## Items

| set | items | what | rule |
|---|---|---|---|
| R-MSc | 94 (+6 aliases, 5 void) | every MSc item of `../ms-lab-regression/`, rebuilt from today's catalog, as in msc-l4-note | R |
| R-MSm | 89 | every MSm item of `../ms-lab-regression/`, rebuilt the same way | R |
| M | 16 | msc-l4-note's eight minimal pairs (`../msc-l4-note/pairs.csv`), MSc only | M (open, see below) |
| H | 15 tau2 tasks × MSc and MSm | the agent-side worksheets (`~/Developer/ADELE/worksheets/tau2-agent-side-2026-10-17/`) | H1–H3 |

**Set P under the MSc candidate.** Each arm is placed on its own examples. The refund example is judged in its current
wording under the current text and in its new wording under the candidate.

**4-gram check.** Every item is checked against every example bullet of the text it is judged on, and against the new
candidate sentences. Written items with a shared 4-gram are void in both arms. Real tasks are reported only. Void at build: r30 S1 and S2
("will hear you out") and battery D08 ("bring them to accept"), as on 2026-10-02.

**Set H: two inputs.** Pablo labels from the worksheet, which shows the whole task. The judge is run on both inputs
so that the rubric and the input can be told apart:
- **script:** the frozen tau2 text, as released labels use it today;
- **full task:** the worksheet's parts 1 to 3, with the domain policy written in, and without the labels section. It
  opens with the worksheet's line on whose task is rated.

Pablo's labels go to `human_labels.csv` (ids, levels, his "enough information" mark, a note). He gives them before any
judge label of this study is shown to him. Items he marks "not enough information" leave rules H1 to H3, by his
ruling of 2026-10-17 (use only well-designed tasks). They are still reported.

**Calls.**

| part | calls |
|---|---|
| R-MSc: 94 × 2 arms × 3 | 564 |
| R-MSm: 89 × 2 arms × 3 | 534 |
| M: 16 × 2 arms × 3 | 96 |
| H: 15 × 2 rubrics × 2 arms × 2 inputs × 3 | 360 |
| **pass 1** | **1,560** (520 prompts) |

Pass 2 adds at most about 60.

## Rules (`analysis/analyse.py`)

- **R (no regression), per rubric.** Every check of `../ms-lab-regression/` that holds under the current text also
  holds under the candidate.
  - MSc: P-MSc placement, F-on-MSc no leak, r30 pairs, r36 pair, r75 ladder, r70 human labels, B MSc high, mid-band and
    anchors.
  - MSm: P-MSm placement, F-on-MSm no leak, r60 stated-stance carve, r60 anti-count guard, r60/r69 Level 4/5 boundary,
    B MSm low, B MSm on pure MSc items.

  A check that holds only under the current text goes to pass 2 (both arms, its items only). The loss is confirmed if
  the candidate still fails. A check that fails under both texts is reported, not ruled. F-on-MSm failed on 2026-10-02
  on two PLs Level 5 examples, and Pablo accepted that overlap; if it fails under both texts again, it is reported only.
- **M (minimal pairs), MSc candidate.** In every pair the solver refuses a request, and the task needs nothing from
  the other party. In A they object once and let it go. In B they keep pressing. Pablo's ruling (2026-10-17): only what
  the task needs counts; a persistent opponent whose acceptance the task does not need is not contested. So under the
  candidate, A and B are within one level of each other on at least 7 of 8 pairs, and B is at 3 or less on at least 7
  of 8. msc-l4-note's M1 and M2 encoded the opposite reading and are not used.
- **H1, per rubric (full-task input).** The candidate matches Pablo exactly at least as often as the current text does.
- **H2, per rubric (full-task input).** No item is two or more levels from Pablo under the candidate while within one
  under the current text.
- **H3, input (current text).** Full task matches Pablo exactly at least as often as script. Reported as a finding for
  the input decision; it does not decide the candidates.

MSm's H rules apply only if Pablo gives MSm labels on at least 10 items.

**Verdict, per candidate.** MSc passes if R, M and H1–H2 hold for MSc. MSm passes if R and H1–H2 (if they apply) hold
for MSm. Then Pablo decides on adoption: edit `src/`, a provenance entry, and a relabel of the released sets.

**Also reported:**
- every R item whose label changes between arms;
- set S (sibling cross-loading), descriptive;
- set H per item: level by rubric, arm and input; Pablo's label; his customer-side label of 2026-10-14 for comparison;
- the effect of the input under each arm;
- answers set aside, and how often all three repeats agree.

## Predictions (sealed)

| | p |
|---|---|
| MSc: P-MSc placement holds under the candidate | 0.7 |
| MSc: r75 ladder holds under the candidate | 0.35 |
| MSc: B MSc high holds under the candidate (X06R is the risk: three managers make demands, but the task never says it needs anything from them) | 0.5 |
| MSc: R holds (no confirmed loss) | 0.3 |
| MSm: r60 stated-stance carve holds (B2, the insincere price, relied on the removed Level 4 passage) | 0.7 |
| MSm: R holds | 0.55 |
| MSc: H1 holds | 0.6 |
| MSm: H1 holds (if it applies) | 0.6 |
| H3: full task at least as good as script | 0.6 |
| M holds | 0.6 |

## Caveats

- **Pablo has seen judge labels of 10 of the 15 tau2 items,** on the script input with the current MSc text. His
  earlier labels on them rated the customer's side. So H is a weak test of the current text and a fair one of the
  candidate.
- **Fifteen items cannot show a small effect.** H rules guard against a clear loss.
- **The full-task input is long** (policy about 7.7k characters plus records). The judge may handle it worse than a
  short text, whatever the rubric. H3 measures that.
- **The candidate changes the MSc construct on purpose.** Some lab targets were set under the old driver (r30's
  "resistance rises" pair, the r75 ladder). A loss there may be the intended change rather than a fault. Pass 2
  cannot tell these apart; Pablo rules on each confirmed loss.

## Cost

1,560 Opus-low calls plus pass 2. Earlier rounds used about 2 to 3 weekly points per 300 calls, so about 10 to 15
weekly points. Pablo's time: the 15 worksheets.

## Amendment 1 (2026-10-17, before any judging)

- **Order of work (Pablo: do everything that does not need him first).** All 520 prompts are judged now. Sets R and M
  are analysed at once (`analysis/analyse.py`). Set H stays sealed: `collect.py` writes its labels only to the gitignored
  `data/annotations/mscand-1/sealed_H.csv`, and nothing about them is read or shown until Pablo's labels are in
  `human_labels.csv`. If a candidate loses a lab check, its wording may be revised and re-tested (a new amendment and
  run) before Pablo labels, so that he labels the final text once.
- **Battery X06R leaves rule R** ("B MSc high"), reported only. Its task ("restore power… while three depot managers each
  demand their own area first") states nothing it needs from the managers. Under Pablo's ruling (only what the task
  needs counts) its registered MSc 5 belongs to the old construct. Claude's call, open to Pablo's veto.

## Amendment 2 (2026-10-17, after mscand-1 and mscand-2; set H still sealed)

**Pass-1 and pass-2 results that motivate it.** R holds for both candidates: the one MSc loss in pass 1 (r36 D2, 3)
was not confirmed in pass 2 (4). MSc v1 fails rule M: the persistent versions (B) score 4 on 8 of 8 pairs under both
texts. The judges read "an outcome that conflicts with what the task needs from them" as conflict with the task's
outcome (no refund), and cite the Level 4 refund example for every refusal.

**MSc v2 (`MSc_candidate_v2.txt`, built by `make_candidates.py`).** Two changes to v1, nothing else:
- Level 4: "The task requires someone to be brought round against their will. It cannot succeed unless they accept or
  do something they are working against, so each move must answer their counter-moves as they push back."
- The refund example: "Bring a customer who is shouting for a refund the policy does not allow to accept the store
  credit it does offer."

**Screen first (`make_screen.py`, run `mscand-s1`).** The 16 pair items under v2, three repeats, 48 calls. Rule M as
registered. If M holds, the full v2 run (R-MSc and set H on MSc, candidate arm only, against mscand-1's current arm)
follows after Pablo has seen the v2 wording. If M fails, v2 is dropped and Pablo decides on the next wording.
Caveat: the screen re-uses the eight pairs that showed the problem, so a pass is weaker evidence than a fresh test;
the full run's R checks guard against side effects.
