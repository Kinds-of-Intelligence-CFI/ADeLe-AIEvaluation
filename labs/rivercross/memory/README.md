# Rivercross MMs history-only pilot

This pilot tests whether hiding the current rivercross state introduces additional working or short-term memory demand. The design is paired: each underlying method-1b state appears once as 1b_state_visible.csv and once as 1b_history_only.csv.

The main signal is:

MMs_delta = MMs_history_only - MMs_state_visible

Analyze the paired delta rather than the absolute history-only score. Shared planning difficulty, puzzle difficulty, and cost-to-go are tied to the same underlying state and should partially cancel in the paired comparison. Note that in the v3 results the strong judges give exactly 0 on every state-visible item, so the delta reduces to the absolute history-only score; keep the paired design as a guard against baseline drift, but do not credit it with variance reduction.

## Success criteria

For the original paired history-only pilot, proceed only if:

1. paired MMs_delta is systematically greater than zero;
2. MMs_delta increases with object-location update complexity after controlling for history_length;
3. MMs_delta is not mainly explained by cost_to_go.

For the v3 contrast set, the hard gates are stricter. Read them as manipulation checks, not as external-validity findings: the design deliberately restricts cost_to_go to {1,2} and history_length to {3,4,5} while object_location_updates spans 1-20, so gates 1 and 3 mostly verify that the design held, and near-zero correlations with the restricted controls are expected for any judge that tracks the manipulation. Claims like "MMs does not absorb task difficulty" would need a set where cost_to_go varies substantially; this one cannot support them.

1. the state-visible MMs baseline remains near zero;
2. within fixed history_length buckets, MMs_delta increases from low to medium to high object-memory complexity;
3. object-memory complexity explains MMs_delta beyond history_length and cost_to_go (within the restricted ranges above).

Judge agreement, non-collapsed label distributions, and reasons that mention state tracking are diagnostic checks, not the primary go/no-go criteria.

Statistical unit: the -01/-02 replicate pairs share identical feature vectors, so pair-level tests (n=18) overstate the evidence. The analysis script also reports cell-level statistics on the 9 unique design cells (replicates averaged); quote those as the primary numbers.

## Frozen v3 protocol

The v3 prompt, contrast frames, ground-truth pair file, MMs rubric version, analysis script, and hard gates are frozen for multi-judge validation, **committed at `2b0a2e9`** ("Freeze MMs v3 protocol"). Further prompt, frame, rubric, or gate changes should be treated as a new protocol version rather than mixed into the v3 comparison. Post-freeze commits add reporting diagnostics to the analysis script (prompt-token correlation, per-cell aggregation) without changing the v3 gates or labels; the v4 verbosity control below is a separate protocol version.

Judge panel: v3 was run with Claude Sonnet 5, Claude Opus 4.8, GPT-5, and Claude Haiku 4.5, with no pre-registered inclusion criterion; Haiku's exclusion from the headline claim (below) is therefore post hoc. From v4 on, fix the judge panel and an inclusion criterion independent of the gates (e.g. a state-reconstruction accuracy screen on held-out histories) before collecting labels.

Frozen v3 artifacts:

- labs/rivercross/frames/1b_memory_contrast_state_visible.csv
- labs/rivercross/frames/1b_memory_contrast_history_only.csv
- labs/rivercross/frames/ground_truth/1b_memory_contrast_pairs.csv
- labs/rivercross/prompts/templates/memory_state_tracking_annotation_v3.txt
- labs/rivercross/prompts/generated/prompt_MMs_1b_memory_contrast_state_visible_v3.txt
- labs/rivercross/prompts/generated/prompt_MMs_1b_memory_contrast_history_only_v3.txt
- labs/rivercross/memory/analyze_mms_delta.py
- labs/rivercross/memory/analyze_multi_judge_mms.py

## Caveats

Rivercross history-only states are deterministically reconstructable from the initial state and move history. A successful pilot supports a narrower claim: hiding the current state introduces measurable bookkeeping-type memory demand that grows with state updates. It does not by itself prove irrecoverable-information working memory.

