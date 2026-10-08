# Running annotation runs

This guide is for anyone who wants to run an ADeLe annotation run: our planned bulk runs, or the same runs with
another judge model. It assumes a fresh clone of the `agentic-v2` branch.

What is decided, and why, is in `BENCHMARKS.md` (which tasks), `PLAN.md` (the gates and the order) and
`noreason/RESULTS.md` (which judge).

## Rules first

The repository is public. Some of our benchmarks carry canary strings or ask that their items never be posted. So:
- **Never commit task texts, judge prompts, judge answers or agent traces.** They live in `data/` and in the judge-io
  folder, both outside git. Commit only specs, run folders (ids, hashes, levels), code and documents.
- **Install the guard once per clone:** `sh scripts/install-hooks.sh`. Before every commit it refuses trace files and
  checks the staged files against every task text you hold. Never bypass it with `--no-verify`.
- **Don't launch a bulk run without the maintainer's go.** The gates in `PLAN.md` come first.

## 1. Install

```
python -m venv .venv && . .venv/bin/activate
pip install -e ".[dev]"
sh scripts/install-hooks.sh
```

Put API keys in a `.env` file at the repository root. It is gitignored, and `adele` reads it on start:

```
ANTHROPIC_API_KEY=...     # for backend "anthropic-batch"
OPENAI_API_KEY=...        # for backend "openai-batch", or litellm with OpenAI models
HF_TOKEN=...              # read access to the private instance dataset
```

## 2. Get the task texts

The frozen task texts are in a **private** Hugging Face dataset. Ask the maintainer for read access. The repository
holds only their index, `INSTANCES.tsv` in this folder: names, counts and sha256s, no text.

```
adele instances fetch                          # all benchmarks into data/instances/
adele instances fetch --benchmark eqbench4     # or some of them
```

Every file is checked against the committed sha256. A mismatch stops the fetch and deletes the file.

The maintainer pushes new or changed benchmarks with `adele instances push`, which refuses a public dataset, and
commits the updated index.

## 3. Run

A run is a spec (a TOML file in `specs/`) frozen into a run folder. These steps work for any API backend.

```
adele mass plan specs/gate-dryrun.toml      # cells, tokens and cost; writes nothing
adele mass pin specs/gate-dryrun.toml       # freezes cells and hashes into runs/gate-dryrun/, writes the prompts
adele mass run gate-dryrun --dry-run        # shows one request; contacts no API
adele mass run gate-dryrun                  # submits batches, polls, fetches; rerun to resume after any stop
adele mass collect gate-dryrun              # parses answers into runs/gate-dryrun/labels.csv
adele mass check gate-dryrun                # every label traced to an answer file
adele mass status gate-dryrun
```

- **Resuming is safe.** Every step saves the ledger, so rerunning `adele mass run` never sends a cell twice.
- **Raw answers stay outside the repo.** Prompts and answers go to `$ADELE_JUDGE_IO`, by default
  `~/Developer/ADELE/judge-io`.
- **Commit the run folder** (`runs/<name>/`: manifest, cells, ledger, labels) on a branch, and open a pull request.
  CI checks it for traces and canaries.
- **Specs are frozen once pinned.** To change anything, give the spec a new name.

Inside Claude Code, the maintainer can also run specs with `backend = "subagent"` through the `/annotate` skill.

## 4. Use another judge model

The runner is judge-agnostic.

| backend | providers | effort setting |
|---|---|---|
| `anthropic-batch` | Claude | `output_config.effort` |
| `openai-batch` | OpenAI | `reasoning_effort` |
| `litellm` | most others | `reasoning_effort` |

Keep `builder = "v2-noreason"`: the bare-digit prompt works for any model.

A different judge labels differently, so its labels are never mixed with ours unchecked.

1. **Qualify it first.** Copy `specs/qualify-judge-pl.toml.example` and `specs/qualify-judge-ms.toml.example`, set
   the names and the `[judge]` table, then plan, pin, run and collect both. That's 530 calls on our reference
   subset. Then run:
   ```
   python experiments/benchmarks/mass-annotation/qualify_judge.py qualify-<judge>-pl qualify-<judge>-ms
   ```
   It compares the new judge's agreement with our released labels against our production judge's, rubric by rubric,
   and prints **qualified**, **mixed** or **not qualified**. For reference: our production judge qualifies, Sonnet
   5.5 without reasoning is mixed, and Sonnet 5.5 with reasoning is not qualified.
2. **Then run the bulk specs** under new names, with your `[judge]` table.
3. **Keep its labels in their own label set** (`labelsets/<judge>.toml`). A label set takes labels from one model
   only.

`adele mass plan` knows prices for Claude models only. For others, pass `--usd-in` and `--usd-out` (USD per million
tokens).

## 5. Label sets and exports

A label set names the runs that make up a set of labels, in order of precedence. `labelsets/current.toml` is the
released v2 set.

```
adele mass labelset current                                   # summary
adele mass labelset current --out /tmp/x --format parquet     # export: long, wide, rubrics, MANIFEST.tsv
```

Every label carries its run, judge, prompt hash, `rubric_sha256` (the rubric text judged) and `task_version` (the
frozen task frame). To change what "current" means, edit the TOML in a pull request, not code.

## Troubleshooting

- **`benchmark ... is not in INSTANCES.tsv`.** Run `adele instances fetch` for it.
- **`... no longer matches its sha256`.** Your local task file differs from the committed index. Fetch it again.
- **`exists and was pinned from different inputs`.** You changed a spec, rubric or task file after pinning. Use a
  new spec name.
- **The pre-commit hook flags a file.** Remove the task text from it. If you are sure it is safe (for example, public
  licence text), ask the maintainer to add it to `contamination_allow.tsv` with a reason.
