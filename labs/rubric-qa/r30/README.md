# Round 30 inputs — the paired old-arm test for `PLs` and `MSc`

Committed **before any annotation was run**. `prereg_r30.json` states every hypothesis, the
value that would falsify it, and the fact that criterion validity is not testable here.

| file | what it is |
|---|---|
| `prereg_r30.json` | pre-registration: arms, judges, hypotheses, decision rule |
| `MSe_old.txt`, `MSc_old.txt` | the old arm, taken verbatim from `origin/agentic` |
| `PLs_new.txt`, `MSc_new.txt` | the new arm, taken verbatim from this branch |
| `nset.csv` | 16 real trace frames (8 SWE-bench HAL cp50 + 8 tau-bench airline cp50), verbatim from `labs/hal-traces` — designed by neither rubric |
| `pset.csv` | all 81 examples the four rubrics carry, with the level each claims |
| `cset.csv` | 8 designed minimal pairs: stakes ×2, resistance ×1, agent-count ×1 |

The `C` set is the only part that is designed rather than sampled, and it is built so that
**each arm is scored against its own stated drivers** — origin names stakes and the number of
agents as drivers, this branch's `MSc` explicitly disclaims both. Neither theory of the
construct is assumed correct; a rubric fails the contrast when it contradicts its own text.
