# pls-relabel — results

**Question.** How do the PLs labels of the seven agentic benchmarks change under the adopted PLs text, which adds
three computer-world examples at Levels 3 to 5?

**Answer.** They fall a little, mostly on DeepSWE, and the signal moves rather than grows.
- DeepSWE: 59 of 90 tasks were at Level 2; now 25 are. PLs now tracks solve rate (ρ = −0.22, p = 0.033; was 0.00).
  It adds a little beyond PLp (partial ρ = −0.20, p = 0.06; PLp and PLs correlate +0.14).
- SWE-bench Verified: 26 tasks at Level 2 become 5. The weak signal halves (−0.09, p = 0.051; was −0.18).
- tau2 is unchanged (97 per cent of labels the same; −0.20 within domain, was −0.19).
- Elsewhere PLs moves by at most a tenth of a level on average and stays null.

**Status.** Complete (2026-10-04). 1,029 calls (runs `pls-relabel`, `pls-relabel-long`), all written by Opus 5.5
at effort low; 1,027 labels. Two tasks have no label after safety-classifier stops on every attempt (ProgramBench
`zip-password-finder`, TB-Science `protein-active-learning`). The seven releases now carry these labels. Sealed
predictions: 6 of the 11 not set at 0.5 on the right side.

## Design

See `PREREGISTRATION.md`, pushed before any label (`9784275`; deviation 1: launched before the weekly reset, at
Pablo's request). Old labels are each study's released v2/PLs labels at commit `cd608bf`.

## Results

| set | n | old levels 0/1/2/3/4 | new levels | unchanged | mean shift | ρ old | ρ new |
|---|---|---|---|---|---|---|---|
| SWE-bench Verified | 443 | 1/416/26/0/0 | 2/436/5/0/0 | 93% | −0.05 | −0.18 (p < 0.001) | −0.09 (p 0.051) |
| tau2 (within domain) | 242 | 4/14/224/0/0 | 3/18/221/0/0 | 97% | −0.01 | −0.19 (p 0.003) | −0.20 (p 0.002) |
| DeepSWE | 90 | 0/31/59/0/0 | 1/64/25/0/0 | 50% | −0.39 | 0.00 | −0.22 (p 0.033) |
| ProgramBench | 129 | 0/114/15/0/0 | 0/123/6/0/0 | 85% | −0.07 | −0.14 ns | −0.09 ns |
| FrontierSWE | 19 | 0/9/10/0/0 | 1/12/6/0/0 | 74% | −0.26 | −0.01 ns | +0.07 ns |
| Terminal-Bench 4.0 | 34 | 9/9/16/0/0 | 10/11/14/0/0 | 85% | −0.09 | +0.05 ns | −0.01 ns |
| TB-Science | 69 | 29/10/25/5/0 | 30/7/29/2/1 | 86% | 0.00 | +0.09 ns | +0.04 ns |

ρ is Spearman with each set's primary outcome (as `ms-benchmarks`); "ns" means p ≥ 0.05. Terminal-Bench 4.0 now
has a PLs label for `uefi-bootkit` (35 tasks); the ρ shown is on 35.

**DeepSWE.** Of the 59 tasks at Level 2, 39 fell to 1 and 20 stayed. Of the 31 at Level 1, 5 rose to 2. The tasks
that keep Level 2 are harder (ρ = −0.22). The new labels correlate only weakly with PLp (+0.14), and the partial
correlation with solve rate given PLp is −0.20 (p = 0.06): a small signal of its own. On SWE-bench the partial is
+0.03 (p = 0.47): nothing beyond PLp, before or after.

**SWE-bench.** 25 of the 26 tasks at Level 2 fell to 1. They carried most of the old weak signal.

## Predictions (sealed)

| prediction | p | outcome |
|---|---|---|
| DeepSWE: at least 50 of 90 at Level 1 or lower | 0.75 | yes (65) |
| DeepSWE: mean shift below −0.3 | 0.6 | yes (−0.39) |
| SWE-bench: at least 80 per cent unchanged | 0.75 | yes (93%) |
| tau2: at least 80 per cent unchanged | 0.75 | yes (97%) |
| no set's mean shift above +0.2 | 0.9 | yes |
| more sets shift down than up | 0.7 | yes (6 down, 1 flat) |
| TB-Science keeps at least 3 tasks at Level 3 | 0.6 | no (2, and 1 at Level 4) |
| no task at Level 4 or 5 | 0.85 | no (1 TB-Science task at 4) |
| SWE-bench new PLs significant and negative | 0.5 | no (p = 0.051) |
| tau2 significant and negative | 0.45 | yes |
| no other set significant and negative | 0.75 | no (DeepSWE) |
| every set of 90 or more within 0.1 of its old ρ | 0.6 | no (DeepSWE moves by 0.22) |

## What this means

- The new examples make PLs sharper on runnable code tasks: most fall to Level 1, as the ruling intends.
- Where tasks keep Level 2 on DeepSWE, they are harder, and not only because their plans are harder. One set, one
  test: treat it as a lead, not a finding.
- PLs stays a weak, secondary rubric on these benchmarks. Its one steady signal is tau2, where stated rules settle
  what each action does.

## Files

| | |
|---|---|
| runs | `../mass-annotation/runs/pls-relabel/`, `../mass-annotation/runs/pls-relabel-long/` |
| analysis | `analysis/analyse.py` → `results/analysis.json` |
| releases | the seven studies' `release/` folders now take PLs from these runs (`../release.py` and each `export.py`) |