The contrast frames are synthetic (constructed by `build_memory_contrast.py` from enumerated legal traces), not sampled from real agent rollouts. The pilot shows judges can rank constructed contrast items; it does not yet show how MMs annotation behaves on real 1b rollout states.

In the v3 design, object mentions in the history text scale with object_location_updates (Spearman(delta, history_prompt_tokens) is ~0.9 for the strong judges), so v3 alone cannot distinguish a judge that tracks state updates from one that counts history verbosity. The v4 verbosity control below exists to separate these.

## Current pilot result

The first MMs prompt fixed the basic paired setup but gave inflated state-visible labels. The v2 prompt fixed the state-visible baseline, but history-only labels collapsed to history_length. The v3 contrast set addresses this by holding history_length fixed while varying object_location_updates, num_reversals, and interference_count.

All numbers below are regenerated from the frozen artifacts by `analyze_multi_judge_mms.py` and recorded in `labs/rivercross/memory/results/multi_judge_v3.txt`; quote that file, not this prose, if they ever disagree.

With Claude Sonnet 5 labels on the 18-pair v3 contrast set, the single-judge pilot passes the hard gates: mean state-visible MMs is 0.000, mean history-only MMs is 2.222, mean paired delta is 2.222, and pair-level Wilcoxon p=3.815e-06 (an earlier README version reported p=8.501e-05, which no longer reproduces). At the honest unit of analysis - the 9 unique design cells, replicates averaged - the cell-level Wilcoxon gives p=0.001953 and cell-level Spearman(delta, object_location_updates)=0.982. Pair-level: MMs_delta is strongly associated with object_location_updates (Spearman rho=0.987) and is not associated with history_length (rho=0.082) or cost_to_go (rho=-0.047); recall from the success-criteria section that the near-zero control correlations are largely guaranteed by the restricted control ranges. MMs_delta also correlates with history prompt token count (rho=0.893), which is why the v4 verbosity control exists. The regression diagnostic mms_delta ~ object_location_updates + history_length gives beta=0.977 for object_location_updates and beta=-0.037 for history_length. Individual coefficients for reversals/interference should not be over-interpreted because those features are collinear in the high-complexity contrast items.

Multi-judge validation supports the v3 signal across strong judges. Claude Opus 4.8 reproduces the Sonnet pattern: mean state-visible MMs is 0.000, mean history-only MMs is 2.222, mean paired delta is 2.222, Spearman(delta, object_location_updates)=0.889, Spearman(delta, history_length)=0.000, and Spearman(delta, cost_to_go)=0.204. GPT-5 also reproduces the pattern: mean state-visible MMs is 0.000, mean history-only MMs is 2.333, mean paired delta is 2.333, Spearman(delta, object_location_updates)=0.974, Spearman(delta, history_length)=0.000, and Spearman(delta, cost_to_go)=0.000. Cross-judge agreement is high among the strong judges: Sonnet vs Opus Spearman=0.872, within-1=1.000, QWK=0.791; Sonnet vs GPT Spearman=0.986, within-1=1.000, QWK=0.961; Opus vs GPT Spearman=0.884, within-1=1.000, QWK=0.769. Claude Haiku 4.5 does not pass the v3 judge-independence check: mean state-visible MMs is 0.444, mean paired delta is 3.000, Spearman(delta, object_location_updates)=0.343, Spearman(delta, history_length)=0.583, and Spearman(delta, cost_to_go)=0.722. Haiku appears to count visible state and/or task difficulty despite the prompt constraints, so it should be treated as a weak/noisy judge for this protocol rather than as confirming evidence.

## Multi-judge validation

The Sonnet v3 result is positive, but it should not be treated as full validation until the signal is judge-independent. The next validation step is to run at least two additional judges, ideally one stronger Claude judge and one non-Claude judge. Each judge must annotate both v3 prompts so the paired delta remains the main signal.

