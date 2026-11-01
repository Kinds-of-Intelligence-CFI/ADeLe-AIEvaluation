# Judging a subagent run in a Claude Code cloud session

The same judges as on the Mac (`.claude/agents/`, byte-identical to the pinned files), on a cloud VM. First used for
`w1v1-other` (2026-11), to spend Claude Code cloud credit instead of the weekly subscription.

State moves between machines through a **private Hugging Face dataset**, `adele-ai-evaluations/adele-cloud-runs`:
the ledger, the labels, the answer files, the relays and the judge transcripts (`scripts/cloud/hf_sync.py`). The
cloud session commits nothing to git.

## Once: the cloud environment (Pablo)

1. **Repository.** The private mirror `PabloAMC/ADeLe-AIEvaluation-cloud`, branch `cloud/w1v1-other`. It's a snapshot
   of `agentic-v2` without the 16 LFS battery files: the org's LFS budget is spent, and judging does not need them.
   Never merge it anywhere.
2. **Environment variable** `HF_TOKEN`, a fine-grained Hugging Face token with:
   - read on `adele-ai-evaluations/adele-instances`;
   - write on `adele-ai-evaluations/adele-cloud-runs`.

   The judge I/O folder defaults to `~/judge-io`, outside the repo, because judges must not see a CLAUDE.md.
3. **Network access:** allow `huggingface.co`, `*.hf.co` (file downloads), `pypi.org`, `files.pythonhosted.org` and
   `github.com`.

## Before each cloud session (Mac)

Stop judging the run on the Mac, then `python scripts/cloud/hf_sync.py push <run>` with the repo's venv. One ledger,
one writer.

## Each session (cloud)

1. `scripts/cloud/bootstrap.sh <run>`. It:
   - installs `adele` in `.venv`;
   - fetches the run's instance files (hash-checked);
   - re-pins the run, which it refuses unless every frozen input is identical;
   - writes the prompts;
   - pulls the run's state from the dataset.
2. `ADELE=.venv/bin/adele`, `PY=.venv/bin/python`, `REPO=$(git rev-parse --show-toplevel)`, `T=~/.claude/projects`
   (judge transcripts; `collect` and `check` keep only this run's).
3. **Pilot, first session only:** one round of 50 cells, then stop and report, so Pablo can read how much credit it
   used: `$ADELE mass next <run> --max 1 --batch-size 50 --cwd $REPO --direct`, then launch, collect, check and sync
   as below. Report the cell count and the time taken.
4. **Rounds of 100 cells** (`wave1-v1` amendment 1: in a cloud session subagents cannot start subagents, so this
   session starts the judges itself):
   - `$ADELE mass next <run> --max 1 --batch-size 100 --cwd $REPO --direct`. It prints `agent: adele-judge-v2-low`
     and one `=== <cell> ===` ... `=== end ===` block per cell.
   - Start the judges ten per message, every call `run_in_background: true`:
     - `subagent_type` = `adele-judge-v2-low`;
     - `model` = `opus`;
     - `description` = the cell;
     - `prompt` = the two lines between that cell's `===` lines, exactly.

     Send the next ten when the previous ten have all finished. A call that fails with a concurrency-limit error is
     sent again; no other cell is sent twice.
   - When every cell of the round has finished: `$ADELE mass collect <run> --transcripts $T --relays-done --cwd $REPO`,
     then `$ADELE mass check <run> --transcripts $T --cwd $REPO`. Stop and report if check fails.
   - `$PY scripts/cloud/hf_sync.py push <run>`. Report one line: cells labelled, rejections, classifier stops.
5. **End the session after about 1,000 cells** (ten rounds), because each start adds to this session's context.
   Push, then report "start a new session". The next session's bootstrap pulls the state from the dataset.

## Rules

- **Never `cd`.** The judges inherit the session's working directory, and `check` verifies it.
- **Never commit or push anything** from the cloud session. Task texts, prompts and transcripts go only to the
  private datasets (`benchmark-contamination` rule).
- **Start only `adele-judge-v2-low`,** with exactly the printed instruction. Never send a cell twice (except after
  a concurrency-limit error), and never edit prompt or response files.
- **At most ten judges at once.** The default session cap is 20 subagents.
- **Stop when Pablo says**, at the time limit he gives, on any command error, or when credit runs out. This session
  can't see the credit meter; Pablo watches it.

## Back on the Mac

`python scripts/cloud/hf_sync.py pull <run>`. It refuses if the cloud ledger lost or changed an answer recorded here.
Then:
- run `adele mass check <run>`;
- commit `runs/<run>/ledger.csv` and `labels.csv` to `agentic-v2`.

The protocol was checked on the VM. The transcripts sit in `data/cloud-runs/<run>/transcripts/` (gitignored) for any
re-audit.
