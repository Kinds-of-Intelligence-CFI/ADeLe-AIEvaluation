# Three-benchmark agentic pilot: PLp, PLe, PLs on real instances with public success flags

**Date:** 2026-09-14 · **Branch:** `agentic-v2` · **Owner:** Pablo · **Status:** exploratory, not pre-registered

38 real benchmark instances × 3 dimensions × 3 judges = 342 labels, median-of-three. The first
time the PL family has been run on real instances that carry per-instance success flags for many
models. Artifacts: `labels_long.csv` (every judge cell), `medians.csv` (medians + solve rates).

> **Read the limits first.** This was *not* pre-registered: items and judges were chosen before
> any hypothesis was sealed, so every number here is descriptive. Nothing below is a gate result.
> The one thing it can do — and does — is tell us which dimension is worth a pre-registered run,
> and which one cannot be validated on these benchmarks at all.

---

## 1. Design

| | |
|---|---|
| dimensions | PLp (Planning), PLe (Action control), PLs (Simulating) — rubric text as on `agentic-v2` |
| judges | haiku, sonnet, opus, one item per call, `#!` line stripped by `catalog.py`, examples kept, median of three (JUDGING.md rules 1–3) |
| items | 14 SWE-bench Verified, 14 tau2 (5 airline, 6 retail, 3 banking_knowledge), 10 Terminal-Bench 2.0 |
| sampling | stratified by public per-instance solve rate, seed 0, plus 2 items carrying pilot anchors |
| outcome | SWE-bench: solve rate over 135 leaderboard entries. tau2: mean reward over 11 models × 4 trials. Terminal-Bench: mean reward over 14 submissions × 5 trials |

Sources and how they were fetched are in `docs/per-instance-results-survey.md`.

---

## 2. The headline: the dimensions behave as designed, and that is the problem

Median demand by benchmark family:

| dimension | SWE-bench Verified | tau2 | Terminal-Bench 2.0 | variance between benchmarks |
|---|---|---|---|---|
| **PLe** | **3** (14/14, no variance) | **1** (11/14) | **3** (10/10, no variance) | **77%** |
| PLs | 1 (12/14) | 2 (10/14) | 0 (6/10) | 28% |
| PLp | 2 (range 1–3) | 2 (range 0–2) | 2.5 (range 1–4) | 17% |

**PLe is doing exactly what the re-key says it should, and that makes it unmeasurable here.**
The r39/r76 doctrine places a task at Level 1 when the environment settles success after
essentially every action, and at Level 3 when checks are available but elected. τ-bench tool calls
return success per call → 1. SWE-bench and Terminal-Bench give you a test suite you may run
whenever you choose → 3. Every judge, nearly every item. The rubric is not failing; it is
reporting that *the checking regime is a property of the harness, not of the instance*.

The consequence for desideratum 9 is sharp, and I do not think it has been stated in the record
before: **a dimension that is constant within a benchmark cannot have its criterion validity
tested within that benchmark.** No number of extra SWE-bench items will help PLe. Its relation to
success can only be estimated across benchmarks, where it is perfectly confounded with everything
else that differs between SWE-bench and τ-bench. Annotating 500 SWE-bench instances on PLe would
buy one number, 3, five hundred times.

---

## 3. What did vary, and what it is worth

**PLp is the only dimension with usable within-benchmark spread on all three benchmarks** (1–3,
0–2, 1–4). Its relation to success is negative in every family, which is the predicted direction:

| family | Spearman(PLp, solve rate) | n |
|---|---|---|
| SWE-bench Verified | −0.34 | 14 |
| tau2 | −0.14 | 14 |
| Terminal-Bench 2.0 | −0.16 | 10 |
| pooled, family-centred | **−0.20** (p = 0.23) | 38 |

Three out of three families negative. Read honestly, that is a sign test at p = 0.125 and a
pooled correlation that does not reach significance. **Achieved power at n = 38 for the observed
effect is 23%** — this pilot was always going to be unable to detect an effect this size. To test
ρ = −0.20 at 80% power needs ~194 items; ρ = −0.30 needs ~85.

Not a length artefact: PLp against prompt characters gives ρ = −0.11, −0.20, +0.11 by family, none
close to significant, so the judges are not just reading "longer task, harder plan". Volume is
routed out of PLp by design and appears to stay out.

---

## 4. The dissociation result, which is the genuinely new evidence

The collinearity that started this whole re-key had a signature: PLe − PLp ≈ +1.0 with SD 0.28,
and zero frames where one was high and the other low. `battery-v1` showed the re-keyed rubrics
separate, but on **designed** items; the record notes the 16 real HAL/τ frames "have almost no
spread and could not settle it either way".

On 38 real benchmark instances:

