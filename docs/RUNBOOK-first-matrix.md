# Runbook: from public data to the first demand-annotated results matrix

Everything below is scripted; the steps marked **[you]** need your machine (network / email /
judgement), the rest is already committed on branch `benchmark-results`. Total hands-on time
for the [you] steps: ~30 minutes plus waiting.

## 0. Publish + sanity (5 min) [you]

    git push -u origin benchmark-results
    pip install -e ".[dev]" && pytest            # first clean-install run of the full suite
    # CI comes alive on the push; expect green.

## 1. Fetch the bulk per-instance flags (15 min, ~all cached afterwards) [you]

    # SWE-bench Verified: 468×134 matrix from a few-MB sparse checkout
    git clone --depth 1 --filter=blob:none --sparse \
        https://github.com/SWE-bench/experiments /tmp/swe-experiments
    git -C /tmp/swe-experiments sparse-checkout set --no-cone '/evaluation/verified/*/results'
    adele results fetch-swebench /tmp/swe-experiments -o swebench.parquet

    # AIME 2025+2026 per-problem correctness (~97 model configs)
    adele results fetch-matharena --dataset MathArena/aime_2025_outputs -o aime25.parquet
    adele results fetch-matharena --dataset MathArena/aime_2026_outputs -o aime26.parquet

    # ARC Prize: the ONLY per-instance record of the current generation
    adele results fetch-arcprize \
        anthropic-claude-opus-5 anthropic-claude-fable-5 openai-gpt-5-6 \
        moonshot-kimi-k3 thinky-inkling deepseek-v4-flash-0731 \
        -o arc.parquet
    # (scraper fails loudly if a page yields <80% of expected tasks — if it does,
    #  the site changed; send me the saved HTML and I'll fix the parser)

    adele results join swebench.parquet aime25.parquet aime26.parquet arc.parquet \
        -o matrix.parquet          # prints the coverage report

## 2. Freeze the instances we will annotate (10 min) [you]

    adele instances prepare -b swebench -b terminalbench -b aime -o ./instances
    # Fetches task text, canonicalizes ids to match the results matrix,
    # validates (dup ids / empty prompts hard-fail; long prompts warn),
    # freezes per-benchmark parquet + a sha256 manifest (instances/INSTANCES.tsv),
    # and prints the token/cost estimate BEFORE anything is spent.
    # terminalbench + aime loaders are schema-defensive: if a dataset's column
    # names differ they fail listing the observed columns — paste me the error.

    adele instances check-join ./instances matrix.parquet
    # MANDATORY before annotating: verifies the frozen instance ids actually
    # join the success flags from step 1. A low match rate = canonicalization
    # bug = annotation money that would not join. Fails loudly below 90%.

## 3. Send the partner asks (10 min) [you]

    See docs/partner-data-request.md — Epoch first (attach
    scripts/extract_scores_standalone.py + the manifest table), then Scale, then Sierra.
    When a scores.csv comes back:  adele results ingest-scores scores.csv -o epoch.parquet

## 4. Rubric regression gate (me, next session)

    Re-judge the banked PLp/PLe/MSc/MSm items under the catalogue-independent rubric text
    (old items = regression set; PLp's 94%/QWK .964 must hold). Nothing gets production-
    annotated before this passes.

## 5. Annotation (me, after the gate)

    adele agentic judge instances/instances_swe-bench-verified.parquet -m <judge> -n 30
    # dry-run first; then the full runs. Interruption-safe: every completed call
    # streams to raw_responses.jsonl and --resume (default) skips paid-for pairs
    # on restart, so a crash at call 4,900 of 5,000 costs nothing.

    SWE-bench Verified (500) + Terminal-Bench (~100) + AIME (60) × the active seven
    agentic dimensions ≈ 5k judge calls; AIME doubles as the discriminant-validity control
    (agentic demands should floor there). Output: demand vectors keyed by
    (benchmark, instance_id) — joinable onto matrix.parquet from step 1 by construction
    (guaranteed by step 2's check-join).

## 6. First envelope (me)

    Fit per-dimension ability curves on the dense previous-generation columns of the matrix;
    validate extrapolation on the current-generation columns (ARC + partner CSVs + TB2.1).
    That extrapolation check IS the safety-envelope demonstration.

## Known gaps (tracked, not blocking)

- Terminal-Bench 2.1 per-trial results live in Harbor Hub's JS app — needs API discovery in
  a browser session before a fetcher can be written; TB2.0's bulk HF dump works meanwhile.
- HLE/BrowseComp have no public per-instance data at any generation; only worth revisiting
  if we run models ourselves.
- GAIA instance text requires one gated-accept click on HF (`gaia-benchmark/GAIA`).
