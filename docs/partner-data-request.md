# Partner data requests: exactly what we send, what comes back

Some publishers hold per-instance results we need but don't offer as downloads (bot-protected
viewers, log size, contamination worries). The protocol below makes the ask cost them minutes:
they run one auditable script against their own files and send back a small CSV of IDs and
scores. We never receive logs, prompts, model outputs, or infrastructure access.

## Epoch AI — the full exchange, spelled out

**What we SEND (one email, two attachments):**

1. `scripts/extract_scores_standalone.py` — a single Python file, ~100 lines, stdlib +
   inspect-ai only. They can audit it in one sitting: it reads every `.eval` file under a
   directory they choose and writes six columns per scored sample — `benchmark, model,
   sample_id, epoch, score, log_sha256_12`. It never touches sample inputs, outputs, messages
   or metadata, and it prints the SHA-256 of the CSV it wrote, so what they review is
   verifiably what they send.
2. The request manifest (section below): which benchmarks and models we care about, so they
   can point the script at the right log directories and ignore the rest.

**What THEY do (10–20 minutes):**

    python extract_scores_standalone.py /their/inspect/logs scores.csv
    # open scores.csv, confirm it contains only IDs and letters/numbers, reply with it attached

**What WE GET BACK:** one CSV, likely a few hundred KB, e.g.:

    benchmark,model,sample_id,epoch,score,log_sha256_12
    gpqa_diamond,claude-fable-5,recNXpiB...,1,C,9f2ac01b3d44
    swe_bench_verified,gpt-5.6-sol,astropy__astropy-12907,1,I,77b0e3aa91c2

`sample_id` is Inspect's dataset sample id, which for these benchmarks is the public instance
identifier — so the rows join directly onto our demand annotations by (benchmark, instance_id)
via `adele results ingest-scores scores.csv`. That single file gives us the per-question
success matrix for every model Epoch has run — currently including Claude Fable 5, GPT-5.6
and Kimi K3 — on the benchmarks below.

**Request manifest (what to name in the email):**

| Epoch benchmark | why we want it |
|---|---|
| GPQA Diamond | densest static anchor; joins HELM's 22-model cohort |
| SWE-bench Verified | extends our 134-entry matrix to Epoch's harness + current models |
| SimpleQA Verified | cheap wide coverage |
| MirrorCode | only per-instance coding signal for Fable 5 / GPT-5.6 (their Aug 2026 update) |
| OTIS Mock AIME | joins MathArena's math axis |
| FrontierMath (public problems only) | whatever is shareable |

Models: everything they have; the June–August 2026 generation (Fable 5, GPT-5.6*, Kimi K3,
DeepSeek V4, Gemini 3.x) is the part we cannot get anywhere else.

**What we OFFER in return:** the per-instance demand-level annotations (18 validated
dimensions) for those same benchmark instances, plus the fitted ability profiles per model —
an explanatory axis on top of their accuracy numbers (what *kind* of difficulty each model
fails at). Their attribution in any resulting publication.

**What we explicitly do NOT ask for:** eval logs, transcripts, prompts, completions, tokens,
costs, API access, or anything requiring legal review of content sharing.

**Fallback tier, if even per-sample flags cannot be shared.** The same script has an
aggregate-only mode: we send our demand-annotation CSV alongside it, they run
`... --aggregate annotations.csv`, and the output contains no sample ids at all — only, per
(benchmark, model, dimension, demand level), the counts `n_samples, n_solved`. These are the
sufficient statistics for fitting ability curves, so the collaboration still works; we lose
instance-level diagnostics (calibration outliers, red-team candidates) and must re-ask
whenever the rubrics are revised — which is why per-sample flags remain the primary ask and
this is the fallback. (This mode is also the template for frontier labs with genuinely
private evals: run locally, share only the envelope statistics.)

### Email draft

> Subject: one script run → 300 KB of sample IDs + scores from your Inspect logs?
>
> Hi — we build ADeLe (annotated demand levels; arXiv:2503.06378, Kinds of Intelligence
> Centre, Cambridge). We annotate benchmark instances with cognitive-demand levels and fit
> per-dimension ability curves; your hub is the only continuously updated per-question record
> of the current model generation (we know the log viewer is bot-protected, and why).
>
> We are not asking for logs. Attached is a ~100-line script (stdlib + inspect-ai) that reads
> a directory of .eval files and writes only (benchmark, model, sample_id, epoch, score) —
> no sample content of any kind — plus a checksum of its own output. Running it over your
> GPQA Diamond, SWE-bench Verified, SimpleQA Verified, MirrorCode and OTIS-AIME logs and
> replying with the CSV would take ~15 minutes and give us per-question joins for the models
> nobody else has run (Fable 5, GPT-5.6, Kimi K3...).
>
> In return: our per-instance demand annotations for those benchmarks and the fitted ability
> profiles — an explanatory layer over your accuracy numbers — plus attribution.
>
> If you'd rather grant a research token for the log endpoints instead, that works too.

## Scale / Transluce — SWE-bench Pro (smaller, secondary ask)

We want per-instance resolved/unresolved flags for the public SWE-bench Pro leaderboard
entries (the Docent dashboards visibly contain them). Ask for `(instance_id, model, resolved)`
per entry or a Docent export/API pointer; offer the demand annotations of the SWE-bench Pro
public task set in return.

## Sierra (tau2/tau3) — third

Every current-generation submission (Opus 5, Fable 5, GPT-5.6-sol, Qwen 3.8 Max) has
`trajectories_available: true` with per-trial files on their S3. Ask for the per-task reward
summaries only (not the trajectories) for those entries.

## Bookkeeping

- Sequence: Epoch first (one CSV covers five benchmarks × the current generation), Scale
  second, Sierra third.
- Pin the extractor's git SHA in correspondence so the run is reproducible.
- Everything received is ingested with `adele results ingest-scores` and lands in the standard
  matrix with `source` recording the partner.
