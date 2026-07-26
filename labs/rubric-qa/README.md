# rubric-qa: inter-judge pilot for the re-keyed PLp rubric

First empirical check of the single-driver PLp rubric (commit "rubrics(v2):
re-key PLp on a single demand driver"). 8 tasks from pilot/tasks.csv, 3 judges
(haiku / sonnet / opus) x 3 independent samples each = 72 annotations, using
the exact `build_annotation_prompt` format from `adele.annotation.prompts`
with the new rubric. Judges saw only the task prompt text - no benchmark name,
no USACO division label.

Battery: the 5 USACO 2025 US Open problems (Bronze/Silver/Gold/Plat/Plat,
an external-difficulty ladder), 2 tau-bench tasks as demarcation traps
(designed PLp cap 2: their difficulty is MS/PLe, not plan-finding), and 1
AssistantBench lookup as an L1 anchor probe.

Results (see plp_v2redesign_pilot_labels.csv):
- Within-judge 3-seed full agreement: haiku 4/8, sonnet 7/8, opus 8/8.
- Cross-judge: all pairs within +-1 on 8/8 tasks. Krippendorff alpha
  (interval): 0.861 over all ratings, 0.811 over judge modes.
- Spread: every judge used levels 1-4; per-judge SD 0.85-1.15 (old-rubric
  HAL labels sat at ~0.5).
- USACO ladder medians Bronze->Plat: 3,3,4,4,4 - monotone, blind to division.
- Traps: 17/18 ratings at or under the designed cap (one haiku seed gave 3).
- L1 anchor: 9/9 exact.

Known systematic effect: sonnet reads the whole USACO ladder one level higher
than haiku (haiku mode 3 vs sonnet mode 4 on all five problems; opus splits
by difficulty: 3,3,4,4,4). Constant offset between judges, not noise - the
L3/L4 gate ("can the decomposition be listed at the outset?") is applied with
different strictness. Candidate fix if it persists at scale: one more L3/L4
matched example pair.

Caveats: single small battery; judges are the harness's current haiku/sonnet/
opus builds, not the exact API snapshots used for the old HAL labels; judge
output kept to a short justification rather than full printed CoT. Next steps:
old-rubric arm on the same 8 tasks for a paired comparison, then re-annotation
of the HAL traces for the PLp/PLe separation test.

## Round 2: gate-walk protocol (diagnosis)

Re-ran the 5 USACO tasks with a "gate-walk" instruction: judges answer six
boundary questions in order, with task evidence, before any score is stated.
All three judges agree on gates 0-2 everywhere; the whole divergence is the
L3/L4 gate phrase "established methods exist for tasks of this kind".
haiku reads "kind" at class level (all of competitive programming -> ceiling
L3); sonnet reads it at instance level (no template for this exact objective
-> floor L4); opus resolves it by sketching a plan and checking whether the
outline falls out of recognizing the problem type.

## Round 3: L3/L4 patch + verification

Commit "PLp: sharpen the L3/L4 gate" makes opus's test explicit in the rubric
text. Verification on the divergent cells (2 seeds, original protocol):
sonnet on Bronze moved 4,4,4 -> 3,4; sonnet on Silver and haiku on the
Platinums unchanged; opus stable. Conclusion: the patch helps at the margin
but the L3/L4 boundary for competition programming remains partly
judge-capability-relative - whether "recognizing the type yields a plan
outline" depends on whether the judge itself can sketch the plan. Text alone
will not close the gap.

What does close it, on this data: the cross-judge MEDIAN. Median of
(haiku, sonnet, opus) equals opus's calibrated answer on every USACO task in
every round (3,3,4,4,4), because haiku and sonnet err in opposite directions.
Recommendation: keep the 3-judge median as the operational label; treat
per-judge offsets as a calibration property to monitor, not a rubric bug to
chase further. A protocol-level option for the team (touches shared
annotation code, not this branch): add the sketch test to the judge
instruction - "before deciding between Levels 3 and 4, attempt to write the
plan outline; if you can, it is Level 3".

## Round 4: paired baseline - OLD v2 rubric, same 8 tasks, same protocol

Labels in plp_oldrubric_pilot_labels.csv. Head-to-head (72 vs 72 annotations):

| metric                        | old rubric      | new rubric      |
|-------------------------------|-----------------|-----------------|
| Krippendorff alpha            | 0.611           | 0.861           |
| levels used (any judge)       | 1-3             | 1-4             |
| per-judge SD                  | 0.40-0.69       | 0.85-1.15       |
| USACO medians B,S,G,P,P       | 3,2,2,2,3       | 3,3,4,4,4       |
| monotone in division          | NO (inverted)   | YES             |
| Spearman vs division          | 0.15            | 0.66            |
| trap violations (cap 2)       | 0/18            | 1/18            |
| Platinum vs tau-bench sep.    | NONE (both 2)   | 2 levels        |

The old rubric reproduces the measured HAL failure on this battery: scores
compress into 2-3, Bronze is rated HARDER than two Platinums, and a Platinum
problem gets the same PLp as a tau-bench flight change. The judges' stated
reasons are the borrowed drivers: "no multi-agent coordination -> below
Level 3", "roughly 4-10 steps -> Level 2", "static and single-agent ->
modest planning". Under the old rubric the judges also disagree in a
DIFFERENT direction than under the new one (old: haiku above sonnet/opus;
new: sonnet above haiku/opus), i.e. old-rubric agreement is not just lower,
it is unstable in sign.

Verdict: on every metric except trap compliance (both fine), the re-keyed
rubric dominates the old one on this battery. Remaining known issue is the
haiku/sonnet L3/L4 offset under the new rubric, mitigated by the 3-judge
median (see Round 3).

## Round 5: PLe re-key pilot (63 annotations, new PLe rubric)

Battery: usaco-0004/0011 and tau-0007 (separation profile vs their PLp
labels), ple-wizard (designed L1: per-step-validated setup wizard),
ple-ledger (designed L4: year-end reconciliation, silent propagation),
ple-migration (designed L5: no-rollback live migration), chess-trap
(designed PLe<=1: find a winning chess line and write it down — plan-hard,
execution-easy). ab-0011 was built but not run (wizard covers the floor).

Results (ple_v2redesign_pilot_labels.csv):
- Designed ladder: PERFECT. wizard 9/9 at L1, ledger 9/9 at L4, migration
  9/9 at L5; alpha = 1.0 on those three. Where the feedback/propagation/
  irreversibility structure is explicit in the task, all three judges read
  the gates identically.
- Overall alpha 0.797; every judge used 5-6 levels, SD 1.25-1.58.
- Separation vs PLp so far: usaco-0011 PLp 4 / PLe 3; tau PLp 2 / PLe 2;
  usaco-0004 PLp 3 / PLe 3 (no separation).

THE ROUND'S REAL FINDING - the chess trap failed, unanimously (4,3,4 /
4,4,4 / 4,3,4 against a designed cap of 1), and the judges were being
FAITHFUL to the rubric as written: they cited the Level 4 "long
mathematical derivation by hand" anchor and argued that calculating chess
variations is a chain of dependent internal steps whose early errors
silently invalidate the rest. They are right that it is; the rubric never
says whether "actions" include internal reasoning steps. If they do, every
hard reasoning task scores high on BOTH PLp (finding the plan) and PLe
(carrying out the reasoning) and the collinearity we are trying to remove
comes back through the side door — visible already in haiku's 4,4,4 on
usaco-0004 ("algorithm design errors propagate") and sonnet's 3,1,0 seed
instability there (each seed picked a different notion of what the
"actions" of a competitive-programming task are).

