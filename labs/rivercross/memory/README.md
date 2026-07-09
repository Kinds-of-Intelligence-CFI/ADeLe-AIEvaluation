# Rivercross MMs history-only pilot

This pilot tests whether hiding the current rivercross state introduces additional working or short-term memory demand. The design is paired: each underlying method-1b state appears once as 1b_state_visible.csv and once as 1b_history_only.csv.

The main signal is:

MMs_delta = MMs_history_only - MMs_state_visible

Analyze the paired delta rather than the absolute history-only score. Shared planning difficulty, puzzle difficulty, and cost-to-go are tied to the same underlying state and should partially cancel in the paired comparison.

## Success criteria

For the original paired history-only pilot, proceed only if:

1. paired MMs_delta is systematically greater than zero;
2. MMs_delta increases with object-location update complexity after controlling for history_length;
3. MMs_delta is not mainly explained by cost_to_go.

For the v3 contrast set, the hard gates are stricter:

1. the state-visible MMs baseline remains near zero;
2. within fixed history_length buckets, MMs_delta increases from low to medium to high object-memory complexity;
3. object-memory complexity explains MMs_delta beyond history_length and cost_to_go.

Judge agreement, non-collapsed label distributions, and reasons that mention state tracking are diagnostic checks, not the primary go/no-go criteria.

## Frozen v3 protocol

The v3 prompt, contrast frames, ground-truth pair file, MMs rubric version, analysis script, and hard gates are frozen for multi-judge validation. Further prompt, frame, rubric, or gate changes should be treated as a new protocol version rather than mixed into the v3 comparison.

Frozen v3 artifacts:

- labs/rivercross/frames/1b_memory_contrast_state_visible.csv
- labs/rivercross/frames/1b_memory_contrast_history_only.csv
- labs/rivercross/frames/ground_truth/1b_memory_contrast_pairs.csv
- labs/rivercross/prompts/templates/memory_state_tracking_annotation_v3.txt
- labs/rivercross/prompts/generated/prompt_MMs_1b_memory_contrast_state_visible_v3.txt
- labs/rivercross/prompts/generated/prompt_MMs_1b_memory_contrast_history_only_v3.txt
- labs/rivercross/memory/analyze_mms_delta.py
- labs/rivercross/memory/analyze_multi_judge_mms.py

## Caveat

Rivercross history-only states are deterministically reconstructable from the initial state and move history. A successful pilot supports a narrower claim: hiding the current state introduces measurable bookkeeping-type memory demand that grows with state updates. It does not by itself prove irrecoverable-information working memory.

## Current pilot result

The first MMs prompt fixed the basic paired setup but gave inflated state-visible labels. The v2 prompt fixed the state-visible baseline, but history-only labels collapsed to history_length. The v3 contrast set addresses this by holding history_length fixed while varying object_location_updates, num_reversals, and interference_count.

With Claude Sonnet 5 labels on the 18-pair v3 contrast set, the single-judge pilot passes the hard gates: mean state-visible MMs is 0.000, mean history-only MMs is 2.222, mean paired delta is 2.222, and Wilcoxon p=8.501e-05. MMs_delta is strongly associated with object_location_updates (Spearman rho=0.987) and is not associated with history_length (rho=0.082) or cost_to_go (rho=-0.047). The regression diagnostic mms_delta ~ object_location_updates + history_length gives beta=0.977 for object_location_updates and beta=-0.037 for history_length. Individual coefficients for reversals/interference should not be over-interpreted because those features are collinear in the high-complexity contrast items.

