# Plan: the sensory rubrics (SPv, SPa)

Branch: `sensory`, cut from `agentic` at `7acd8eb`.

Deliberately independent of `rubrics/v2-improved`, which carries the four agentic
dimensions (`PLp PLe PLs MSc`) and their validation. Neither branch depends on the other,
and the agentic PR should not wait for this one. What this branch *does* take from that
work is method: the design conventions and the tests, not the commits.

This is a plan, not a proposal to merge. Nothing here proposes any change to v1.

---

## 0. Status

`SPv.txt` (visual), `SPa.txt` (auditory), `SNk.txt` (kinesthetic) and `SNp.txt` (dexterity)
already exist in `src/adele/rubrics/data_v2/Paolo_Pablo/`, transcribed from the source Doc
and held out of the active set as `_DEFERRED_MULTIMODAL`. They are in no manifest and
nothing annotates with them. So this is a promotion question, not a drafting question.

**Scope: `SPv` and `SPa` only.** `SNk` and `SNp` stay deferred — no current benchmark
exercises them at all, so they cannot be validated even in principle, and bundling them
would sink the two that can be.

## 1. Does a sensory dimension belong in ADeLe?

Yes, and the gap is clean. Across the v1 set — `AS AT CEc CEe CL KNa KNc KNf KNn KNs MCr
MCt MCu MS QLl QLq SNs VO`, plus the `UG_choice_num` format helper — nothing scores *how
hard it is to get the content out of the signal*:

- `SNs` (Spatio-physical Reasoning) scores reasoning over spatial relationships once you
  have them: "mental manipulations… transformations, and physical predictions". The input
  is assumed legible.
- `AS` (Attention and Scan) scores *locating* a target among distractors, and says so
  outright: "The challenge is not on determining what to look for but focusing the
  attention to find it within a larger context." Once attention lands on the target, the
  target is assumed readable.

That assumption is exactly what fails for a fogged windscreen, a water-damaged page or a
voice at 0 dB SNR. v1 was built for text benchmarks, where the assumption was free.

## 2. The single driver

**How far the required information sits from a direct readout of the signal.**

One quantity, modality-neutral — which is what lets `SPv` and `SPa` share a ladder.

| L | the information is… |
|---|---|
| 0 | not carried by any perceptual signal — the task has no visual/auditory input |
| 1 | **presented**: the signal shows it plainly; reading it off is the whole job |
| 2 | **separated**: present and intact, but interleaved with a background that does not resemble it, so it must be isolated first |
| 3 | **reconstructed**: partly destroyed, occluded or masked, so what remains must be completed using regularities of the domain |
| 4 | **combined**: no single view carries it; several individually insufficient views must be put together across space, time or modality |
| 5 | **inverted**: no direct route exists; recovery requires knowing how the signal was formed and working backwards through that process |

Written into the level descriptions themselves, not the preamble — the verb spine
convention from the PL family. Each level carries a `Critically…` floor naming what does
*not* qualify. The two boundaries needing them most are 1/2 (a busy but legible scene is
still 1) and 3/4 (one degraded view is 3 however degraded; 4 requires that no single view
suffices).

### 2.1 Routing table

| feature | goes to | why |
|---|---|---|
| how long perception must be sustained | `VO` | duration, not recovery |
| how many distractors are scanned past | `AS` | AS owns this by its own preamble, including "visual objects, sounds" |
| what the recovered content *means* | `KN*`, `CL`, `MS` | interpretation, not extraction |
| rotating or projecting a recovered shape | `SNs` | transformation of an already-legible input |
| producing images or audio | nowhere here | generation is not perception |
| number of elements when all are clear | nothing | high detail is not demand |

### 2.2 Two rubrics, not one

The driver is modality-neutral, so a single "perceptual recovery" dimension is tempting.
Reject it: a model can be strong on vision and weak on audio, and one score would average
that into noise. Keep both, sharing an identical ladder and differing only in anchors and
examples. That also makes the pair a discriminant-validity test in itself — the same
ladder on two modalities should produce *uncorrelated* scores across a mixed battery.

## 3. What is wrong with the current drafts

### 3.1 `SPv`

