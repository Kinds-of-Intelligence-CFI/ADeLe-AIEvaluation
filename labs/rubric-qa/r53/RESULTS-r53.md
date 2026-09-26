# Round 53 — PLs v9 against the first human anchor (2026-08-22)

Judges h/s/o, 3 seeds, one item per call, never Fable. Seal: `sealed_predictions_r53.md`.
Raw: `results_r53.csv`. **The rubric under test is NOT in `src/`** — Pablo reviews the text
after this round and it is submitted only on his approval.

## Headline: 6/6 exact against Pablo's labels, 22/22 exact overall, α 0.992

| item | judges | Pablo |
|---|---|---|
| ab-0024 snow frequency | 0 | **0** |
| usaco-0002 max triplet value | 0 | **0** |
| tau-0146 order redirect and swap | 2 | **2** |
| tau-0007 upgrade then cancel | 2 | **2** |
| swe-0090 false validation error | 2 | **2** |
| swe-0461 block-matrix multiply | 3 | **3** |

This is the first PLs number in the project that could have failed for the right reason.
Every previous round scored the text against my own design intent. These six are the labels
Pablo gave in conversation, on benchmark instances, before the v9 wording existed.

All seven pre-registered rules pass:
- **Falsifiers**: A7 = 3 (coupling alone does not reach the top band), A4 and A5 = 2 (an exact
  answer under a supplied rule stays low), A8 = 4 (accuracy places it, not part count).
- **Accuracy contrast** separates by 3 levels on the weather situation and 2 on the break.
- **Coupling boundary**: mutual 3 and 3, chain 2 and 2, no overlap.
- **Carves**: planning search 1, minds 1, obscure-law knowledge 1, execution 0.
- **Executability pair**: the same bug scores 3 reasoned on paper and 1 with a shell and a
  test suite available. Gap of 2, which is the clause Pablo's tool-usage observation put into
  the text today, measured for the first time.

## What the judges' reasoning shows, which matters more than the numbers

The new clauses are doing the work, not being ignored:
- On usaco-0002 a judge quoted the state-change test and the matching L0 example, and said in
  terms that the combinatorial difficulty is real but not scored here.
- On tau-0007 a judge applied the reversed scope explicitly, scored the *tracing* of the
  upgrade-then-cancel consequence, then used the domino gloss to keep it at 2 because the
  chain does not feed back.
- On swe-0461 a judge found the actual feedback — `_blockmul`'s degraded output re-entering
  its own precondition check — and separately noted that runnability trims the accuracy
  demand without removing the coupling demand. That is the executability clause and the
  coupling clause interacting correctly rather than fighting.

## Honest limits

- **Six human labels is a thin anchor**, and they were given in a conversation where I framed
  the candidate levels for each item. That framing could have anchored them. The fresh Part A
  items on the label sheet remain the clean test.
- Sixteen of the twenty-two items are still construction-side.
- Both executability items are new and unreviewed; the pair separates, but the pair is mine.
- **Desideratum 9 is untouched.** No criterion validity, as for the whole stream.
