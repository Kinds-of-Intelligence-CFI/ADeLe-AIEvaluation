# Jev vs Opus 5.5: diagnosis of 40 disagreements

Source: 40 cases, 8 per rubric (PLp, PLe, PLs, MSm, MSc). In each, Jev's top level differs from Opus 5.5's level.
Rubrics: `src/adele/rubrics/data_v2/Paolo_Pablo/{PLp,PLe,PLs,MSm,MSc}.txt`.
Jev writes no reasoning. So "Jev's likely error" is a guess, inferred from its probabilities and the rubric.

Column "Jev (p)" gives Jev's level, then Jev's probability for that level / for Opus's level.

## 1. Cases

| # | Rubric | Benchmark | Instance | Jev (p) | Opus | Deciding clause (rubric words) | Opus correct? | Jev's likely error |
|---|---|---|---|---|---|---|---|---|
| 1 | MSc | eqbench4 | hand_rd2_004_workplace_detector | 4 (.46/.27) | 3 | L4 note: "merely pained or displeased ... pursuing no outcome of its own, belongs below" | Yes. The user defends a belief out of fear; no rival goal. | Read "defensive, resistant user" as contest. Ignored the L4 carve-out. |
| 2 | MSc | eqbench4 | hand_eta_002_shame_armored_aggressor | 4 (.55/.26) | 3 | Same L4 note; L3 "content to be persuaded" | Arguable. Her wish for absolution could count as an outcome she pursues. | Same: defensiveness read as opposition. |
| 3 | MSc | eqbench4 | hand_rd2_006_moral_exile | 4 (.65/.17) | 3 | Same L4 note | Arguable. The urge to escalate publicly is close to an outcome of its own. | Same, with high confidence. |
| 4 | MSc | eqbench4 | d50dd97d | 4 (.41/.30) | 3 | Same L4 note | Yes. Hostile testing is defence, not a rival aim. | Took "challenges, dominance" as counter-moves. |
| 5 | MSc | eqbench4 | d02bd044 | 2 (.38/.37) | 3 | L3 "does not yet hold the view ... route runs through answering them" | Yes. Insight must be won against deflection. | Near-tie. Read a supportive chat as cooperative eliciting (L2). |
| 6 | MSc | tau2-airline | 46 | 1 (.34/.27) | 4 | L4 example "keep refusing a refund the policy does not allow" | Yes. Near-verbatim match to the L4 example. | Read a routine service script (L1). Missed that the user keeps pushing. Very flat distribution. |
| 7 | MSc | tau2-airline | 2 | 4 (.41/.37) | 2 | L2 "the other party is helping ... eliciting and arranging" | Yes. The compensation ask is gentle; the user cooperates. | Near-tie. Surface cue: airline complaint plus compensation, like the L4 refund example. |
| 8 | MSc | eqbench4 | abca3049 | 2 (.42/.35) | 3 | L3 "does not yet hold the view" | Yes. Reframing his "careful" stance is a stance to win. | Same as #5: supportive chat read as L2. |
| 9 | MSm | tau2-retail | 34 | 0 (.63/.13) | 3 | L3 "inferring specific mental properties" | No. Opus said 2-3 fit, then took 3 against the lower-level tie-break. Working out which items are "office" is not mind reading. Likely 2. | Defaulted to 0. Applied the "stated outright" carve-out to the whole task. |
| 10 | MSm | gamearena | word-art@artist | 0 (.35/.34) | 3 | L3 example "visualizing where the seeker might look" | Yes. Must predict how the guesser will read the drawing. | Near-tie. Read a drawing task as non-social. |
| 11 | MSm | gamearena | dark-hex@player | 0 (.59/.19) | 3 | L3 hide-and-seek example | No. Opus said 2-3 and "only weakly" 3; the tie-break gives 2. | Read a board game as Sudoku-like (L0 example). |
| 12 | MSm | tau2-retail | 44 | 0 (.44/.09) | 2 | L2 "basic intuition about the behaviour of others" | Yes. | L0 needs that interacting with others is "not necessary"; here it is. Over-applied the "stated outright" carve-out. |
| 13 | MSm | tau2-retail | 42 | 0 (.62/.07) | 2 | L2; tie-break between 2 and 3 | Yes. | Same as #12. |
| 14 | MSm | cooperbench | dspy_task-8563-f2-f5@coop | 0 (.28/.09) | 4 | L4 "clear distinction between self- and other-related representations" | Arguable. The partner's plans arrive as messages (stated stance), which points to 3. | Read a coding task; ignored the partner. Flat distribution. |
| 15 | MSm | tau2-retail | 74 | 0 (.38/.28) | 3 | L3 "inferring specific mental properties" | No. Opus said "fits Level 2 or Level 3", then took 3 against the tie-break. | Same as #12. |
| 16 | MSm | tau2-retail | 36 | 0 (.60/.07) | 2 | L2; carve-out for stated stances | Yes. | Same as #12. |
| 17 | PLe | swe-bench-verified | matplotlib-26342 | 0 (.52/.30) | 3 | L3 "checking is elected rather than forced" | Yes. | Read a small edit as a "single atomic action" (L0). |
| 18 | PLe | swe-bench-verified | django-15814 | 0 (.35/.21) | 3 | L3, same | Yes. | Same. |
| 19 | PLe | swe-bench-verified | matplotlib-26291 | 0 (.31/.31) | 3 | L3, same | Yes. | Exact tie between 0 and 3. |
| 20 | PLe | swe-bench-verified | django-16560 | 0 (.44/.34) | 3 | L3, same | Yes. Multi-site edit; easy to test. | Same as #17. |
| 21 | PLe | swe-bench-verified | django-16527 | 0 (.49/.25) | 3 | L3, same | Yes, low end. One line, but a check is still needed. | Took the "routine run off by rote ... makes no demand" note literally. |
| 22 | PLe | swe-bench-verified | pallets-flask-5014 | 0 (.60/.14) | 3 | L3, same | Yes. | Same as #21. |
| 23 | PLe | swe-bench-verified | django-15104 | 0 (.36/.21) | 3 | L3 "that a check runs on the environment's machinery does not matter" | Arguable. The fix is given; it sits near the rote-routine note. | Same as #21. |
| 24 | PLe | swe-bench-verified | django-13794 | 0 (.47/.34) | 3 | L3, same | Yes. | Same as #17. |
| 25 | PLp | swe-bench-verified | sympy-16792 | 0 (.34/.13) | 2 | L2 "divided into a few well-defined subtasks" | Yes. Debugging does not fix the actions (L1 note). | Read the issue as "the plan is given" (L0). |
| 26 | PLp | tau2-banking_knowledge | task_081 | 0 (.85/.06) | 2 | L2, same | Arguable. Opus calls the choices policy knowledge, which points to 1. | Read policy plus user order as "steps explicitly provided" (L0). High confidence. |
| 27 | PLp | cooperbench | outlines-1706-f1-f6@solo | 0 (.39/.17) | 2 | L2, same | Yes. The spec gives most of the decomposition. | Read the detailed spec as a given plan (L0). |
| 28 | PLp | cooperbench | outlines-1655-f1-f9@coop | 0 (.31/.23) | 2 | L2, same; "knowing how ... is knowledge" | Yes. | Stripped the regex work as knowledge, and stopped there. |
| 29 | PLp | swe-bench-verified | django-12262 | 0 (.64/.05) | 2 | L2, same | Yes. | Issue names the faulty check, read as a given plan. |
| 30 | PLp | swe-bench-verified | sphinx-9461 | 0 (.36/.29) | 3 | L3 "the decisions interact ... compared before committing" | Yes. | Missed the interacting choices. Second mode at 3. |
| 31 | PLp | cooperbench | jinja-1621-f5-f10@coop | 0 (.33/.27) | 3 | L3, same | Yes. Cache and alias placement interact. | Same as #30. |
| 32 | PLp | swe-bench-verified | astropy-12907 | 0 (.33/.14) | 2 | L2 vs L1 "single standard routine" | Arguable. Opus itself calls it borderline with 1. | Same as #25. |
| 33 | PLs | eqbench4 | 554550c2 | 5 (.44/.29) | 3 | L4 "a task whose answer survives a rough run belongs at the level below" | Yes. | Read an unpredictable human as "a model no one can be sure of" (L5). |
| 34 | PLs | eqbench4 | 5acf5f76 | 5 (.50/.24) | 3 | Same L4 note; L5 "model is agreed" note | Yes. | Same. |
| 35 | PLs | eqbench4 | 396ee5af | 5 (.54/.22) | 3 | Same | Yes. | Same. |
| 36 | PLs | eqbench4 | 6c2fbc51 | 5 (.50/.25) | 3 | Same | Yes. | Same. |
| 37 | PLs | eqbench4 | 2eb2e0bc | 5 (.56/.22) | 3 | Same | Yes. | Same. |
| 38 | PLs | terminal-bench-4.0.0 | photonic-waveguide-routing | 4 (.31/.29) | 0 | "optimising or checking a fixed configuration makes no demand" | Yes. | Near-tie. Read physics and hard optimisation as simulation. Ignored the carve-out. |
| 39 | PLs | frontierswe-v2 | quantum-espresso-pwx-in-rust | 4 (.47/.01) | 1 | "stays low wherever the solver can run the system and look" | Yes. | The task is about a simulation code, so Jev scored it high. Ignored the run-and-look carve-out. |
| 40 | PLs | eqbench4 | 8e40ff8c | 5 (.53/.24) | 3 | Same as #33 | Yes. | Same as #33. |