1. **Multi-driver preamble** — "resolution and detail required, temporal dynamics…,
   clutter and signal-to-noise ratio, and scene complexity". Four conjuncts: the same
   structure that made the old agentic rubrics collinear. A static degraded X-ray and a
   clean fast rugby scrum land on the same level for unrelated reasons, so the number is
   uninterpretable.
2. **Level 0 has no examples at all** — only `TODO(pablo)`.
3. **Adjacent levels share anchors.** Glare at L1 ("even with slight glare") and L2 ("with
   slight glare"). Camouflage at L3 and again at L5.
4. **L5 is L4 with intensifiers** — both use "severely degraded" and "binding ambiguity in
   chaotic scenes"; L5 adds "expert", "severe", "constant".
5. **A quarter of the examples are `AS` examples** (5 of 20): keys in a cluttered drawer,
   tracking 2–3 people, following the basketball, tracking occluded players, the
   air-traffic controller. Every one is scanning for a target among distractors, which is
   `AS` by AS's own definition. Activating `SPv` as drafted would introduce a **new**
   collinearity with a v1 dimension.
6. **A human role names the solver** — "air-traffic controller visually tracking aircraft"
   describes who does the task. Example *content* may contain people; the level must not
   presuppose a human solver.

### 3.2 `SPa`

1. **Same four-conjunct preamble** (fidelity, speed, SNR, source count).
2. **Construct leak at L3** — "detecting sarcasm or hesitation in a voicemail based on
   intonation" is mind-modelling reached through audio. The acoustic recovery is trivial.
3. **Construct leak at L5** — "composing a complex symphony" is generation. As drafted, a
   text-only model writing a score would take `SPa` 5. A criterion-validity break, and a
   good trap item.
4. **A propensity, not a demand, at L5** — "learning to speak a language… to a
   native-level accent" scores an acquisition trajectory. Same category error that removed
   `ECc`.
5. **The cocktail-party case is unassigned** — separating one voice from competing voices
   is recovery (`SPa`); choosing *which* voice to attend to is `AS`. The ladder must say
   which, at the level, or it will be read both ways.

## 4. What round 25 adds: the examples matter as much as the levels

Round 25 on the agentic branch (`labs/rubric-qa/README.md` §25) tested the *examples*
rather than the level descriptions, by stripping every `Examples:` block, shuffling the
examples into a pool, and asking judges holding the full level text to put each one back.
75% of examples were recovered by 3/3 judges before fixes, 92% after. Three lessons
transfer directly, and one of them changes this plan's critical path.

**Lesson 1 — the dangerous defect is an example that contradicts its own level.** Not
vagueness: outright inconsistency, which no amount of reading the level text can fix
because the example *is* the level text for most judges. `SPv`'s glare pair is exactly
this shape and would fail 0/3 with certainty; the L3/L5 camouflage repeat is a second.

**Lesson 2 — a cross-dimension note is not free.** Adding "carrying this out is `PLe`" to
a `PLp` L5 example dropped it from 3/3 to 3/6, while the mirror note on the `PLe` side
cost nothing. A contrast note helps when it names what the example is *not*; it hurts when
it invites the judge to weigh another dimension's difficulty while placing the item. So
the `SPv`/`SPa` ↔ `AS` separation should be carried by **one-directional** notes, tested,
not sprinkled on both sides by assumption.

**Lesson 3, and the schedule change — the placement test needs no stimuli.** It is
text-only end to end: it reads the rubric, not the world. So the internal coherence of the
`SPv`/`SPa` ladders can be measured **today**, before any pipeline work, and the rewrite
can be driven by evidence rather than by the audit in §3 alone. This moves the first real
result forward from "after the pipeline exists" to "this week".

## 5. The oracle

The reason the work is worth doing. Every result trusted in this project came from an
oracle. Perception has a *better* one than planning did, because degradation can be
constructed and measured.

- **Visual, monotone** — ImageNet-C style corruption: 15 families × 5 published severity
  steps on fixed content. Holding content constant and sweeping severity gives a
  ground-truth *ordering*, the same form of oracle that worked on rivercross. The oracle
  need not say "this is level 3"; it need only say "B is at least as hard as A".
- **Visual, occlusion** — swept masked fraction of the target region.
- **Visual, multi-view** — constructed items recoverable from k views and not from k−1.
  This directly tests the 3/4 boundary, which the current draft cannot express at all.
- **Auditory, monotone** — additive noise at measured SNR, swept on fixed speech.
- **Auditory, separation** — swept number of concurrent sources.

Two orthogonal sweeps matter: with severity alone, a rubric could score well by tracking
"how bad it looks" rather than the driver.

## 6. Validation plan

Pre-register before each round, as in `labs/rubric-qa/prereg_*.json`. Judges: haiku,
sonnet, opus. Reasoning before the number. Fable is not a judge.

| R | test | needs pipeline? | pre-registered prediction | kill criterion |
|---|---|---|---|---|
| 1 | **0-vs-≥1 gate** on existing text tasks | no | ≥95% of text-only pilot tasks score `SPv` 0 and `SPa` 0 | text tasks scoring >0 means the gate leaks and the dimension contaminates every existing label |
| 1b | **example placement** on the drafts, then on each rewrite | no | drafts ≤60% clean; the glare pair and the camouflage repeat fail 0/3 | a rewrite that does not reach 85% clean is not ready to test against stimuli |
| 2 | pipeline smoke test: stimuli reach the judge, levels parse | yes | — | — |
| 3 | **monotonicity** on the corruption sweep | yes | Spearman ρ ≥ 0.6 between assigned level and severity step, per corruption family | ρ < 0.6 pooled ⇒ the driver is wrong; stop, do not patch |
| 4 | **designed battery**, ~8 items per level per modality | yes | ≥80% exact against pre-registration, α ≥ 0.8 | <60% exact ⇒ the boundaries are not annotatable |
| 5 | **collision tests**: minimal pairs differing only at a boundary (the glare pair; k−1 vs k views) | yes | each pair separated by ≥1 level in the right direction by all three judges | any pair scored equal by 2/3 judges ⇒ that boundary is not real |
| 6 | **routing traps**: the symphony item (generation), the sarcasm item (`MS`), the cluttered-drawer item (`AS`) | mixed | all three score ≤1 on the sensory dimension | a trap scoring ≥3 ⇒ the ladder has re-absorbed a routed feature |
| 7 | **real benchmark** (a VQA/MMMU-style set; an audio set for `SPa`) | yes | level distribution spans ≥3 levels | >90% of real items on one level ⇒ report the range restriction, not an α |

Rounds 1 and 1b run today. Rounds 2–7 do not.

Report α **with** the level distribution, always — α collapses under range restriction,
and perception on real benchmarks is likely to be range-restricted.

## 7. The pipeline dependency

`src/adele/annotation/prompts.py`:

```python
def build_annotation_prompt(demand_name: str, rubric_content: str, task_instance: str) -> str
```

Text in, text out. Sensory annotation needs:

1. an optional stimulus argument carried through `build_annotation_prompt` →
   `annotator.py` as content blocks rather than a string;
2. an annotation unit change from **task** to **instance** — ImageNet has easy and hard
   images, so a per-benchmark score is meaningless here in a way it is not for planning.
   The frame/label CSV schema assumes one row per task and needs a stimulus reference;
3. an audio-capable judge. Image input is fine across haiku/sonnet/opus; audio is not.
   Until that is resolved `SPa` can be validated only at rounds 1 and 1b and on *described*
   synthetic items — weaker evidence, to be labelled as such rather than pooled with
   `SPv`'s.

This is the load-bearing risk. If (1)–(3) are not going to be built, the honest move is to
leave both rubrics deferred rather than ship unvalidated ladders.

## 8. The battery consequence

A dimension scoring 0 on 95% of the battery is nearly free to add and nearly useless, and
a near-constant column has no variance to correlate. Activating `SPv`/`SPa` is only worth
it if the battery gains genuinely multimodal benchmarks. That is a battery decision, not a
rubric decision, and should be put to the team *before* the rubric work finishes rather
than discovered afterwards.

## 9. Decisions needed

1. Is the battery going multimodal? If no, stop here.
2. Is anyone building the stimulus-carrying annotation path? Without it, rounds 3–7 cannot
   run.
3. Is an audio-capable judge available, or does `SPa` ship after `SPv`?
4. Does `AS` keep clutter-search, as this plan assumes? The alternative — moving it into
   the sensory dimensions — would be a v1 change, which we are not proposing.

## 10. Out of scope

`SNk`, `SNp`, any change to v1, and any claim that these rubrics are validated.
