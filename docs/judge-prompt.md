# The judge prompt

**Production since 2026-11-02:** builder `v1-layout-noreason` (`adele.annotation.prompts`), with Opus 5.5 at effort
low. Through the API it runs with `judge.harness = "subagent-v2-low"`, so its labels pool with subagent labels. Pablo
adopted it on 2026-11-02, on Jose's proposal: "drop the chain-of-thought and the minimum; the rest, the closer to the
original the better."

```
The following rubric describes six distinct levels of *{dimension}* required by different tasks:
{rubric}

TASK INSTANCE: {task}

INSTRUCTION: Score the level of *{dimension}* demanded by the given TASK INSTANCE using a discrete value from 0 to 5. Answer with the level alone, as a single digit from 0 to 5, and nothing else.
```

It is the published v1.0 prompt (paper, Table 6) with two changes:
- **No chain-of-thought request.** Opus reasons on its own, and effort sets how much.
- **A bare-digit answer** instead of the closing sentence.

## Why (evidence)

| question | study | answer |
|---|---|---|
| Which prompt differences move labels? | `experiments/benchmarks/prompt-ablation` | The tie rule (+0.08) and written reasoning (+0.05) do; the length clause and the layout don't. The effects add. |
| Does dropping the tie rule unfreeze a rubric? | `experiments/benchmarks/tie-rule-freeze` | No. The PL bar, the MSc v4b and MSm lab rules, and the tau2 MSc link all hold. MSc against Pablo goes 13 → 14 of 15. |
| Why do our v1 labels read lower than GPT-4o's? | `experiments/benchmarks/v1-prompt-bridge` | Mostly the model, not the prompt: Opus scores each construct more narrowly, with less halo. |
| Can a cheaper model judge with this prompt? | `experiments/benchmarks/judge-choice` | No. Sonnet 5.5 and Haiku 5.5 miss every agreement bar; on MSc both read refusals as negotiations. |
| What does the prompt change on Opus? | `experiments/benchmarks/judge-choice` | About +0.13 against the old production labels; Pablo's set H 12 of 15 (full input) and 15 of 15 (real tau2 input). |

## What it means for existing labels

- **Runs pinned before 2026-11-02 keep their prompt.** That includes the rest of `w1v1-other`, so wave 1 stays one
  prompt.
- **New runs use `v1-layout-noreason`.**
- **Released sets** are relabelled at the next planned relabel. Label set layers record the prompt behind each label
  (`prompt_builder`).
- **Still to do:** a formal freeze check of this prompt (the full PL bar, the MSc/MSm lab with three repeats).
  tie-rule-freeze checked the tie-rule removal itself; the other changes (layout, the length clause) did nothing in
  the ablation.

## History

| from | prompt | why |
|---|---|---|
| paper (v1.0) | published prompt, chain-of-thought, GPT-4o | — |
| 2026-07-26 | the repo's `v1` builder gains a tie rule | judging protocol moved from rubric text to the shared prompt |
| 2026-09-29 | `v2`: natural wording, short assessment, tie rule, length clause | Sonnet 5.5's safeguards blocked the chain-of-thought request (`natural-prompt`) |
| 2026-10-07 | `v2-noreason`: bare digit | no loss without reasoning (`noreason`) |
| 2026-11-02 | `v1-layout-noreason` (this file) | as close to the paper as possible, without the tie rule or chain-of-thought |
