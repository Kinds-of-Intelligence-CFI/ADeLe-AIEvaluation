# Mass annotation runner — architecture (draft for approval, 2026-10-01)

**Aim.** Launching an annotation run on any grid of (benchmarks × rubrics) is one command, with any judge
(Claude Code subagents, Claude Code cloud sessions, Anthropic or OpenAI batch APIs, any litellm model), and every run
is resumable, auditable and produces labels in one schema. Nothing is run by this work; it only builds the machinery.

## Today

- `adele.annotation.annotate()`: OpenAI Batch or litellm, v1 prompt only, no job-id persistence (an interrupted batch
  is lost), records `run_info.json` but not the instance manifest.
- Every recent study (`swebench-pl` … `plp-o-relabel`) re-implements prompt pinning, relay batching, `writers.py`,
  `collect.py` and protocol checks as per-study scripts around Claude Code subagents.
- Rubric acronyms collide across generations (`MSm` in v1 and v2). Rivercross is not a registered benchmark.

## Design

Five pieces, each with one job. `annotate()` and the v1 prompt stay untouched (v1 reproduction).

```
spec.toml ──plan──► cost/size report (no side effects)
    │
    └──pin──► run/  manifest.json   (hashes: spec, git commit, rubric files, instance files, prompt builder, judge)
                    cells.parquet   (cell_id, benchmark, instance_id, rubric_ref, repeat, prompt_sha256)
                    ledger.parquet  (per cell and attempt: status, backend handle, writer model, reason)
              $ADELE_JUDGE_IO/run/prompts/<cell_id>.txt     (prompt text: outside the repo)
                    │
        submit / poll / fetch   ◄── JudgeBackend (subagent | anthropic-batch | openai-batch | litellm)
                    │
              collect ──► labels.parquet (one schema for every backend) ──► analyses
              check   ──► protocol and writer report
```

**1. Spec** (TOML, committed): what to annotate and with which judge.

```toml
name = "tier1-v1-v2"
[tasks]
benchmarks = ["tau2-airline", "tau2-retail", "rivercross-1b"]
subset = "solvable"                 # or a file of instance ids
[rubrics]
refs = ["v1/AS", "v1/AT", "...", "v2/MSm", "v2/MSc"]   # generation-qualified; memory added by editing this list
[prompt]
builder = "v2"
[judge]
backend = "subagent"               # or "anthropic-batch", "openai-batch", "litellm"
model = "claude-opus-5-5"
effort = "low"
repeats = 1
retry = { fallback_writer = 1, unparsed = 1 }
```

**2. Pin** freezes the spec into an immutable run: every cell and every prompt hashed, the manifest recording the
commit and the sha256 of each rubric and instance file. Cell ids are short, safe (no `__`, no `/`), and stable.
Re-pinning the same spec at the same commit gives the same cells.

**3. Ledger** is the single source of truth for progress: one row per cell attempt (pending, submitted with its backend
handle, answered, parsed, rejected with a reason, retried). Every command reads and writes it, so any command can
stop and any session can resume. Batch job ids live here, which fixes today's batch-loss problem.

**4. Judge backends** share one small interface:

```python
class JudgeBackend(Protocol):
    def submit(self, run, cells) -> list[Handle]   # recorded in the ledger
    def poll(self, run, handles) -> dict[Handle, Status]
    def fetch(self, run, handles) -> Iterable[Answer]   # cell_id, text, writer_model, usage
```