| family | mean(PLe − PLp) | SD | PLe>PLp | PLp>PLe | equal |
|---|---|---|---|---|---|
| SWE-bench Verified | +1.00 | 0.68 | 11 | 0 | 3 |
| tau2 | −0.21 | 1.12 | 2 | 7 | 5 |
| Terminal-Bench 2.0 | +0.60 | 0.97 | 5 | 1 | 4 |
| **pooled** | **+0.45** | **1.06** | 18 | 8 | 12 |

The constant-offset signature is gone on real data: SD 1.06 against the old 0.28, and the sign of
the difference **reverses by benchmark** — τ-bench tasks demand more planning than execution
control, SWE-bench the reverse. Both directions, on instances nobody designed to produce them.

Within-family (centring removes the between-benchmark component, which is the easy part):

```
        PLp    PLe    PLs
PLp    1.00  -0.03   0.12
PLe   -0.03   1.00  -0.07
PLs    0.12  -0.07   1.00
```

Essentially independent. **Caveat that matters:** because PLe is constant in two of the three
families, every within-family correlation involving PLe is carried entirely by the 14 τ-bench
items. The PLp × PLs independence is the one supported by all three.

---

## 5. Judge agreement, and a disagreement with the lab record

| dimension | exact (3/3) | within ±1 | mean spread |
|---|---|---|---|
| PLe | 63% | 84% | 0.55 |
| PLs | 45% | 76% | 0.79 |
| PLp | 34% | 84% | 0.82 |

Markedly worse than the designed probes of rounds 37–76, where PLe reached α 0.967. Real
benchmark prompts are messier to score than purpose-built items, and PLp — the dimension we most
want to scale — is the least reproducible of the three. Median-of-three is doing real work; a
single-judge production run would inherit this noise directly.

One contrast with the record: **haiku runs high here**, not low. Mean levels by judge — PLe 2.63
(haiku) vs 2.29 / 2.29, PLp 2.16 vs 1.92 / 2.00. The close-out documents haiku sitting *a level
low* at Level 3 and above. Different direction, same conclusion: do not use it alone.

---

## 6. Anchors: one usable, and a snapshot trap worth knowing about

Two sampled items carried pilot anchors (PLe 1 after the tau re-key, PLs 2 from r53).

- **tau-retail-96** — prompt byte-identical to pilot `tau-0146`. Measured **PLe 1 ✓, PLs 2 ✓**. Two for two.
- **tau-airline-7** — **anchor void.** Same task *id* as pilot `tau-0007`, different task *text*.

That second one is the useful accident. The pilot drew τ-bench from the HuggingFace mirror
`HuggingFaceH4/tau2-bench-data`; `data/instances/` was frozen from the sierra-research repo. For
airline task 7 the two differ: upgrade to *economy* versus to *business* plus a card number, and
the newer text adds "You are sick." Same id, different task.

I checked which snapshot the outcome data belongs to, because that is the join that decides
everything: **the Sierra reward files carry the same text as our frozen instances.** The join is
sound and the labels in `medians.csv` describe the tasks the models were actually scored on. But
two rules follow:

1. Historical anchors do **not** transfer by `(benchmark, instance_id)` across tau2 snapshots. The
   r38/r39/r53/r76 τ labels are attached to the HF-mirror text and must be re-verified by prompt
   hash before being reused as ground truth.
2. `instances.check_join` verifies that *ids* match. It cannot see that the *text* behind an id
   has changed. A prompt-hash column exists (`prompt_sha12`) — the reward-side fetcher should
   record one too, so a snapshot drift fails loudly instead of silently mislabelling.

---

## 7. What I would do next, and what I would not

**Would not:** scale PLe annotation on SWE-bench, Terminal-Bench, or any single-harness code
benchmark. The answer is already known and constant. This is the cheapest saving in the plan.

**Would, in order:**

1. **Pre-register PLp on tau2 + SWE-bench at n ≈ 200.** It is the only dimension that varies
   within every benchmark, its direction is consistent, and 194 items is the honest number for the
   effect actually observed. Seal the prediction (negative within-benchmark association), fix the
   panel at three judges, and report the family-centred statistic.
2. **Get PLe variance from the trajectory, not the task.** Checking structure changes *within* a
   rollout — a τ-bench agent that stops reading tool returns is in a different regime than one that
   does not. That is rung 2/3 of the ladder, and the Sierra trajectories are public, unencrypted
   and already downloaded. This is the natural home for PLe, and it would also make the
   task-level-vs-trace-level agreement claim in the redesign testable.
3. **Fix the two repo drifts the survey found** (`tau2.py` describing the bucket as aggregate-only;
   the Terminal-Bench note pointing at Harbor Hub instead of the HF leaderboard repo).

**A caution about ambition.** Even a perfect PLp result on these three benchmarks is a
within-benchmark, single-generation finding. Every model in the SWE-bench and Terminal-Bench
columns is from 2025–early-2026; the extrapolation-to-frontier claim the runbook wants needs the
current generation, and today that exists only for tau2 banking_knowledge, ARC and the gated Epoch
data.