For each judge, check: state-visible mean, history-only mean, mean delta, Spearman(delta, object_location_updates), Spearman(delta, history_length), Spearman(delta, cost_to_go), and regression delta ~ object_location_updates + history_length + cost_to_go. Across judges, check delta-rank agreement, within-1 agreement, QWK, and Spearman correlation between judges' deltas.

Run multi-judge analysis with repeated --judge arguments:

python labs/rivercross/memory/analyze_multi_judge_mms.py --pairs labs/rivercross/frames/ground_truth/1b_memory_contrast_pairs.csv --judge sonnet:labs/rivercross/memory/labels/mms_contrast_state_visible_sonnet_v3.csv:labs/rivercross/memory/labels/mms_contrast_history_only_sonnet_v3.csv

Add future judges using the same format:

python labs/rivercross/memory/analyze_multi_judge_mms.py --pairs labs/rivercross/frames/ground_truth/1b_memory_contrast_pairs.csv --judge sonnet:<sonnet_state_visible.csv>:<sonnet_history_only.csv> --judge opus:<opus_state_visible.csv>:<opus_history_only.csv> --judge gpt:<gpt_state_visible.csv>:<gpt_history_only.csv>

## Human spot check

`human_spot_check_completed.csv` holds a single-annotator manual pass over the 9 `-01` items: it confirms sv_should_be_0 on every state-visible view, rough history-only levels of 1/2/3 for low/medium/high, and the expected delta direction and within-history-length ordering. Its ordering agrees with the strong judges. Limitations: annotator and date are not recorded, it covers only half the pairs, and levels are marked "rough" - treat it as a sanity check, not a human baseline. Before any external claim, complete all 18 pairs, record annotator + date in the file, and get the planned second annotator for a human-human ceiling.

## v4 verbosity control

v3 cannot separate "judge tracks object-location updates" from "judge counts history verbosity", because in the contrast set object mentions scale with updates. The v4 protocol adds that separation:

- `frames/build_verbosity_control.py` rewrites the 6 low items' histories verbosely (every line also names the objects that did not move, without revealing banks), leaving every ground-truth memory feature unchanged while pushing token counts above the high group (verbose-low mean 238 tokens vs high mean 186).
- The v4 frame (`frames/1b_memory_verbosity_history_only.csv`) contains these 6 verbose-low items plus the 12 unmodified v3 medium/high items as same-batch anchors; standard-low items are excluded so judges cannot recognise duplicated traces. Pair metadata: `frames/ground_truth/1b_memory_verbosity_pairs.csv`. Prompt: `prompts/generated/prompt_MMs_1b_memory_verbosity_history_only_v4.txt` (same template and rubric as v3). State-visible views are identical to v3, so the frozen v3 state-visible labels are reused.
- Decision rule, within one v4 run: a token-counting judge must score verbose-low at or above high; an update-tracking judge must score verbose-low below medium, near the v3 low labels (~1).

Analyze with:

python labs/rivercross/memory/analyze_verbosity_control.py --labels sonnet:labs/rivercross/memory/labels/mms_verbosity_history_only_sonnet_v4.csv --v3-low-labels sonnet:labs/rivercross/memory/labels/mms_contrast_history_only_sonnet_v3.csv

**v4 result** (full output in `results/verbosity_control_v4.txt`): all three strong judges (Sonnet 5, Opus 4.8, GPT-5) label every verbose-low item 1 - identical to their frozen v3 low labels - while ranking the same-batch medium and high anchors above it (Mann-Whitney verbose-low < high, p<=0.0013 per judge), even though verbose-low has the highest token count of any group (mean 238 vs high 186). The token-counting explanation of the v3 signal is refuted for these judges; the verbosity caveat above is resolved for v3's headline claim. Judge annotation was run with `--max-tokens 16384` for Sonnet and `--max-tokens 32768` for GPT-5 (reasoning models return empty content at the old 4096 default).

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
