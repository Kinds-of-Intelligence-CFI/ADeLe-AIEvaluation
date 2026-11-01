# natural-prompt — results

**Question.** Can a plain annotation prompt stop Sonnet 5.5's safeguards from blocking our requests,
without changing the labels of our judge (Opus low)?

**Answer.** Half yes. The plain prompt removes the blocks completely: Sonnet 5.5 answered all 44 PLp
cells, including the 23 it had blocked twice. But it also moves Opus low's labels up: +0.16 on PLp
and +0.27 on PLe. No label went down. So it is not a drop-in replacement for the old prompt.

**Status.** Complete (2026-09-29). First run: "fixes the flags, but changes the labels". Variant B
(amendment 1): fails one of five checks (T2) but keeps the other labels at 95.5%. The old prompt
stays in use until Pablo decides. The main open question is whether the shift comes from the prompt or from
judge drift since 2026-09-27, when the old labels were made.

## Design

See `PREREGISTRATION.md`, pushed before any label (`98f65a8`).

- **The prompt** (`prompt.py`): one sentence stating the research purpose, the rubric and task in
  tags, "rate the task's demand ... according to the rubric", the lower-of-two rule, a short
  assessment before the level, and the usual final sentence. The inputs are identical to the old
  prompt's: every rebuilt old prompt matched its stored hash.
- **A.** Sonnet 5.5 high on the 44 PLp gate cells.
- **B.** Opus low on the 132 gate cells, against Opus low's stored labels under the old prompt
  (`swepl-gate-low`, 2026-09-27).

## Pre-registered results

From `results/natural_prompt.json` (`analysis/analyse.py`).

**A. Safeguards: passes.**
- The 23 cells blocked twice under the old prompt: all 23 answered.
- The 21 control cells: all 21 answered.
- Calls stopped by a safeguard: 0 of 44. Every answer was written by `claude-sonnet-5-5` at effort
  high.

**B. Method: fails check 3.**

| | exact | within one level | mean shift |
|---|---|---|---|
| all 132 cells | 0.84 | 1.00 | +0.16 |
| PLp | 0.84 | 1.00 | +0.16 |
| PLe | 0.73 | 1.00 | +0.27 |
| PLs | 0.95 | 1.00 | +0.05 |

- Checks 1 (exact 0.83 or more), 2 (within one level 0.98 or more) and 4 (at least 95% labelled by
  `claude-opus-5-5`) hold. Check 3 (every shift within ±0.10) fails on PLp and PLe.
- **Every change is upward.** PLp: 7 cells up (0→1 twice, 1→2 four times, 2→3 once). PLe: 12
  cells from 2 to 3.

**Verdict: "fixes the flags, but changes the labels."**

**Sealed predictions.**

| prediction | p | outcome |
|---|---|---|
| A passes | 0.65 | happened |
| at least 20 of 21 control cells answered | 0.85 | happened (21) |
| B: exact 0.83 or more | 0.65 | happened (0.84) |
| B: within one level 0.98 or more | 0.9 | happened (1.00) |
| B: every shift within ±0.10 | 0.55 | failed (+0.16, +0.27) |
| B passes | 0.45 | failed |
| both pass | 0.3 | failed |
| answers shorter under the natural prompt | 0.75 | happened (871 against 1,065 characters) |

## Exploratory results

- **With the plain prompt, Sonnet 5.5 high sits close to Opus medium on PLp.** It matches 80% of
  the 44 cells exactly, with a mean shift of +0.02, against Opus medium's labels under the old
  prompt. Under the old prompt it matched 62% of the 21 cells it answered, with +0.29. Against Opus
  low under the same plain prompt, it matches 77%, with −0.18.
- **The wording effect is as large as the model effect.** Changing only the prompt moves Opus low by
  a quarter level on PLe. That is the size of the Sonnet-against-Opus offset in `judge-sonnet55`.
- **Cost.** The 5-hour meter went from 0% to 10% and the weekly meter from 0% to 2%, over 176 calls
  plus relays and my own turns.

## Amendment 1: variant B

Pre-registered after reading the first run's 21 changed answers (`34a6567`; see deviation 1 for
the count). Variant B adds: compare with the rubric's examples, base the level on the stated
conditions rather than on how long or easy the work looks, and choose the lower of two adjacent
levels only when the task genuinely fits both. From `results/variant_b.json`
(`analysis/analyse_b.py`).

| check | result | holds |
|---|---|---|
| T1. the 12 PLe cells stay at 3 | 12 of 12 | yes |
| T2. the 6 upgraded PLp/PLs cells go back | 2 of 6 | no |
| T3. the other 111 cells match the old labels | 95.5% exact; shifts 0.00 (PLp), +0.03 (PLe), 0.00 (PLs) | yes |
| A. Sonnet 5.5 answers the 44 PLp cells | 44 of 44, no safeguard stop | yes |
| P. Opus cells labelled by Opus 5.5 | 132 of 132 | yes |

**Verdict: fails (T2).**
- Back to the old label: django-11433 (PLp 1, citing the Level 1 examples) and django-15629 (PLs 1,
  citing the failing-test example).
- Still at 2: astropy-7671, scikit-learn-14894 and sympy-20916 (PLp), and django-15916 (PLs). The
  judges now compare with the examples, but match these bug fixes to Level 2's data-pipeline example.
  Two answers still take the higher level after naming the lower one ("Level 1 or at most Level 2";
  "could be argued down to Level 1").
- Contested cells: django-11451 and django-12143 stay at 1 (old 0); django-15629 PLp returns to 2.
- Overall against the old labels: 82.6% exact, shift +0.14, almost all from the 12 PLe cells.

**Sealed predictions.** T1 0.75: held. T2 0.55: failed. T3 0.7: held. A 0.85: held. B passes 0.35:
failed.

**Reading.** Variant B keeps what the plain prompt fixed (the PLe reading and Sonnet's blocks) and
removes the drift elsewhere: 95.5% agreement on the undisputed cells is above Opus low's repeat
agreement (about 88%). The miss is narrow: whether a standard bug fix is one routine (PLp 1) or a
few assembled steps (PLp 2). That is a boundary question in the rubric, like the 2/3 question in
`plp-2-3-boundary`, and no prompt sentence settled it.

## Deviations and caveats

- No deviations from the pre-registration.
- **Main caveat: no same-day control.** The old-prompt labels were made on 2026-09-27. Subagent
  model snapshots cannot be pinned, so part of the shift could be judge drift rather than the prompt.
  Noise alone is unlikely: 19 moves, all upward. A same-day run of the old prompt on the same 132
  cells would separate the two.
- Two Opus calls got a "connection lost" notice after answering. Both answers were complete and
  were written by Opus 5.5.
- One benchmark and 44 tasks. PLs is nearly constant on SWE-bench, so its agreement says little.

## Reproduce

```
python experiments/benchmarks/natural-prompt/analysis/analyse.py
```

The numbers above are those committed with this file. The judges' answers stay out of the repo.
