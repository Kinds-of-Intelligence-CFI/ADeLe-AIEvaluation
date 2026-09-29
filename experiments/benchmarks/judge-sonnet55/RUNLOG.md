# judge-sonnet55 — run log

## 2026-09-29 — probe and pinned run `s55h-gate`

- **Probe.** One throwaway call (`adele-judge-low`, model alias `sonnet`) on a non-study prompt: the
  answer was written by `claude-sonnet-5-5`. On 2026-09-28 the same alias still gave
  `claude-sonnet-5`.
- **Pinned run.** `make_run.py` copied the 88 PLp and PLe prompts of `swepl-gate`; every hash matched.
  New agents `adele-judge-high` and `judge-dispatcher-high` were installed. The harness loads new
  agent files from the next user message, so judging starts after Pablo's next message.
- The analysis script was tested on synthetic labels, which were not kept.
