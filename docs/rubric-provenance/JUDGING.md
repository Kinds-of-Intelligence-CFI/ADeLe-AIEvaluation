# Judging protocol for rubric rounds (state of 2026-08-26)

Hard-learned rules, each from a measured failure in labs/rubric-qa:

1. **Strip the `#!` line mechanically before showing a rubric to a judge.** Telling a judge to
   ignore it does not work: r58 and r64 were both contaminated through it, r64's judge quoting the
   very warning added to prevent that. `catalog.py` already strips it for production; any ad-hoc
   harness must too.
2. **Never strip the examples.** The level statements alone under-determine the top band: in r68
   the same judge moved the same item three levels on whether the examples were present. Stripped
   -variant numbers are lower bounds, not like-for-like readings.
3. **Three judges or one strong one.** haiku sits a level low at Level 3+ and was the sole wrong
   cell in r58, r61, r63, r64 and r69; median-of-three absorbed it every time. A single-judge run
   with a small model will misplace the top band and the carves.
4. **Mechanical item-independence at seal time.** Diff every item's word 4-grams against every
   example bullet of the file under test. Asserting the check is not running it: the assertion
   version failed in r60; the mechanical version caught a circular item in r69 before the round.
5. One item per call, sealed predictions and decision rules before any judging, never Fable as a
   judge, and record failed seals as failed.
