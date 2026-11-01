# Judging a subagent run in a Claude Code cloud session

The same judges as on the Mac (`.claude/agents/`, byte-identical to the pinned files), on a cloud VM. First used for
`w1v1-other` (2026-11), to spend Claude Code cloud credit instead of the weekly subscription.

## Once: the cloud environment (Pablo)

1. **Repository.** This repo, or a fork under your own account if the org has not approved the Claude GitHub app.
   A fork of this public repo is public too; nothing secret is ever committed (labels, ledgers, scripts only).
2. **Environment variables:**
   - `HF_TOKEN`: a read-only, fine-grained Hugging Face token for `adele-ai-evaluations/adele-instances` (make a
     new one for the cloud; do not reuse the write token).
   - `ADELE_JUDGE_IO=/root/judge-io` (any folder outside the repo; judges must not see a CLAUDE.md).
3. **Network access:** allow `huggingface.co`, `*.hf.co` (file downloads), `pypi.org`, `files.pythonhosted.org`
   and `github.com`.

## Each session

1. `scripts/cloud/bootstrap.sh <run>`. It installs `adele` in `.venv`, fetches the run's instance files (hash-checked),
   re-pins the run (it refuses unless every frozen input is identical), writes the prompts and unpacks the answer
   files judged elsewhere (`cloud-io/`).
2. `ADELE=.venv/bin/adele`, `REPO=$(git rev-parse --show-toplevel)`, `T=~/.claude/projects` (judge transcripts;
   `collect` and `check` keep only this run's).
3. **Pilot, first session only:** one relay of 50 cells, then stop and report, so Pablo can read how much credit
   it used.
   - `$ADELE mass next <run> --max 1 --batch-size 50 --cwd $REPO`;
   - launch the relay, collect, check (below);
   - commit, push, and report the cell count and the time taken.
4. **Rounds:**
   - `$ADELE mass next <run> --max 4 --cwd $REPO`.
   - Launch every printed relay in one message: one Agent call per block, `subagent_type` = the dispatcher on
     the `agent:` line, `description` = the handle, `prompt` = the text between the `===` lines exactly,
     `run_in_background: true`. Wait for all to finish.
   - `$ADELE mass collect <run> --transcripts $T --relays-done --cwd $REPO`, then
     `$ADELE mass check <run> --transcripts $T --cwd $REPO`. Stop and report if check fails.
   - `python3 scripts/cloud/responses.py pack <run>` (bare-digit answer files, so the Mac can verify them too).
   - Commit `runs/<run>/ledger.csv`, `labels.csv` and `cloud-io/<run>-responses.tsv` only, and push. Report one line: cells labelled, rejections,
     classifier stops.

## Rules

- **Never `cd`.** The judges inherit the session's working directory, and `check` verifies it.
- **Never commit anything from `data/`, the judge I/O folder, `.env` or `.venv`.** Task texts and prompts never
  enter git (`benchmark-contamination` rule). The pre-commit hook checks this.
- **Never launch judges directly**, never re-send a relay, never edit prompt or response files.
- **At most 4 relays at once.** Each is 4 subagents, and the default session cap is 20.
- **Stop when Pablo says**, at the time limit he gives, on any command error, or when credit runs out. This
  session cannot see the credit meter; Pablo watches it.
- A machine that also judges this run must not run it at the same time: one ledger, one writer.
- Back on the Mac, after merging: `python3 scripts/cloud/responses.py unpack <run>`, then `adele mass check <run>`. The
  protocol was checked on the VM, where the transcripts are; the ledger keeps each answer's verdict.
