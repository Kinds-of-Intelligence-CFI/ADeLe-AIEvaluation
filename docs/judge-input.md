# What the judge sees: the task input rule

A demand label rates the task. So the judge must see the task as the agent faces it, and what the task asks for. It
must not see how to solve it or how the solution is checked.

Pablo's rulings, 2026-10-26:
- "the judge should see the goal in all benchmarks too, if available"
- for the coding and terminal sets: "Actually skip the tests, I think it is not relevant in this case. But it should be
  clear what is the goal without those tests."
- for tau2: "keep the goal and drop the expected-action list."

## The rule

The judge sees three things:
1. **What the agent is given.** The issue, `instruction.md` or prompt, verbatim. Where the agent works under a policy
   or with tools and data, those too.
2. **Hidden parts of the setting that shape the task.** For example, the script a simulated user follows.
3. **The goal: what counts as success, in prose.** What must be true at the end, and what the agent must deliver or
   say.

The judge never sees:
- tests, test names or test code;
- reference solutions: gold patches, `solution/` folders, or lists of expected actions or tool calls;
- any agent's attempt.

The line: success criteria written in prose are in, even when they come from the grader. Checking code and solution
steps are out.

## How each benchmark applies it

| set | goal shown | built by |
|---|---|---|
| tau2 (airline, retail, banking_knowledge) | The task's own data: the designer's purpose, what the agent must tell the customer, the outcome checks (prose assertions), what the reward is based on, known task issues. Also shown: the domain policy, the agent's tools, the records it can look up, the customer's script and the standing simulator rules. Not shown: the expected agent and customer actions. | `experiments/benchmarks/tau2-goal/build.py` |
| FrontierSWE | Each task's public "Task" and "Verification" sections (prose). | `experiments/benchmarks/goal-visible/build.py` |
| SWE-bench Verified, DeepSWE | A goal statement per set, written from the benchmark's public docs, naming the repository (DeepSWE also the language). | same |
| ProgramBench, Terminal-Bench 4.0, TB-Science | A goal statement per set, written from the benchmark's public docs. | same |

The original task text is always kept verbatim. Each builder checks it against its frozen hash.

## Caveat: tau2 record selection

The tau2 records the judge sees (the customer's account, reservations, orders, products, required documents) were
picked with ids taken from the grader's criteria (`msc-l4-note/make_agent_worksheets.py`, `records`). So the judge
learns which records the task touches, though not what should be done to them. A cleaner selection would use only what
the customer's script gives; where it names no id, the account would be found from the name and zip code it gives.

## Practical rules for builders

- Never commit task text, tests or solutions. Instance folders live in gitignored `data/`.
- No line over 2,000 chars. The Read tool cuts longer lines, and `adele mass check` catches this only for the chunked
  judge. Write JSON bodies (for example, documents) as plain text.
- Send a task to the chunked judge, with all its rubrics, when any rubric's prompt exceeds 50,000 chars or 1,500 lines.
- Keep judged texts byte-identical when rebuilding. The tau2 `records` helper collects ids in a set, so its order can
  change between runs; copy judged files rather than regenerating them.

## Where the decisions are recorded

`experiments/benchmarks/tau2-full/PREREGISTRATION.md` (full task, amendment 1),
`experiments/benchmarks/tau2-goal/PREREGISTRATION.md` (production tau2 input),
`experiments/benchmarks/goal-visible/PREREGISTRATION.md` (coding and terminal sets).
