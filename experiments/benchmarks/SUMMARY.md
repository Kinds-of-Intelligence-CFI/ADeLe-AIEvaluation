# ADeLe v2 on agentic benchmarks — summary (2026-10-04)

Hand-written overview of the planning rubrics (PLp, PLe, PLs) and the social rubrics (MSm, MSc) on seven agentic
benchmarks. Every number links to a study's `RESULTS.md`, which has the pre-registration, the sealed predictions and
the code. The study index is [RESULTS.md](https://github.com/Kinds-of-Intelligence-CFI/ADeLe-AIEvaluation/blob/agentic-v2/experiments/benchmarks/RESULTS.md).

**Setup.** One judge for everything: Claude Opus 5.5 at effort low, ADeLe's v2 annotation prompt, one call per task and
rubric. The judge sees what the agent sees, never tests, solutions or agent attempts. Each benchmark uses a clean set:
tasks named defective by an external review are dropped, and so are tasks no model solves. The outcome is each task's
solve rate across many models. The test is Spearman ρ between a rubric's level and solve rate. A good demand rubric
should give a negative ρ: higher demand, fewer solves.

## Results

ρ against solve rate on the clean set. "ns" = not significant (p ≥ 0.05). Levels are counts of tasks.

| benchmark | tasks | PLp | PLe | PLs | MSm / MSc |
|---|---|---|---|---|---|
| [SWE-bench Verified](https://github.com/Kinds-of-Intelligence-CFI/ADeLe-AIEvaluation/blob/agentic-v2/experiments/benchmarks/swebench-clean/RESULTS.md) | 443 | **−0.58**; levels 0–3 | −0.30 (423 at 3) | −0.09 ns (436 at 1) | all 0 |
| [ProgramBench](https://github.com/Kinds-of-Intelligence-CFI/ADeLe-AIEvaluation/blob/agentic-v2/experiments/benchmarks/programbench-pl/RESULTS.md) | 128 | **−0.48**; 2/3 = 24/104 | −0.09 ns | −0.09 ns | all 0 |
| [tau2](https://github.com/Kinds-of-Intelligence-CFI/ADeLe-AIEvaluation/blob/agentic-v2/experiments/benchmarks/tau2-clean/RESULTS.md) (within domain) | 242 | **−0.30**; mostly 2 | −0.07 ns | −0.20 | about 2; −0.07 ns / +0.09 ns |
| [DeepSWE](https://github.com/Kinds-of-Intelligence-CFI/ADeLe-AIEvaluation/blob/agentic-v2/experiments/benchmarks/deepswe-clean/RESULTS.md) | 90 | **−0.22** (p 0.04); 2/3 = 24/66 | 0.00 | −0.22 (p 0.03) | all 0 |
| [FrontierSWE](https://github.com/Kinds-of-Intelligence-CFI/ADeLe-AIEvaluation/blob/agentic-v2/experiments/benchmarks/frontierswe-pl/RESULTS.md) | 19 | −0.20 ns; 18 of 19 at 3 | +0.29 ns | +0.07 ns | about 0 |
| [Terminal-Bench 4.0](https://github.com/Kinds-of-Intelligence-CFI/ADeLe-AIEvaluation/blob/agentic-v2/experiments/benchmarks/tb4-clean/RESULTS.md) | 34 | +0.12 ns; 25 of 34 at 3 | −0.17 ns | −0.01 ns | about 0 |
| [TB-Science](https://github.com/Kinds-of-Intelligence-CFI/ADeLe-AIEvaluation/blob/agentic-v2/experiments/benchmarks/tbsci-pl/RESULTS.md) | 69 | +0.24 (wrong sign); 52 of 69 at 3 | 0.00 | +0.04 ns | about 0 |

MSm and MSc come from one study across all sets:
[ms-benchmarks](https://github.com/Kinds-of-Intelligence-CFI/ADeLe-AIEvaluation/blob/agentic-v2/experiments/benchmarks/ms-benchmarks/RESULTS.md).

## What it says

- **PLp tracks difficulty where planning drives it.** It works on SWE-bench Verified, ProgramBench, tau2 and DeepSWE.
  On ProgramBench it survives a control for prompt length.
- **PLp is flat where knowledge drives difficulty.** On Terminal-Bench 4.0 and TB-Science most tasks sit at PLp 3, and
  agents fail on domain knowledge and strict verifiers. A flat PLp is what the rubric should do there. On TB-Science
  PLp does rise with the authors' expert-hour estimates (+0.41).
- **PLp is coarse at the top.** Long projects sit at Level 3. On FrontierSWE, the tasks no model solves get Level 4
  more often (4 of 15, against 1 of 19). Across all 34 FrontierSWE tasks, PLp falls with mean reward (−0.36, p 0.04).
  Our clean-set rule therefore cuts off part of the top, though not all of it
  ([amendment 1](https://github.com/Kinds-of-Intelligence-CFI/ADeLe-AIEvaluation/blob/agentic-v2/experiments/benchmarks/frontierswe-pl/RESULTS.md)).
- **PLe and PLs barely vary on real tasks.** PLe is mostly 3 on coding work and goes higher on terminal tasks. PLs is
  mostly 0–2. Their signals are weak and secondary.
- **PLs is simulating in one's head (2026-10-04).** It stays low wherever the agent can run the system and look, which
  covers most sandboxed coding tasks. Three computer-world examples (systems that cannot be run first) were added at
  Levels 3–5 after a lab check
  ([pls-computer](https://github.com/Kinds-of-Intelligence-CFI/ADeLe-AIEvaluation/blob/agentic-v2/experiments/benchmarks/pls-computer/RESULTS.md)),
  and PLs was relabelled on all seven sets
  ([pls-relabel](https://github.com/Kinds-of-Intelligence-CFI/ADeLe-AIEvaluation/blob/agentic-v2/experiments/benchmarks/pls-relabel/RESULTS.md)).
  The PLs column above is the new labels. PLs fell on DeepSWE (Level 2 on 25 of 90, was 59) and now tracks its solve
  rate; on SWE-bench its weak signal halved (was −0.18).
- **MSm and MSc separate social from single-agent tasks.** They are 0 on every coding and terminal set and about 2 on
  tau2, the only set with another party. They do not track tau2 difficulty: tau2 tasks fail on procedure, which PLp
  reads. The social benchmarks below test them further.

## Social benchmarks (2026-10-03)

Three frontier benchmarks with other parties, labelled on all five rubrics to test MSm and MSc where social demand
should matter.

| benchmark | outcome | MSm / MSc levels | result |
|---|---|---|---|
| [EQ-Bench 4](https://github.com/Kinds-of-Intelligence-CFI/ADeLe-AIEvaluation/blob/agentic-v2/experiments/benchmarks/eqbench4-plms/RESULTS.md) (120 persona chats, 10 models) | new judged outcome: did the person disclose their hidden issue (κ 0.87; tracks Elo +0.85) | MSm 4 on 119; MSc 3 or 4 | no rubric tracks disclosure within source; MSm saturates |
| [CooperBench](https://github.com/Kinds-of-Intelligence-CFI/ADeLe-AIEvaluation/blob/agentic-v2/experiments/benchmarks/cooperbench-plms/RESULTS.md) (120 pairs, solo and coop) | drop in success from solo to coop | coop: MSm 3, MSc 2 on all; solo 0 | both rise with cooperation, but are flat across pairs; no link to the drop |
| [Game Arena](https://github.com/Kinds-of-Intelligence-CFI/ADeLe-AIEvaluation/blob/agentic-v2/experiments/benchmarks/gamearena-plms/RESULTS.md) (24 game × role) | none comparable across games | MSc 0 on board games, 4 on werewolf talk and bargaining | profiles as expected; a model's social-game edge does not match its EQ-Bench rating |

What it says: MSm and MSc separate social from non-social tasks reliably, but within a social benchmark they barely
vary, so they cannot rank social tasks by difficulty. What makes social tasks hard here (a defensive persona, a power
imbalance, colliding features) is not what the rubrics read.

## Controlled tests

- **Rivercross** (river-crossing puzzles,
  [rivercross-v2](https://github.com/Kinds-of-Intelligence-CFI/ADeLe-AIEvaluation/blob/agentic-v2/experiments/benchmarks/rivercross-v2/RESULTS.md)):
  PLp follows the length of the remaining solution, not how much search a state needs. PLs is constant at 2. PLe is 3
  on 52 of 54 states.
- **MS lab regression**
  ([ms-lab-regression](https://github.com/Kinds-of-Intelligence-CFI/ADeLe-AIEvaluation/blob/agentic-v2/experiments/benchmarks/ms-lab-regression/RESULTS.md)):
  today's judge and prompt reproduce the lab's MSm and MSc results (30 of 35 stored medians exact). Two
  pre-registered checks fail; neither is a judging problem.

## Data

Per-task labels and outcomes, ready to share, with a data card each (GitHub only for now):
[swebench-clean](https://github.com/Kinds-of-Intelligence-CFI/ADeLe-AIEvaluation/tree/agentic-v2/experiments/benchmarks/swebench-clean/release),
[tau2-clean](https://github.com/Kinds-of-Intelligence-CFI/ADeLe-AIEvaluation/tree/agentic-v2/experiments/benchmarks/tau2-clean/release),
[tbsci-pl](https://github.com/Kinds-of-Intelligence-CFI/ADeLe-AIEvaluation/tree/agentic-v2/experiments/benchmarks/tbsci-pl/release),
[deepswe-clean](https://github.com/Kinds-of-Intelligence-CFI/ADeLe-AIEvaluation/tree/agentic-v2/experiments/benchmarks/deepswe-clean/release),
[frontierswe-pl](https://github.com/Kinds-of-Intelligence-CFI/ADeLe-AIEvaluation/tree/agentic-v2/experiments/benchmarks/frontierswe-pl/release),
[programbench-pl](https://github.com/Kinds-of-Intelligence-CFI/ADeLe-AIEvaluation/tree/agentic-v2/experiments/benchmarks/programbench-pl/release).
The first three hold the planning labels only; the last three also hold MSm and MSc.

## Limits

- One judge, one sample per cell. Human labels exist only for small lab sets.
- Solve rates come from public leaderboards, with their own defects. Clean sets remove the known ones.
- Correlations are within benchmark. Comparing levels across benchmarks needs a common scale, which is future work.
