# swev30-r3 run log

## 2026-09-26 — probe call from the session that made deviation 2: invalid

One call (`django__django-15382` × VO × opus) was sent from the session that edited
`adele-judge.md`, to check the new settings before the other five. Its transcript shows the old
definition: the CLAUDE.md files and the nested `ADELE_v2` guide were still attached (first
request 7,504 tokens; 7,518 in r2). A new agent file added to the same `.claude/agents/` folder
was then not found by that session ("Agent type 'judge-probe' not found"). So this session, which
runs in the Claude desktop app, keeps the agent definitions it loaded at start, although the
Claude Code docs describe a file watcher. The probe's answer (VO = 3) is set aside under
`data/annotations/swev30-r3/responses_discarded_probe/` and is not a label.

The transcripts show one more injected file, in r2 as well: the `instructions` attachment also
carries the session's auto-memory index (`MEMORY.md`), whose entries currently include Epoch's
verdict that SWE-bench Verified is flawed.

## 2026-09-26 — diagnosis, and one valid call

Why the probe saw the old definition: the Claude Code CLI behind the desktop app does reload agent
files when they change, but each turn keeps the agent definitions it had when it started (the
turn's tool context is built from a snapshot). The edit, the probe and the throwaway agent all
fell in one turn. No restart is needed; a change applies from the next message. An earlier
session's "Agent type 'adele-judge' not found" had a different, documented cause: that session
created the `.claude/agents/` folder after it started, and a session never watches a folder
created after its start.

In the next turn the same cell ran under the pinned r3 definition: opus VO = 3, a valid r3 label.
Its transcript has no `instructions` attachment (first request 3,274 tokens, against 7,504) and
effort `max`. The nested `ADELE_v2/CLAUDE.md` guide is still attached when the judge reads the
prompt: `omitClaudeMd` removes the CLAUDE.md files loaded at start, not one attached when a file
below its folder is read (in the CLI's code, that second filter applies only when managed-policy
files exist). One throwaway call, with a copy of the same prompt placed outside `ADELE_v2/`
(`~/Developer/ADELE/judge-io-test/`, since removed), carried no CLAUDE.md of any kind: final
context 10.6k tokens, against 18.0k with the guide. Its answer is not a label.

Status: superseded by deviation 3 (run `swev30-r4`). The one label is discarded: kept aside under
`data/`, never analysed.