Construct decision needed (Pablo/team): does PLe measure ENVIRONMENTAL
execution (steps that read/write the world outside the agent) or also
COGNITIVE execution (carrying out a long internal derivation)? The
PLp/PLe-separation goal argues for environmental-only. Proposed fix if so:
(1) a preamble clause defining actions as interactions with the
environment, with internal reasoning routed to the reasoning/planning
dimensions; (2) replace the L4 derivation anchor (internal work) with an
environmental one — the ledger reconciliation item itself is ideal; the
codebase and contract anchors already qualify. Not applied yet - this
changes what the dimension measures, so it needs sign-off.

## Round 6: plan-step action definition - verification of the failed cells

Commit "PLe: define an action as the carrying-out of one plan step" adds the
intentional action definition (separately instructable + separately
wrong-and-redoable; tokens fail both tests), swaps the L4 derivation anchor
for the validated ledger item, and adds the chess contrast anchor at L1.
Re-run of the two failed cells, same protocol:

- chess-trap (designed <=1): was 4,3,4 / 4,4,4 / 4,3,4 -> now 1,1,1 / 0,1,1 /
  0,1,0. All 9 seeds within the cap. Judges now route the search to Planning
  explicitly.
- usaco-0004: was 4,4,4 / 3,1,0 (unstable) / 3,3,3 -> now 3,3,0 / 1,1,1 /
  1,1,1. Median 3 -> 1. sonnet's seed instability collapsed. Reading: the
  task-as-posed delivers one program; iterative local testing is solver
  strategy, not task structure, so low PLe follows from the task-not-solver
  principle. Flagged as a construct call worth team awareness: CP problems
  are now high-PLp / low-PLe by design.

