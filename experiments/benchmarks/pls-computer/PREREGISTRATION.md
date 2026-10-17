# pls-computer — pre-registration

Committed and pushed before any label of this study, with the items, prompt index and analysis script.
Pablo approved the run on 2026-10-04.

**Why.** José noted that PLs has one computer-world example (Level 1) and none above it, while most agentic tasks
are set in computer worlds. The low PLs levels on coding tasks come mostly from the rubric's rule that demand
stays low "wherever the solver can run the system and look" (nearly every PLs reason on ProgramBench, DeepSWE and
FrontierSWE cites it). Pablo's ruling: PLs is simulating in one's head, not with an external tool. So the rule
stays. What the rubric lacks is an example of a computer world where the run cannot be repeated first.

**Question.** Do three such examples place where intended, and do they leave everything else unchanged?

**Candidate.** `PLs_candidate.txt`: the current `PLs.txt` plus one example bullet at the end of Levels 3, 4 and 5.
No other change. `make_prompts.py` asserts this.
- Level 3: a web service whose retries load a slowing database; a release that doubles traffic, with no copy of
  the system to try it on.
- Level 4: an LRU cache shared by a cycling batch job and a web process's hot keys; the job runs only on the live
  cache and cannot be rehearsed.
- Level 5: 300 services moved to a new retry and timeout policy in one release, with no copy at that scale.

## Design

- **Judge.** Opus 5.5 at effort low, `adele-judge-v2-low` (Read, Write; no CLAUDE.md), relayed by
  `judge-dispatcher-v2-low`; v2 prompt (`build_annotation_prompt_v2`), rubric as the catalog shows it. One item
  per call. Only answers written by `claude-opus-5-5` count; others are judged once more. Never Fable.
- **Blinding.** Opaque file ids; all sets and both texts shuffled together into run `plsc-1`.
- **4-gram check (JUDGING.md rule 4).** Every item of P, M and B is checked against every example bullet of the
  rubric it is shown with. One pair item (M3a) shared "and there is no" with the new Level 3 bullet. It was
  reworded, with its partner M3b, before sealing. Now no item shares a 4-gram.

| set | items | texts | labels per item and text | calls |
|---|---|---|---|---|
| P placement | the 3 new bullets, under the current text (which lacks them; examples kept, JUDGING.md rule 2) | cur | 3 | 9 |
| M minimal pairs | 4 pairs of computer situations (`pairs.csv`) | cur, cand | 3 | 48 |
| B battery-v1 | the lab's 36 standing items (lab record `7159671`) | cur, cand | 1 | 72 |
| R real tasks | 60 sandboxed tasks: 20 each from the SWE-bench Verified, DeepSWE and TB 4.0 clean sets (seed 20261004) | cand; cur on 20 | 1 | 80 |

209 calls in pass 1. R's candidate prompts are the released prompts with the rubric text swapped. R's reference is
the released label (same judge, prompt and current text). The 20 current-text repeats (7, 7, 6) measure how often
the judge alone changes a released label.

**Minimal pairs.** Each pair differs in one respect.
- M1 (queue backlog with feedback) and M2 (two jobs that may deadlock): a full test copy is available (a) or the
  run happens once, live (b). Holds if a ≤ 2 and b ≥ 3.
- M3 (a filling disk, no spare machine): nothing else writes (a), or a full disk triggers timeouts that write more
  to the log (b). Holds if a ≤ 2 and b ≥ 3.
- M4 (a short Python function): traced by hand with no interpreter (a), or with an interpreter open (b). Holds if
  a ≤ 2 and b ≤ a. This guards against the new examples lifting rule-governed code tracing, which the rubric
  places at Level 2 at most.

## Checks and decision rule (`analysis/analyse.py`)

An item's label under a text is the median of its labels (lower middle if even).
1. **Placement (P).** Each new example's median under the current text, against its own level. Exact or within
   one: kept. Off by two or more: that example is dropped from the candidate. Placement does not fail the
   candidate.
2. **Minimal pairs (M).** A loss is a pair that holds under the current text and fails under the candidate.
3. **Battery (B).** Per item, candidate minus current. A move of two or more goes to pass 2.
4. **Real tasks (R).** Per task, candidate minus released label. A move of two or more goes to pass 2. **Drift**:
   more tasks up than down, sign test p < 0.05, and a larger share up than in the noise subset.
5. **Pass 2 (`plsc-2`).** Every pair behind a loss, and every item with a move of two or more, is judged again
   under both texts, three repeats each. A loss is confirmed if pass 2 repeats it. A move is confirmed if pass 2
   moves the item in the same direction. If more than 8 items need pass 2, I stop and report before running it.
6. **The candidate passes** if no loss and no move of two or more is confirmed, and R shows no drift. Then the
   kept examples go to `src/adele/rubrics/data_v2/Paolo_Pablo/PLs.txt` with Pablo's OK. Otherwise `PLs.txt`
   stays unchanged and the report names what broke.

**Also reported.** Agreement and shifts per set; R's level counts per benchmark; how often candidate answers name
the new examples (regex in `analyse.py`); each pair's medians under both texts, losses or not.

## Predictions (sealed)

- The candidate passes: 0.75. All three examples are kept: 0.6.
- Placement exact under the current text: Level 3 0.6, Level 4 0.45, Level 5 0.4. Within one: 0.9, 0.9, 0.85.
  A miss is low rather than high: 0.8.
- Pairs hold under the current text: M1 0.7, M2 0.6, M3 0.6, M4 0.75. No confirmed loss: 0.85. At least one gain:
  0.3.
- Battery: no confirmed move of two or more: 0.9. At least 75 per cent of the 36 items unchanged: 0.7.
- Real tasks: at most 10 per cent of the 60 go up: 0.7. Drift: 0.1. No confirmed move of two or more: 0.9.
  The noise subset changes at least 15 per cent of its 20 labels: 0.5.
- Candidate answers name a new example on 5 to 30 per cent of R tasks: 0.5.

## Cost

209 calls in pass 1, plus up to about 50 in pass 2 and retries. About 2 weekly points (now 54 per cent).
