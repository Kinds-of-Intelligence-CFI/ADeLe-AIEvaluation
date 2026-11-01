# MMe (Episodic memory) examples review (draft for Pablo, 2026-10-04)

Source: `src/adele/rubrics/data_v2/Marko/MMe.txt` (Marko). No provenance file, never lab-tested. So the bar here
is conservative: fix only clear problems. Nothing has been judged. Confidence is how sure I am that a problem is real.

MMe's driver, from its own text: how much must be retrieved about a past event (number of elements, precision,
binding), after how long a delay, against how much interference. The preamble sets the floor: the delay must lie
"beyond immediate working memory". That is the line to MMs.

## Verdicts

| level | example (short) | verdict | why | confidence |
|---|---|---|---|---|
| 0 | learn which action is rewarded by trial and error | **replace** | reward learning from repeated trials is the stimulus-response association MMp's preamble claims. "Without recalling past episodes" is a gloss that tells the judge the answer. An expert-only case | 0.65 |
| 0 | read a visible word | keep | perception. Same as MMs L0, which is fine at 0 | — |
| 0 | features of an object in view | keep | perception | — |
| 1 | one word after five minutes, no distraction | keep | one item, short delay, no interference | — |
| 1 | first of ten photos reappears | **fix** | no delay is given. Ten photos in a row can take 20 seconds, which is MMs (L2: under 30 s, recognition). Add a delay beyond working memory | 0.5 |
| 1 | two objects in novel locations | **fix** | no delay is given, so it can be done from working memory (MMs L1–2). Also jargon ("novel, unique locations") and a semicolon | 0.55 |
| 2 | five words after five minutes and a jigsaw | keep | small set, minutes, modest distraction | — |
| 2 | person repeats a story from two hours ago | keep | one episode recognised after hours. No mind modelling is needed | — |
| 2 | ten pictures among nine similar distractors (black poodle) | **fix** | the poodle clause asks for fine discrimination, which is L3's "higher degree of precision". It then differs from the L3 bullet only by 9 vs 12 distractors. A hairline pair | 0.6 |
| 3 | seven words, ten minutes, similar-word distraction | keep | moderate set, notable interference | — |
| 3 | ten pictures among twelve highly similar distractors | keep | with the L2 fix, it differs from L2 only in distractor similarity, which is the driver | — |
| 3 | keys, wallet, phone placed this morning, not where they were yesterday | keep | hours, proactive interference. Natural | — |
| 4 | watch everyone in an airport terminal for a day | **fix** | thousands of faces is closer to L5's "exceptionally large number". A day of watching everyone also loads sustained attention (v1 AS). No one sets this task. Give a count | 0.5 |
| 4 | ~10 items hidden across a large area, several hours | keep | large set, hours, distraction | — |
| 4 | sequence of 12 cards after other games with the same deck | keep | order, interference from the same deck | — |
| 5 | 50-page legal document, weeks later, "relation to other statutes" | **fix** | the last clause asks for legal knowledge and reasoning about other statutes, not for memory of the reading. Trim it | 0.5 |
| 5 | every occasion an object has been encountered | keep | exhaustive autobiographical retrieval. Vague but correct | — |
| 5 | order of 25 cards dealt a week earlier | keep | very large set, week, interference, order binding | — |

Counts: keep 12, fix 5, replace 1, drop 0, flag 0.

## Proposed wordings

- **L0, replaces trial and error:**
  > Say how many days there are in a leap year.

  General knowledge, with no need to recall when or how it was learned. The L0 text names this case.
- **L1, photos:**
  > In a five-minute slideshow of ten holiday photos, recognise that the last photo is the same as the first.

  One item, recognised with a strong cue, after minutes, with distinct photos between. L1.
- **L1, two objects:**
  > Ten minutes after watching a friend put a ball in a box and a cup on a shelf, say where each one is.

  Two locations, short delay beyond working memory, no interference. L1.
- **L2, pictures:**
  > Identify ten previously seen pictures of household objects from a lineup that adds nine new, clearly different pictures, after a 30-minute delay.

  Recognition after half an hour with low-similarity distractors. Modest interference, L2. The L3 bullet now
  differs only in distractor similarity.
- **L4, faces:**
  > Watch 150 passengers board a flight one by one, then the next day pick out any of them in a crowd of unfamiliar faces.

  A large set, seconds of exposure each, a one-day delay, a crowd of distractors. L4. A day is not L5's "very long
  interval".
- **L5, legal document:**
  > After reading a dense 50-page legal document once, accurately answer detailed questions about specific clauses and cross-references weeks later without review.

  Unchanged except for the trimmed clause. Exceptionally large content, weeks, fine precision. L5.

## Style numbers

| | count | mean words | max words |
|---|---|---|---|
| current | 18 | 19.9 | 27 |
| candidate | 18 | 19.5 | 27 |

v1: mean 25.6 words per bullet. No em dashes or semicolons remain in the bullets.

## Disentanglement

- **MMs.** Three places blurred the line: L1 photos and L1 locations (no delay), and L5 legal document, which had a
  near-copy at MMs L5 ("a 10-page legal document", no delay stated). The first two are fixed here. The MMs copy is
  replaced in the MMs review. MMs L4 (5-minute family tree) and L5 (building tour) still sit near MMe; see the MMs
  review.
- **MMp.** L0 trial-and-error learning was in MMp's territory. Replaced.
- **PL, MS.** No example loads PLp, PLe, PLs, MSm or MSc. L2 "repeats the same story" needs no inference about the
  speaker's mind.

## Problems in the level statements (not changed, reported only)

1. **Several drivers, no rule for trading them off.** Number of items, delay, exposure time, interference, precision
   and binding all raise the level, joined by "or". L3 says "a moderate number over hours to days, or a larger number
   over shorter delays". An annotator cannot place a task high on one factor and low on another. Desiderata 3 and 5.
2. **Delay bands overlap.** L2 minutes to hours, L3 hours to days, L4 hours to years, L5 "very long intervals".
   The delay does not separate L3 to L5.
3. **No "does not cover" paragraph.** The line to MMs (what counts as "beyond immediate working memory") and the
   line to semantic knowledge (KN) sit only in the preamble and L0.
4. **No reading for model tasks.** For an LLM or agent, the key case is information earlier in the context or the
   trajectory. It is still "available", but may be far back. The rubric does not say whether that is a past event.
   This will decide most labels on agentic benchmarks.
5. **"Only brief exposure"** is required at L4 and L5, but the L5 legal-document bullet is a full careful read.
   Minor.

## Open questions for Pablo

1. Point 4 above is the big one. Should earlier context count as a past event, as a perceptually available input,
   or depend on how far back it is? Marko should probably decide. The swebench-30 run put MMe at 0 on all 30 tasks,
   which suggests judges read it as "never".
2. The L0 replacement is a general-knowledge item. Is that the intended L0 for MMe, or should L0 stay perceptual
   only? The L0 text names general knowledge, so I took it as intended.
3. Marko should see these changes. None of them has been placed by a judge.