| backend | submit | writer check | notes |
|---|---|---|---|
| `subagent` | writes relay batches; a project skill (`/annotate <run>`) launches up to 4 relays and resumes | from transcripts (today's `writers.py`, generalised) | the current Opus-low setup; works the same in a cloud session (the $250 credits) |
| `anthropic-batch` | Message Batches API | `model` field of each response | new; effort as an API parameter |
| `openai-batch` | Batch API, reusing today's request builders | `model` field | job ids now persisted |
| `litellm` | direct calls, any provider | `model` field | small runs and local models |

A judge change is a spec change, so a run with an OpenAI judge is the same command with a different `[judge]`.

**5. Collect and check.** `collect` parses with `extract_demand_level`, applies the writer rule (an answer by a model
other than the requested one is rejected and retried per the spec), and writes `labels.parquet`:
run, cell_id, benchmark, instance_id, rubric_ref, generation, repeat, backend, model_requested, writer_model, effort,
prompt_builder, prompt_sha256, level, valid, response_sha256, attempt. Raw answers stay in the gitignored `data/`.
`check` runs the protocol checks (for subagents: exact message, working directory, no CLAUDE.md, Read then Write)
and a coverage report.

## Commands

```
adele mass plan   SPEC            # cells, tokens, cost per backend; the cost gate; no side effects
adele mass pin    SPEC            # creates the run
adele mass run    RUN             # API backends: submit, poll, fetch, collect until done (resumable)
adele mass next   RUN --max 4     # subagent backend: emit the next relay batches (the skill calls this)
adele mass collect RUN
adele mass check  RUN
adele mass status RUN             # done / pending / rejected, by benchmark and rubric
```

For subagents, launching is `/annotate <run>` in any Claude Code session. The skill runs `next`, launches the relays,
and runs `collect` and `status` when they finish.

## Also needed

- **Benchmark loaders:** rivercross (the states as instances, through `BENCH_LOADERS` and `CANONICALIZERS`); WeirdML v2's
  six public tasks if the team wants them; others as the team picks.
- **Prompt option:** `prompt.builder = "v1" | "v2"`, resolved by name, so old runs stay reproducible.
- **Rubric refs:** `v1/<code>` and `v2/<code>` resolve against `data_v1` and the v2 manifest; `verify_manifest` runs at pin.

## Where it lives

`src/adele/mass/` (new subpackage: spec, pin, ledger, backends, collect, check, cli), additive, with tests on a toy
grid using a fake in-memory backend (resume, retry, writer rejection, id safety, manifest hashes) and a fake transcript
folder for the subagent backend. Specs and runs live in `experiments/benchmarks/mass-annotation/`. The studies' old
scripts stay as they are.

## Implementation notes (2026-10-01): where the code departs from the above, and why

- **CSV, not parquet**, for `cells`, `ledger` and `labels`: run folders are committed, and the repo keeps generated
  tables as plain text so they diff in review (see `.gitattributes`).
- **Raw answers** live next to the prompts in `$ADELE_JUDGE_IO/<run>/responses/`, not in `data/`: the subagent
  judges write there, and every backend now keeps answers in one place outside the repo.
- **`subset`** is a file path only (a CSV with `instance_id`, optional `benchmark` and `keep`); no named subsets yet.
- **Retries** write to `responses/<folder>-a<n>/` instead of moving the first answer to `responses_fallback/`;
  nothing is moved, and each attempt keeps its own file. Retry budgets exist per reason: `fallback_writer`,
  `unparsed`, `refusal` (API safety stop) and `error` (no answer); each defaults to 1.
- **Interface:** `submit(run, items) -> handle` sends one group; `fetch(run, handle, items)` returns one answer per item.
- **Subagent rounds are lockstep:** `next` refuses while relays are outstanding, and `collect --relays-done` settles
  them (a cell no judge received goes back to pending without using an attempt). An answer file that matches no
  Write call or harness confirmation in the given transcripts stops `collect` instead of being rejected, so a wrong
  transcripts folder cannot trigger relaunches.
- **API backends** request no server-side fallback model: an answer by another model would be rejected anyway.
  Batch creation runs without SDK retries, so a lost response cannot leave a second, unrecorded batch.
- **Protocol rule (subagents):** an answer whose judge transcript breaks the protocol (message, working directory,
  tools, attachments, effort, agent, or the cell judged twice) is rejected as `protocol` and retried within budget;
  `labels.csv` carries `protocol_ok`. `next` and `check` also refuse judge/dispatcher agent files changed since pin.
- **Safety valves:** every mutating command holds `<run>/.lock`; `adele mass release RUN (HANDLE...|--all)` returns
  cells of relays or batches that never reached a judge to pending; such returns are capped at 3 per attempt
  (then `error`).

## Out of scope here

Choosing benchmarks and the memory rubrics (team), running anything, the pre-registered analyses.
