# Mass annotation

One runner (`adele mass`, code in `src/adele/mass/`) for any grid of benchmarks × rubrics with any judge.
Design: `ARCHITECTURE.md`; plan and decisions: `PLAN.md`. Specs live in `specs/`, pinned runs in `runs/<name>/`
(`manifest.json`, `cells.csv`, `ledger.csv`, `labels.csv`); prompts and raw answers in `$ADELE_JUDGE_IO/<name>/`
(default `~/Developer/ADELE/judge-io`), never in the repo.

```
S=experiments/benchmarks/mass-annotation/specs/swebench-clean-v1.toml   # from the repo root
adele mass plan $S                               # cells, tokens, rough cost; writes nothing
adele mass pin  $S                               # freeze the run; prompts to $ADELE_JUDGE_IO
adele mass status swebench-clean-v1              # done / no label / in flight / to do
# subagent judges: in a Claude Code session at ~/Developer/ADELE, run /annotate swebench-clean-v1
#   (it loops: next --max 4 -> launch relays -> collect --transcripts ... --relays-done -> check)
# API judges (anthropic-batch, openai-batch, litellm):
adele mass run swebench-clean-v1 --dry-run       # then without --dry-run; rerun to resume
adele mass check swebench-clean-v1               # coverage, answer integrity, protocol (subagents)
adele mass release swebench-clean-v1 HANDLE      # cells of a relay/batch that never reached a judge -> pending
```