Multi-judge validation supports the v3 signal across strong judges. Claude Opus 4.8 reproduces the Sonnet pattern: mean state-visible MMs is 0.000, mean history-only MMs is 2.222, mean paired delta is 2.222, Spearman(delta, object_location_updates)=0.889, Spearman(delta, history_length)=0.000, and Spearman(delta, cost_to_go)=0.204. GPT-5 also reproduces the pattern: mean state-visible MMs is 0.000, mean history-only MMs is 2.333, mean paired delta is 2.333, Spearman(delta, object_location_updates)=0.974, Spearman(delta, history_length)=0.000, and Spearman(delta, cost_to_go)=0.000. Cross-judge agreement is high among the strong judges: Sonnet vs Opus Spearman=0.872, within-1=1.000, QWK=0.791; Sonnet vs GPT Spearman=0.986, within-1=1.000, QWK=0.961; Opus vs GPT Spearman=0.884, within-1=1.000, QWK=0.769. Claude Haiku 4.5 does not pass the v3 judge-independence check: mean state-visible MMs is 0.444, mean paired delta is 3.000, Spearman(delta, object_location_updates)=0.343, Spearman(delta, history_length)=0.583, and Spearman(delta, cost_to_go)=0.722. Haiku appears to count visible state and/or task difficulty despite the prompt constraints, so it should be treated as a weak/noisy judge for this protocol rather than as confirming evidence.

## Multi-judge validation

The Sonnet v3 result is positive, but it should not be treated as full validation until the signal is judge-independent. The next validation step is to run at least two additional judges, ideally one stronger Claude judge and one non-Claude judge. Each judge must annotate both v3 prompts so the paired delta remains the main signal.

For each judge, check: state-visible mean, history-only mean, mean delta, Spearman(delta, object_location_updates), Spearman(delta, history_length), Spearman(delta, cost_to_go), and regression delta ~ object_location_updates + history_length + cost_to_go. Across judges, check delta-rank agreement, within-1 agreement, QWK, and Spearman correlation between judges' deltas.

Run multi-judge analysis with repeated --judge arguments:

python labs/rivercross/memory/analyze_multi_judge_mms.py --pairs labs/rivercross/frames/ground_truth/1b_memory_contrast_pairs.csv --judge sonnet:labs/rivercross/memory/labels/mms_contrast_state_visible_sonnet_v3.csv:labs/rivercross/memory/labels/mms_contrast_history_only_sonnet_v3.csv

Add future judges using the same format:

python labs/rivercross/memory/analyze_multi_judge_mms.py --pairs labs/rivercross/frames/ground_truth/1b_memory_contrast_pairs.csv --judge sonnet:<sonnet_state_visible.csv>:<sonnet_history_only.csv> --judge opus:<opus_state_visible.csv>:<opus_history_only.csv> --judge gpt:<gpt_state_visible.csv>:<gpt_history_only.csv>

## Analysis

After collecting MMs labels for both conditions, run:

python labs/rivercross/memory/analyze_mms_delta.py --state-visible-labels <state_visible_mms_labels.csv> --history-only-labels <history_only_mms_labels.csv>

For the v3 contrast set, pass the contrast pair file explicitly:

python labs/rivercross/memory/analyze_mms_delta.py --pairs labs/rivercross/frames/ground_truth/1b_memory_contrast_pairs.csv --state-visible-labels labs/rivercross/memory/labels/mms_contrast_state_visible_sonnet_v3.csv --history-only-labels labs/rivercross/memory/labels/mms_contrast_history_only_sonnet_v3.csv

## Running model annotation

Use the prompt runner for the two generated MMs prompts. Example with Claude via litellm:

export ANTHROPIC_API_KEY=...
python labs/rivercross/memory/run_prompt_annotation.py --prompt labs/rivercross/prompts/generated/prompt_MMs_1b_state_visible.txt --model claude-sonnet-5 --name mms_state_visible_sonnet
python labs/rivercross/memory/run_prompt_annotation.py --prompt labs/rivercross/prompts/generated/prompt_MMs_1b_history_only.txt --model claude-sonnet-5 --name mms_history_only_sonnet

Then analyze:

python labs/rivercross/memory/analyze_mms_delta.py --state-visible-labels labs/rivercross/memory/labels/mms_state_visible_sonnet.csv --history-only-labels labs/rivercross/memory/labels/mms_history_only_sonnet.csv

Dry-run credential and token checks:

python labs/rivercross/memory/run_prompt_annotation.py --prompt labs/rivercross/prompts/generated/prompt_MMs_1b_state_visible.txt --model claude-sonnet-5 --dry-run
