# Round 64 — auditing PLs's own numbered examples (2026-08-25)

Scored against `PLs_noL34examples.txt`, a variant with the Level 3 and Level 4 example bullets
removed, so each example is scored without being able to match itself. Judges h/s/o, median of three.

## Three of four examples hold. One is mis-pitched.

| example | sits under | h | s | o | median | verdict |
|---|---|---|---|---|---|---|
| one lane closes on a ring road | L3 | 3 | 3 | 3 | **3** | holds |
| fox and rabbit trough below forty | L4 | 3 | 4 | 4 | **4** | holds |
| fine billiards break | L4 | 4 | 4 | 4 | **4** | holds |
| two queues, arrivals at 0/40/55/90/95 | L4 | 2 | 3 | 3 | **3** | **mis-pitched** |

The queueing example fails for exactly the reason r63 predicted, and both stronger judges said so in
the same words: with every arrival and service time given, the answer **survives a coarse run**,
which is what the new sensitivity mark explicitly excludes. It was Level 3 material sitting under
Level 4.

**Fixed**: the arrival list is replaced by "arrivals run all morning at just under the rate the
counter can clear". Near-critical utilisation is genuinely sensitive, so the example now earns the
level it sits under and still shows accuracy-not-part-count, which was its job.

The other three survived, so the over-specification failure is real but not pervasive: it bites
where the numbers *determine* the trajectory, not where they merely *describe* the situation. The
ring road's 4,000-against-800 and the trough's 900-and-40 set a scene; the queue's five timestamps
set the whole course.

## The meta line leaked again, and this time it leaked the warning

Haiku's entire reasoning on the queueing item was:

> The warning states this queueing example ... is "fully determined arithmetic and may score 2
> under this rubric."

That warning was added to the `#!` line in v16 *because* of the r58 leak, and the line already told
judges to read the rubric only. **Telling a judge to ignore a line does not work.** Two rounds now
have been contaminated through it.

v17 changes the instruction from "ignore this line" to "strip this line before showing the rubric to
a judge", and forbids recording any claim about a specific example's likely level there. The
judging protocol should strip the `#!` line mechanically rather than relying on the prompt.

Median-of-three absorbed it again, as it absorbed haiku's outliers in r58, r61 and r63. That is four
rounds in which the weakest judge was wrong in a way the median hid.
