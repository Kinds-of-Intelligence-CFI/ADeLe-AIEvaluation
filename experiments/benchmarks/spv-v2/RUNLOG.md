# spv-v2 — run log

## 2026-10-05

- **Phase A (`spv2-1`).** 222 prompts in four `judge-dispatcher-v2-low` relays, run concurrently. All 222 were
  answered, parsed and written by Opus 5.5. No pass 2 was needed.
- **Phase B (`spv2-b`).**
  - New agents `adele-judge-v2-low-image` and `judge-dispatcher-v2-low-image`, in `~/Developer/ADELE/.claude/agents`.
    They are `adele-judge-v2-low` plus permission to read the images a prompt names.
  - A one-cell smoke test: the transcript shows the PNG loaded as an image block. Then four relays covered the other
    390 cells.
  - The relays reported 91–92 "sent" for 97–98 cells; that is a miscount. All 391 answer files exist, each matched to
    a Write call by `writers.py`, all written by Opus 5.5.
  - The analysis first counted the traps and P-meter, which have no key arm, as key disagreements. Fixed (`dropna`)
    before the write-up.
- **Phase C (`spv2-c`).**
  - ZeroBench main split downloaded to gitignored `data/downloads/zerobench/` after Pablo accepted the gate.
  - The 67 × 100 matrix was decoded from the leaderboard page's Plotly heatmap; its x values are question ids.
  - Answer-leak check: 4 prompts contain their own answer string outside the question text. All four are question 88,
    whose three-character answer occurs as ordinary text in the shared rubric or instructions. That is identical in
    every prompt, so it is not a leak.
