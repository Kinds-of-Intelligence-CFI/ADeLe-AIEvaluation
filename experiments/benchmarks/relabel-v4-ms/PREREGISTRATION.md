# relabel-v4-ms — MSm and MSc relabelled after adoption (pre-registration)

Pablo, 2026-10-25: "Run the MS relabel now on subagents (bare digit, one repeat), keeping the current tau2 script input."

**What.** The two social rubrics as adopted on 2026-10-25 (`b05ddf3`; experiments/benchmarks/ms-candidate): MSc v4b and
the MSm candidate. Every released task that carries MS labels in label set `current` (1,413 tasks, 2,826 cells), in
five specs that copy the released ones (`relabel-v2`, `-long`, `-eqbench4`, `-cooperbench`, `-gamearena`) with two
changes: rubrics MSm and MSc only, and the bare-digit prompt (`v2-noreason`). tau2 keeps its frozen script text.
Judge: Opus 5.5 at effort low through Claude Code subagents, one repeat, the mass runner's retries.

**Prompt mix.** The other released rubrics were labelled with the reasoning prompt. The no-reasoning ablation
(experiments/benchmarks/noreason) and ms-candidate amendment 6 found bare digit agrees with reasoning within the
judge's own rerun noise (MSc 98% and MSm 90% exact on the lab items). The mix is recorded in the label set.

**Reported (no pass/fail; this is production):**
- per benchmark and rubric, the new labels against the released ones: exact, within one, the level counts;
- on the tau2 sets, MSc against Pablo's 15 agent-side labels (the ms-candidate items it covers);
- the criterion signals the benchmark studies report (MSm and MSc against solve rate where a study defined one).

**Then.** Label set `current` gets a `relabel-v4-ms` layer on top, so MSm and MSc come from this run; releases are
rebuilt with the new rubric hashes.
