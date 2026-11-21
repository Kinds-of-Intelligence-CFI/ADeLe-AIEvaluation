# noreason — run log

## 2026-10-06

- **Reference arm.** `noreason-ref` (450) and `noreason-ref-ms` (80) are complete. All 530 labels were written by
  Opus 5.5, with no rejections and every transcript passing `check`.
- **Sentence-format relays stopped.** Two `noreason-ms` relays with the sentence-format prompt were stopped after 132
  answers, all bare sentences (amendment 1). Their run and answers are in `aborted/` and `judge-io/_aborted/`.
- **Digit format verified.** `noreason-ms` was re-pinned with the digit-only prompt. All 400 answers in its first
  wave were a single digit (max 1 character).
- **Duplicate-judgment snag.** The aborted judges had written to the same response paths before their folder was
  moved. The first `collect` therefore saw two judgments for 135 cells and rejected them as `protocol`.
  - Later collects of `noreason-ms` use a transcript folder that drops transcripts started before the re-pin
    (2026-10-06T18:11:37Z; 137 dropped).
  - The 135 cells are re-judged into `opus-low-a2`.
  - `check` passes.
- **Concurrency cap.** At Pablo's request to parallelise, 13 relays were launched at once.
  - Claude Code runs at most 20 subagents at once, counting dispatchers and judges.
  - Relays beyond about 5 failed: two `noreason-ms` and one `noreason-eqbench4` relay sent 0 cells and were
    released; one `noreason-pl` relay stopped after 45 cells, and its 58 unsent cells were returned by
    `collect --relays-done`.
  - No cell was lost. From then on, at most 5 relays at once.
- **Hidden thinking.** In the sentence-format NR relays, 12 of 137 judge transcripts had a thinking block (0–240
  characters). In the reference arm, 38 of 300 did.
- **Weekly limit hit around 20:00.** Five relays stopped with HTTP 429. `collect --relays-done` returned their
  unsent cells, and the five relays recorded afterwards were released unlaunched.
- **State at pause:**
  - no-reasoning arm: ms 484/484, pl 499/3,048, eqbench4 524/600, gamearena 118/120 (2 refused by the API
    safeguard on every attempt), cooperbench 127/1,200, long 6/65, ms-rest 10/1,548;
  - reference arm: 530/530.
- **Amendment 3:** social-set reference labels and the cost analysis (`analysis/cost.py`). Interim cost on matched
  cells: harness $0.041 per label with reasoning against $0.032 without; median 11.0 s against 7.7 s per call.

## 2026-10-07

- **SNR complete:** 7,057 of 7,065 (df5792c). No-label cells: 3 PL and 3 Game Arena safeguard stops, 2 tau2 MS after a
  fallback writer.
- **SNR verdict mixed** once its PL labels were complete, which triggered SR (amendment 4b, 873c80c). SR prompts were
  checked byte-identical to R′ on all 530 shared cells before launch.
- **SR:** PL 3,045/3,048, tau2 MS 484/484, long 65/65, Game Arena 119/120 complete. Social sets (EQ-Bench 4,
  CooperBench, ms-rest) partial and still running; they do not enter the verdict.
- **Order of SR relays:** PL first (it carries the decision rule), other sets in spare slots; at most 5 relays at once
  and `next --max` at most 4.
- **Usage:** the 5-hour window went from 46% to about 90% over the night (SNR finish plus about 5,000 SR cells);
  weekly from 30% to 40%.
- **Results:** `RESULTS.md`. Verdicts: NR mixed (PLp −6 points on the subset only), SNR mixed, SR not usable.
  Recommendation: NR for mass annotation.
