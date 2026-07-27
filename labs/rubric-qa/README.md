# Sensory rubric QA (branch `sensory`)

Validation record for the `SPv` / `SPa` work. The agentic rubrics' 26-round record lives on
`rubrics/v2-improved`; this file starts fresh because the branches are independent.

Method and conventions are inherited: pre-register before running, three judges (haiku,
sonnet, opus), reasoning before the number, report agreement with the level distribution,
and record failed predictions rather than dropping them.

## Round 1b: example placement on the untouched drafts

Protocol identical to the agentic round 25. Strip every `Examples:` block, shuffle the
examples into one pool, hand a judge the full level descriptions plus the pool, and ask it to
put each example back on the level it illustrates. Scoring: how many of three judges recover
the true level. 3/3 clean, 2/3 soft, ≤1/3 defective.

43 examples (20 `SPv`, 23 `SPa`), 129 decisions. `SPv` Level 0 contributes nothing — the
draft has only a `TODO(pablo)` there. Pre-registration in `prereg_sensory_1b.json`, all
decisions in `sensory_placement_labels.csv`.

### Result

| | clean (3/3) | |
|---|---|---|
| `SPv` | 8/20 | **40%** |
| `SPa` | 14/23 | **61%** |
| both | 22/43 | **51%** |

For comparison, on the same test the four agentic rubrics scored 75% before their examples
were repaired and 92% after. **51% is the baseline the rewrite has to beat**; the plan's
target is ≥85%.

### `SPv` L4 and L5 are literally exchanged

The sharpest single result. Two items were swapped by all three judges, in opposite
directions:

- L4 "Resolving extreme binding ambiguity in chaotic scenes (a dense rugby scrum)" → **5, 5, 5**
- L5 "Processing highly degraded thermal or night-vision imagery to identify specific targets" → **4, 4, 4**

This is the "L5 is L4 with intensifiers" defect measured rather than asserted. Both levels
use "severely degraded" and "binding ambiguity in chaotic scenes"; nothing distinguishes them
but adjectives, so the judges sort by vividness instead. A third L4 item — fragmented text
across torn document pieces — went to **3, 3, 3**, and the L5 camouflage item split **3, 4, 5**.
Of the eight L4/L5 examples, one is clean.

### The L1/L2 boundary collapses in both modalities

- `SPv` L2 "Classifying cats and dogs in images" → **1, 1, 1**
- `SPa` L2 "Classifying notes as higher or lower in pitch than a reference" → **1, 1, 1**
- `SPa` L2 "Identifying the direction of a sound source (left vs. right) in a quiet
  environment" → **1, 1, 1**
- `SPa` L2 "Humming back a simple three-note melody" → **1, 3, 3**

L1 says "isolated, distinct sounds in optimal conditions"; L2 says "moderately complex
patterns with minimal clutter". Neither names a condition that the other fails, so anything
clean and simple falls to L1. Under the planned driver this boundary becomes crisp — L1 is
*presented*, L2 requires the target to be *separated* from a dissimilar background — and none
of these four items would be L2 at all.

### Two pre-registered predictions were wrong

**The glare pair placed cleanly.** L1 "Reading printed text in good lighting (even with
slight glare)" → 1, 1, 1; L2 "Reading moderately clear handwriting or text with slight
glare" → 2, 2, 2. Both 3/3. The prediction was that a shared anchor across adjacent levels
must confuse a judge. It did not: the *rest* of each item (printed text in good lighting vs
moderately clear handwriting) carries the distinction, leaving the glare clause redundant
rather than ambiguous. Redundant is still worth removing, but it is not the defect it was
called in the plan, and the plan's §3.1 item 3 is overstated.

**The symphony item placed cleanly at L5** — 5, 5, 5. The prediction was that judges would
balk at scoring generation as auditory perception. They did not, because `SPa` L5's own text
says "creatively generating complex auditory structures". The ladder consistently encodes the
construct error, so a placement test cannot see it.

That is the important methodological caveat for this branch: **placement measures internal
consistency, not correctness.** A rubric can be perfectly self-consistent about the wrong
construct. Only the routing traps (plan round 6) catch the symphony item, and only an
external oracle (plan round 3) catches a mis-scaled driver. Placement is necessary, not
sufficient, and a high score on the rewrite must not be reported as validation.

### Carried forward to the rewrite

1. Rebuild both ladders on the single driver; the L1/L2 and L4/L5 collapses are both
   symptoms of levels separated by adjectives rather than by conditions.
2. `SPv` Level 0 needs examples written, not a TODO.
3. Remove the five `AS` examples from `SPv` (keys in a drawer placed 2/3, basketball 1/3 —
   they are scan items, and they place poorly here because they are not really about
   recovering a signal at all).
4. Drop the symphony and native-accent items from `SPa` L5; both are outside the construct.
5. Re-run this test after the rewrite, and do not treat passing it as validation.