## 2. Per-rubric summaries

**MSc.** Yes, one question explains 6 of 8: does the other party pursue an outcome of its own (L4), or only defend and doubt (L3)? Jev says 4 for four defensive eqbench personas and for a mild compensation ask (#7). It says 1 for a clear refund demand that matches the L4 example (#6). The other 2 (#5, #8) sit at the L2/L3 line: does the person already hold the stance? On eqbench Jev spreads mass over 2, 3 and 4 and rarely picks 3. Opus: 6 yes, 2 arguable.

**MSm.** Yes, one failure explains 8 of 8: Jev picks 0 every time. Level 0 needs that dealing with the other agent is "not necessary". In all 8 cases another agent must be served or anticipated. Jev puts little mass on 1-2 and splits between 0 and 3. Best guess: Jev stretches the "stated outright" carve-out to the whole task, or reads tool, game and coding framing as non-social. Opus is also weak here. In 3 cases (#9, #11, #15) it said 2 and 3 both fit, then took 3 against the tie-break. The likely right level there is 2. So 3 of these 8 "disagreements" are partly Opus errors.

**PLe.** Yes, one failure explains 8 of 8. All are SWE-bench Verified fixes: Jev says 0, Opus says 3. The deciding clause is L3: "checking is elected rather than forced", and a check on the environment's machinery still counts. Jev treats a small local fix as one atomic action, or as a rote routine needing no check. Its second mode is 3 (p .14-.34), with little mass at 1-2. Opus applies the rubric correctly. Only the tiniest given fixes (#23) are arguable.

**PLp.** Yes, one failure explains 8 of 8: Jev says 0 every time. Opus says 2 in six cases (L2, few independent subtasks) and 3 in two (L3, interacting choices). Best guess: Jev reads an issue that names the bug, or a detailed spec, as "a sequence of steps that is explicitly provided" (L0). Opus is mostly right. The L1/L2 line is arguable for routine debug fixes (#32) and the policy-driven banking task (#26).

**PLs.** Yes, one failure explains 6 of 8. On eqbench Jev says 5 and Opus says 3. Jev reads an unpredictable human as a model no one can trust. It ignores two notes: a rough run that still works keeps the task below 4, and an uncertain outcome alone does not place a task at 5. Jev also skips 4 (p .12-.17), which points to a surface match with the social feedback loops in the L5 examples. The other 2 cases (#38, #39) are carve-out misses: a fixed configuration, and a system the solver can run and look at. Opus is right on all 8.

**Across rubrics.** Jev's top level is at an extreme (0 or 5) in 30 of 40 cases. Its mass at the middle-low levels (1-2) is thin in PLe, PLp and MSm. In 5 of 40 cases (#5, #7, #10, #19, #38) the two levels are within 0.05 in Jev's probabilities, so the disagreement is a near-tie.

## 3. Proposed yes/no sub-questions

Ask each separately. Check carve-outs first. Then take the highest level whose question gets a yes. The starred questions would most likely fix the disagreements above.

**PLe (Action control)**
- E0* Does the task take more than one action, such as several edits, tool calls or written sections? (No: 0.)
- E1 Does the environment report, after nearly every action, whether it worked?
- E2 Without being asked, does the environment check the work at natural points, such as a stage that will not run until it is right?
- E3* Can the agent easily check its own work whenever it chooses, such as by running the code, re-reading, or comparing with the source?
- E4 Do errors stay silent where they happen, and show only far from their cause?
- E5 Is checking needed but impossible until the outcome is settled?

**PLp (Planning)**
- P0* Is the full sequence of steps given, or is the task one action? (An issue that names the bug, or a spec, does not by itself give the plan.)
- P1 Does one standard routine fix all the actions, not just the kind of task?
- P2 Must the task be split into several subtasks?
- P3* Can a choice that looks good now fail because of a later step, so options must be compared before committing?
- P4 Must the split into subtasks itself be discovered, with no template?

**MSm (Mind modelling)**
- M0* To do the task well, must the solver deal with or anticipate another agent? (No: 0.)
- M2* Does doing well depend on reading the other agent's behaviour, such as hesitancy, terse replies or preferences?
- M3 Must the solver infer a specific belief, want or reading that the other agent has not stated?
- M4 Must the solver reason explicitly about a mental state that differs from its own view, such as a false belief, hidden knowledge, or doubted sincerity?
- Mc Has the other agent stated a given want and its reasons outright, with no reason to doubt them? (Applies to that want only, not the whole task.)

**MSc (Communication)**
- C1 Does anything the solver must say depend on the other party's replies?
- C2 Does the other party already hold, or readily give, what the task needs, so the work is only eliciting?
- C3 Must the solver change the party's view, decision or acceptance?
- C4* Does the other party pursue a concrete outcome of its own that conflicts with the task's aim (for example a refund, or keeping a lease)? Or are they only hurt, defensive or doubtful?
- C5 Are there two or more parties whose required positions cannot all hold at once?

**PLs (Simulating)**
- S0* Does anything in the situation change over the course? Or is the task to optimise or check a fixed configuration?
- S1* Can the solver run the system, or a trusted model of it, look at the result, and repeat as needed?
- S2 Does a known rule give the whole course?
- S3 Do parts act on each other (feedback), so leaving the coupling out gives the wrong answer?
- S4* Would two nearly identical courses end far enough apart to change the answer, so a rough run fails?
- S5* Is there no agreed model of the situation, as opposed to an outcome that is merely uncertain?