PLp/PLe separation, both directions, on this battery (medians):
  usaco-0004  PLp 3 / PLe 1     chess       PLp ~3 / PLe 1
  usaco-0011  PLp 4 / PLe 3     tau-0007    PLp 2 / PLe 2
  ple-ledger  PLe 4 (PLp low: known procedure)
  ple-migration PLe 5 (PLp low: known procedure)
The old rubric pair could not produce a single high-low cell in either
direction (HAL separation 0.00); the re-keyed pair produces them in both.

## Round 7: executive-scope + transcription/construction patch - verification

Commit "PLe/PLp: full executive scope..." verified on the three moved cells
(3 judges, 2-3 seeds):

- chess-trap (cap <=1): 1,1 / 1,1 / 1,1 - now unanimous, the L0/L1 wobble
  gone. Cap holds for the third consecutive rubric version.
- usaco-0004: 3,3,3 / 2,3,3 / 1,1,3 - median 3 (round 5: 0-4 chaos,
  round 6: over-shot to 1). The judges' 3 is the faithful reading of the
  ladder: a program is a constructed deliverable, sample I/O is an
  END-check not a per-subtask checkpoint, so tens of actions pass without
  feedback -> self-checked L3, errors fixed in place. (The round-6 note
  predicted 2; that assumed samples act as mid-course checkpoints - the
  rubric's own density bands say otherwise. The judges are right.)
  Residual: opus split 1,1,3 - whether a SHORT program is transcription
  or construction stays a judgment call at the boundary; range is now
  1-3 instead of 0-4.
- tau-0007: 2 / 1,1 / 2,2 - stays in the designed 1-2 band, now partly
  for the multi-strand reason (judges cite tracking the timed
  side-request and upgrade-before-cancel ordering).

Battery-wide PLp/PLe profile after all patches (medians):
  chess      PLp ~3 / PLe 1     usaco-0004 PLp 3 / PLe 3
  usaco-0011 PLp 4 / PLe 3      tau-0007   PLp 2 / PLe 1-2
  ledger     PLe 4 / PLp low    migration  PLe 5 / PLp low
Coinciding values on some tasks (usaco-0004) are expected - independence
means the dimensions CAN diverge, not that they must; chess and the
designed items show divergence in both directions.

## Round 8: red-team of the frozen PLp/PLe (old rubrics as the lens)

Attack: coverage regression vs the old v2 texts + structural attacks.
Fixed: PLp preamble restores "allocating limited resources among them"
(resource-coupled planning was graded correctly by the coupling gates but
not named, inviting mis-routing). Deliberately NOT fixed, with reasons:
preamble length (real usability cost, but every clause maps to a measured
failure, alpha held with the long text, and the level-text "Critically"
gates degrade gracefully - rewording validated text without a new failure
signal is overfitting); per-step accuracy excluded from PLe on purpose
(error likelihood is the step's own demand; error DETECTABILITY is
PLe's); goal open-endedness remains unowned in the v2 agentic block
(team-level taxonomy question, not a PLp bolt-on); conversational
feedback L1/L2 off-by-one (tie-break + median absorb it). Verified clean:
environment change mid-execution, loosely-specified plans, no VO leak in
the construction clause.

## Round 9: HAL trace re-annotation (12 cp50 frames, old vs new, 72+72 labels)

Subsample: the mid-trajectory (cp50) checkpoint of every HAL trajectory,
re-annotated for PLp and PLe with the frozen rubrics, 3 judges, 1 seed
(matching the old label design). Paired stats on the same 12 frames:

| judge  | arm | separation | rho   | mean(PLe-PLp) | SD(diff) |
|--------|-----|-----------|-------|---------------|----------|
| haiku  | old | 0.00      | +0.68 | +0.92         | 0.49     |
| sonnet | old | 0.00      | +0.82 | +0.92         | 0.28     |
| opus   | old | 0.00      | +0.84 | +1.08         | 0.28     |
| haiku  | new | 0.00      | -0.03 | +1.25         | 1.01     |
| sonnet | new | 0.08      | +0.75 | +0.17         | 0.69     |
| opus   | new | 0.00      | +0.71 | +0.42         | 0.64     |

Reading, honestly:
1. The OLD failure signature replicates exactly on the subsample:
   separation 0.00 with a near-constant +0.9..+1.1 offset and SD(diff)
   ~0.3 - two ladders keyed on the same driver, different intercepts.
2. The NEW rubrics ELIMINATE the constant-offset signature for sonnet and
   opus: mean diff drops to +0.2..+0.4 and SD(diff) more than doubles -
   the PLp/PLe difference is now task-dependent, which is what two
   genuinely distinct, correlated demands look like. rho ~0.7 with
   variable diff is not collinearity; it is real co-variation.
3. Separation stays ~0 on THIS battery - and that is the battery, not the
   rubric: all 12 frames are SWE-bench bug-fix checkpoints, a family in
   which plan-finding and execution demand genuinely rise together. The
   original audit flagged exactly this ("one benchmark family, battery
   sampling not excluded"). On the heterogeneous pilot battery (rounds
   5-7) the same rubrics separate in both directions. Operational
   conclusion: the separation test needs a mixed-family trace set - the
   tau traces in labs/hal-traces/tau are the natural complement.
4. haiku-specific failure on traces: its new-rubric PLe pins at 4 (11/12
   frames) - it reads every mid-repair codebase frame as the L4
   "extend a large codebase without a test suite" anchor, while sonnet/
   opus credit the repo's test suite as checkpoint feedback and land at
   2-3. Frame-level ambiguity (does the agent have test access?) that the
   frame text does not settle; the 3-judge median absorbs it (median PLe
   3 on most frames). Candidate fix if it persists: state in the L4
   anchor that an available test suite makes errors checkpointed, not
   propagating.
5. Checkpoint-relative annotation ("demand still required from this
   point") adds a second noise source the pilot battery did not have:
   judges disagree about how much work REMAINS (e.g. whether the patch in
   the trace excerpt is already complete), independent of the rubric.

New-rubric label deltas move in sensible directions per frame: nearly-done
frames drop toward 0-1, mid-investigation frames rise to 3-4, and PLp/PLe
now move independently on 5 of 12 frames (old: 0 of 12).

## Round 10: preamble compression - sentinel verification

Commit "PLp/PLe: compress preambles losslessly" (PLe 481->384 words, PLp
194->179) re-checked on six sentinel cells with known expected values:
chess-trap PLe 1,1,0 (cap <=1 holds, 3 judges); ple-ledger PLe 4 (opus);
tau-0007 PLe 2 (sonnet); usaco-0004 PLp 3 (sonnet). All within expected
bands - no behavioural drift detected from the compression. The feedback
definition now names the success-signal reading explicitly ("the task's
success signal, not... an interlocutor's acknowledgement"), resolving the
conversational-feedback ambiguity by definition. Judges: haiku/sonnet/
opus subagents only (never the orchestrating model).

## Round 11: PLs (renamed from MSe) - first evaluation, separated prompt

First round run with the judging protocol moved into the shared
annotation prompt (task-not-solver + tie-break-lower stripped from rubric
text). Battery: two deduction traps (Sudoku with printed grid, chess
position - designed 0), usaco-0004 (fully specified statement, cap 1),
ab-0011 (gather from sources, 1-2), tau-0007 (queryable systems, cap 2),
and designed items at L3 (static segfault debugging), L4 (food-truck
lunch rush, visibly changing), L5 (intermittent radio interference,
unsignalled change). 3 judges x 3 seeds = 72 annotations.

Results (pls_redesign_pilot_labels.csv):
- alpha = 0.986 - the highest of any round. Designed-band compliance
  71/72 (one sonnet seed gave the L5 item a 4).
- Deduction traps: 27/27 at exactly 0, including USACO - judges quote
  the Critically-clause and route the difficulty to Planning explicitly.
  The trap PLe fell into in round 5 (and needed two patches to fix) was
  designed in here from the start and held on first contact.
- Every judge used all six levels; within-judge seed agreement 6-8/8.
- Cross-rubric profiles now three-dimensional and divergent: chess
  PLp3/PLe1/PLs0; usaco PLp3/PLe3/PLs0; tau PLp2/PLe1-2/PLs2; debug-type
  tasks get their demand assigned to PLs instead of leaking into PLp/PLe.

Red-team concerns pre-registered for this round and their outcomes:
L2/L3 gate (gathered vs inferred) - ab-0011 split 1/2, never 3: held.
L4/L5 gate (observable-when-looked-for vs unsignalled) - one off-by-one
seed: held. VO trap (tau many-lookups) - all 2s: held. MS routing was
not exercised by this battery (no social item) - open for the MSc round.

Verdict: the accumulated design pattern (single driver, verb spine,
categorical gates, designed-in traps, protocol in the prompt) produced a
rubric that passed its adversarial battery on the first attempt, with no
patch round needed. PLs is frozen alongside PLp and PLe.
