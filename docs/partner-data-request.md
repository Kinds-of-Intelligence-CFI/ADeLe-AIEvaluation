# Requesting per-sample scores from partners (Epoch AI, Scale/Transluce)

Some publishers hold per-instance results we need but cannot bulk-share (bot-protected
viewers, contamination worries, sheer log size). The ask below is designed to cost them
minutes, not favors: they run one auditable script against their own logs and send back a
CSV of a few hundred KB containing only IDs and scores — no prompts, no model outputs.

## The mechanism

`scripts/extract_scores_standalone.py` — single file, stdlib + inspect-ai only, ~40 lines of
logic. It reads every `.eval` log under a directory and writes six columns per sample:
`benchmark, model, sample_id, epoch, score, log_sha256_12`. It never accesses sample inputs,
outputs, messages or metadata (auditable at a glance), and prints the output's SHA-256 so what
they review is verifiably what they send. We ingest the CSV with
`adele results ingest-scores scores.csv`.

## Email draft — Epoch AI

> Subject: 300 KB of sample IDs + scores from your Inspect logs?
>
> Hi — we build ADeLe (annotated demand levels; arXiv:2503.06378, Kinds of Intelligence
> Centre, Cambridge). We annotate benchmark instances with cognitive-demand levels and fit
> per-dimension ability curves; your Benchmarking Hub is the only continuously-updated
> per-question record of current frontier models (we know the log viewer is deliberately
> bot-protected, and why).
>
> We don't need the logs. We need only (sample_id, model, score) per run — the attached
> ~100-line script extracts exactly that from a directory of .eval files and nothing else
> (it never touches inputs/outputs; it prints a checksum of what it writes). For GPQA
> Diamond, SWE-bench Verified, SimpleQA Verified, MirrorCode and OTIS-AIME across the models
> you've run, the output should be well under a megabyte.
>
> In return we're happy to share the demand annotations for those instances and the fitted
> ability profiles — which give your accuracy numbers an explanatory axis (what kind of
> difficulty each model fails at, not just how often).
>
> Would you run it, or alternatively allowlist a research token for the log endpoints?

## Email draft — Scale / Transluce (SWE-bench Pro trajectories via Docent)

> Subject: per-instance resolved flags for SWE-bench Pro entries
>
> Hi — for a demand-level analysis of SWE-bench Pro (ADeLe, arXiv:2503.06378) we'd like
> per-instance resolved/unresolved flags for the public leaderboard entries. The Docent
> dashboards clearly contain them; we don't need trajectories or patches — just
> (instance_id, model, resolved) per entry, or a Docent export/API pointer if that exists.
> Happy to share the per-instance demand annotations of the SWE-bench Pro public set in
> return.

## Notes

- Sequence the Epoch ask first; their "use this data" page signals willingness, and one CSV
  from them covers five benchmarks × the current generation in one step.
- If a partner prefers, the same extraction can run inside their CI (the script is
  deterministic; pin its git SHA in correspondence).
- Everything received lands in `adele results ingest-scores` → the standard matrix; provenance
  column `source` records which partner produced which rows.
