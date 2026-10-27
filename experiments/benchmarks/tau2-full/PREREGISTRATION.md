# tau2-full — the full task as the tau2 judge input (pre-registration)

Pablo, 2026-10-26: "Agree, make the full task the tau2 input for all rubrics." Asked what the full task holds, he chose
to include how the run is graded and the database records the task touches.

**Why.** Until now the tau2 judge has read only the simulated customer's script (`_taubench_prompt`; chosen in
`tau2-tb4-pl` because the policy and tools are the same for every task of a domain). But the agent's job depends on
how the policy applies to each task. The same script can mean a polite refusal or a real change. In ms-candidate,
MSc v4b matched Pablo's 15 agent-side labels 15 times on the full task and 9 times on the script; relabel-v4-ms, on the
script, matched 10.

## Input

The agent-side worksheet's parts 1 to 3 (`msc-l4-note/make_agent_worksheets.py`), with the policy and the simulator
rules written in, as ms-candidate judged them:
1. what the agent is given: the domain policy, its tools, and the database records it can look up for this task;
2. what the simulated customer is given: the script (the frozen task text, hash-checked) and the standing rules;
3. how the run is graded: expected actions, information the agent must give, outcome checks, known task issues.

Built by `build.py` into `data/instances-tau2-full/` (gitignored; task text is never committed). For the 14 airline
and retail worksheet items, the text is identical to ms-candidate's full-task input (checked by the build).

**banking_knowledge** has no single policy file. Its policy here is the two prompt components that every retrieval
set-up shares (`policy_header.md`, `additional_instructions.md`), plus a line on the 698-document knowledge base. The
records are the task's required documents, as in the worksheets. (The one banking worksheet item, H-12, had only
the knowledge-base line, so its text differs from ms-candidate's.)

**What the judge now sees that it did not.** The goal and how it is graded (part 3), for every rubric. Pablo,
2026-10-26: "the judge should see the goal in all benchmarks too, if available (perhaps with access to the tests,
although I do not think they are strictly needed)." The coding and terminal sets do not yet show their goal (their
judges see the problem statement or `instruction.md` only); bringing them in line is a separate study. Until then
tau2 is the one agentic set whose judge sees the grader.

## Design

- **Tasks.** The 242 released tau2 tasks (airline 49, retail 114, banking 79), as in `pls-relabel/subset.csv`.
- **Rubrics.** All five released on tau2: PLp, PLe, PLs, MSm, MSc (current `src/` texts).
- **Runs.** `tau2-full` (217 tasks, 1,085 cells). `tau2-full-long` (25 banking tasks, 125 cells): every task with a
  prompt over 50,000 chars or 1,500 lines under any rubric (the programbench-pl rule) goes, with all five rubrics,
  to the chunked-read judge. Specs in `../mass-annotation/specs/`.
- **Judge.** Opus 5.5, effort low, Claude Code subagents, bare-digit prompt (`v2-noreason`), one repeat, the mass
  runner's retries. Planner estimate: about 6 weekly points.

## Reported

1. Per benchmark and rubric: new against released labels (label set `current`): exact, within one, level counts.
   For MSm and MSc also against `relabel-v4-ms` (same rubric text and prompt, script input), which isolates the input.
   For the PL rubrics the released labels used the reasoning prompt, so that contrast mixes input and prompt.
2. Criterion signals: each rubric against solve rate, within domain, as `ms-benchmarks` (`tau2-clean` outcomes).
3. MSc against Pablo's 15 labels (his revisions included), as in `relabel-v4-ms`.

## Sealed predictions

| prediction | probability |
|---|---|
| MSc matches Pablo's revised labels exactly on at least 13 of 15 | 0.75 |
| More tau2 MSc labels at Level 1 than in relabel-v4-ms (29 of 242) | 0.75 |
| PLp keeps a negative within-domain signal with p < 0.05 (released: −0.28) | 0.6 |
| MSc has a negative within-domain signal with p < 0.05 (relabel-v4-ms: −0.14, p 0.04) | 0.5 |

## Then

If Pablo agrees: label set `current` gets a `tau2-full` layer on top for the three tau2 benchmarks and five rubrics,
and the tau2 release is rebuilt. Nothing changes before his OK.

## Amendment 1 (2026-10-26, after the first labels): banking re-judged as plain text

**What happened.** The build wrote each banking knowledge-base document as JSON, so a document's body sat on one
line, up to 6,414 chars. The judges read prompts with the Read tool, which cuts lines over 2,000 chars, so they saw
only the start of those documents. The chunked judge's check caught it: all 125 `tau2-full-long` answers were
rejected. The single-read check does not look at line length, so 185 `tau2-full` cells (37 banking tasks) were
labelled on cut text and passed. Airline and retail have no line over 2,000 chars; their 690 labels stand.

**Change (Pablo: "rebuild banking with the documents as plain text, add a long-line check to the builder, amend the
pre-registration, and re-judge all 79 banking tasks").** Banking documents are now plain text (id, title, body with
real line breaks; same content; longest line 1,380 chars). The builder fails on any line over 2,000 chars. The new
texts are in `data/instances-tau2-full-v2/`; airline and retail there are byte copies of the first build (a rebuild
could order records differently, because the worksheet code collects ids in a set). All 79 banking tasks are
re-judged in `tau2-full-banking` (55 tasks, 275 cells) and `tau2-full-banking-long` (24 tasks, 120 cells, chunked
judge), split by the same rule. Every `tau2-full` banking label and the `tau2-full-long` run are set aside.

**Labels used.** Airline and retail from `tau2-full`; banking from the two new runs. Designs, reports and sealed
predictions are unchanged.

## Calls made without asking (for veto)

- No separate 15-item gate before the full run. The MSc inputs for 14 of the 15 items are already proven identical
  to the ones that matched Pablo, and the other rubrics have no human labels to gate on. The 15 items are reported
  inside the full run instead.
- The banking policy text described above.
- Routing whole tasks, not single cells, to the chunked judge, so all five rubrics of a task use the same judge.
