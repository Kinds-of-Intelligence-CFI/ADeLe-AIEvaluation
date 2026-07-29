# Round 30 inputs — the paired old-arm test for `PLs` and `MSc`

Committed **before any annotation was run**. `prereg_r30.json` states every hypothesis, the
value that would falsify it, and the fact that criterion validity is not testable here.

| file | what it is |
|---|---|
| `prereg_r30.json` | pre-registration: arms, judges, hypotheses, decision rule |
| the old arm | not stored here. Byte-identical to `origin/agentic:src/adele/rubrics/data_v2/Paolo_Pablo/{MSe,MSc}.txt` — fetch with `git show origin/agentic:src/adele/rubrics/data_v2/Paolo_Pablo/MSe.txt` |
| `PLs_new.txt`, `MSc_new.txt` | the new arm, taken verbatim from this branch |
| `nset.csv` | 16 real trace frames (8 SWE-bench HAL cp50 + 8 tau-bench airline cp50), verbatim from `labs/hal-traces` — designed by neither rubric |
| `pset.csv` | all 81 examples the four rubrics carry, with the level each claims |
| `cset.csv` | 8 designed minimal pairs: stakes ×2, resistance ×1, agent-count ×1 |

The `C` set is the only part that is designed rather than sampled, and it is built so that
**each arm is scored against its own stated drivers** — origin names stakes and the number of
agents as drivers, this branch's `MSc` explicitly disclaims both. Neither theory of the
construct is assumed correct; a rubric fails the contrast when it contradicts its own text.

## Round 30 — validation run (24-item stress battery, 3 judges, 4 arms)

Pre-registered in `prereg_r30_validation.json` before any arm was run. Labels in
`validation_labels.csv`; the compression baseline it is diffed against is
`regression_new.csv`.

| | result |
|---|---|
| **H1** PLe S04 moves into 2\|3\|4 | **PASS.** `[1,1,1]` -> `[3,3,4]`, all three judges in range |
| **H2** no collateral movement in PLe | **mixed.** 52/72 prereg-consistent, up from 49, but 13 of 24 items moved |
| **H3** MSc stays >= 71/72 | **PASS.** 72/72 |
| **H4** MSm_new drops where the stance is stated outright | **FAIL.** N09 median 3 -> 3 |
| **H5** MSm_new keeps genuine multi-agent inference | **PASS.** N07 4->4, N08 5->5, S05 5->5 |

### What was kept

The **L1 carve-out for continuously displayed state** did exactly what it was
written to do. S04 had been stuck at 1 since round 26 because judges read a
continuously-updating control panel as the environment checking every step. The
preamble already excluded that ("an observation from which success must still be
worked out"), and it had never bound — round 20's finding again. Stating it at
L1, alongside the legality carve-out that already lived there, moved all three
judges into the pre-registered band.

MSc's tightening is clean: 72/72.

### What was reverted, and why

The narrowed v2 MSm draft is **not** wired into `_ACTIVE`. It is kept at
`MSm_new.txt` with its labels, because the result is worth having on record.

The prereg said: H4 failing while H5 holds means v1's MSm was not in fact riding
on the communication half, and the narrowing is unjustified. That is what
happened — but the arm also did something worse than nothing. Removing "social
cognition" from the title and preamble did not narrow the construct, it *widened*
it: judges began scoring adversarial game reasoning as mind modelling.

```
              MSm_old      MSm_new
  T01 chess   [0, 1, 2] -> [2, 2, 4]
  N05 chess   [2, 2, 2] -> [2, 2, 4]
  N02 replic. [0, 0, 1] -> [0, 2, 2]
```

"Social cognition" was doing load-bearing work: it kept the dimension pointed at
*social* agents. Drop it in favour of "modelling other minds", and a chess
opponent qualifies. So the overlap with MSc is still real and still unresolved —
but it is not fixed by rewording MSm's frame, and the obvious-looking fix makes
the dimension worse. This needs a team decision, not another solo iteration.

### Caveat on H2 that limits what round 30 can conclude

Two changes went into the PLe arm at once — the wording tightening and the L1
carve-out — so the churn cannot be attributed to either. Three items moved the
wrong way, and one is a trap that had held since round 6:

```
  T07 olympiad proof (transcription)  [0,0,0] -> [0,0,3]   one judge
  T04 300-step protocol               [4,4,4] -> [1,4,4]   one judge
  T06 death notification              [0,0,0] -> [0,0,3]   one judge
```

Each is a single judge at n=1, which is within this battery's observed noise, but
bundling the two changes means that cannot be shown rather than asserted. The
clean way to settle it is one arm with the tightening only. That was a design
error in this round and should not be repeated.
