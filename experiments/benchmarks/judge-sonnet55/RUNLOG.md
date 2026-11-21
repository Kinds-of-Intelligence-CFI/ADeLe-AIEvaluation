# judge-sonnet55 — run log

## 2026-09-29 — probe and pinned run `s55h-gate`

- **Probe.** One throwaway call (`adele-judge-low`, model alias `sonnet`) on a non-study prompt: the
  answer was written by `claude-sonnet-5-5`. On 2026-09-28 the same alias still gave
  `claude-sonnet-5`.
- **Pinned run.** `make_run.py` copied the 88 PLp and PLe prompts of `swepl-gate`; every hash matched.
  New agents `adele-judge-high` and `judge-dispatcher-high` were installed. The harness loads new
  agent files from the next user message, so judging starts after Pablo's next message.
- The analysis script was tested on synthetic labels, which were not kept.

## 2026-09-29 — run `s55h-gate`: complete

- **Judging.** Two `judge-dispatcher-high` relays of 44 cells, then one retry relay of 24 cells,
  10:43–10:51 UTC. 112 judge calls in all.
- **Safeguard flags.** 24 first-pass calls ended with "Sonnet 5.5's safeguards flagged this message"
  (category `reasoning_extraction`) and wrote nothing, all on PLp. Their one retry failed again for
  23 of them. One PLe call was flagged after it had written its answer. No answer came from another
  model. 65 of 88 cells have a label.
- **Protocol check** over the 112 transcripts: exact two-line message, working directory
  `~/Developer/ADELE`, effort high, no CLAUDE.md, own files only.
- **Meters.** Before (10:43 UTC): 5-hour 6%, weekly 96%. After the retry: 5-hour 11%, weekly 97%.
- **Analysis.** Verdict "does not". The medium arm is skipped, as Pablo decided.
