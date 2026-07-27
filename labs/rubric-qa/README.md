# rubric-qa — validation record for the agentic rubric re-key

The complete empirical record behind the re-keyed v2 agentic demand rubrics (`PLp`,
`PLe`, `PLs`, `MSc`). Every design decision on branch `rubrics/v2-improved` was tested
before it was kept, and this is where those tests and their results live. Narrative
summary for readers who do not want the detail: `docs/agentic-rubric-redesign.md`.

## How to read it

This file is a lab notebook: one section per round, in chronological order, each saying
what was tested, what happened, and what changed as a result — **including the rounds
where a designed test failed and a rubric had to be patched**. Those are the most
informative entries and are deliberately kept rather than tidied away.

Label files, one row per judge x task x seed:

| file | rows | contents |
|---|---|---|
| `plp_v2redesign_pilot_labels.csv` | 72 | PLp, new rubric — 8 pilot tasks x 3 judges x 3 seeds |
| `plp_oldrubric_pilot_labels.csv` | 72 | PLp, **old** rubric, identical setup — the paired baseline |
| `ple_v2redesign_pilot_labels.csv` | 63 | PLe — designed ladder plus traps |
| `pls_redesign_pilot_labels.csv` | 72 | PLs — designed ladder plus deduction traps |
| `hal_cp50_rekey_labels.csv` | 72 | PLp and PLe on 12 HAL trace frames, old and new side by side |
| `pilot_crossdim_labels.csv` | 30 | all four dimensions on 3 real pilot tasks, with the pre-registered value |

Pre-registrations — expectations written down *before* the judges ran, so that
"do the models annotate as we would" is measured rather than rationalised:
`prereg_expected.json` (round 14), `prereg_final.json` (round 16).

## Conventions

- Judges are always haiku / sonnet / opus, prompted through the repo's own
  `build_annotation_prompt`, and always write their reasoning before any score.
- A **designed** level (or **cap**) means the item was written to land at a known level.
  A **trap** is an item built to pull a rubric toward a neighbouring dimension — it
  passes only if the rubric refuses the pull.
- Krippendorff alpha is always reported **with the level distribution beside it**, never
  alone: see round 14 for why (alpha collapses under range restriction even when raw
  agreement is high).

---

## Round 1: inter-judge pilot of the re-keyed PLp rubric

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

## Round 12: MSc re-key + example concreteness pass

MSc re-keyed on ONE driver: how far the other party's stance must be moved,
how much it resists, and how much the moves must be adapted to what they do
in return. Spine: no stance to move (0) -> no steering needed (1) ->
steering a cooperative exchange (2) -> moving an open stance (3) ->
overcoming resistance (4) -> reconciling conflicting stances (5).

Battery (3 designed traps + ladder): msc-mstrap (read a poker opponent, no
interaction -> MS not MSc), msc-ceetrap (persuasive newspaper column),
msc-cafe (1), msc-history (2), tau-0007 (<=2), msc-vet (3, the STAKES
trap), msc-headcount (4), msc-water (5).

Ladder held first try: history 2, vet 3, headcount 4, water 5, mstrap 0.
The stakes demotion is confirmed working: a grave, emotionally heavy
conversation with a trusting, non-opposing family scores 3, not 4 - judges
cite the absence of opposition explicitly. Under the old rubric this was
L4 by definition ("health, jobs, finances or safety"), which graded
consequences rather than communicative demand.

THE ROUND'S FINDING - the CEe trap failed 3/3 (all judges gave 3 vs
designed <=1), and they were faithful to the text: the preamble said
"steering an interaction, not composing its messages", but L3-L5 never
REQUIRED an exchange, so one-shot persuasive composition slid into L3
("brought there by argument, framing or compromise" describes an op-ed
exactly). Same class of defect as PLe's action-definition gap: the
distinguishing structural feature was named in the preamble but not
enforced at any gate.

Fix (commit "MSc: require an exchange"): interactivity is now a gate.
Preamble adds "where no exchange takes place - a message is composed and
sent, with no opportunity to adapt to any response - the demand here is
minimal, however persuasive or delicate the message must be"; L1 widens
from "scripted exchange" to "communication that needs no steering"
(scripted OR one-way); the column becomes an L1 contrast anchor; L3 now
requires the stance to be moved "in exchange with them... adjusted to what
they say back".

Verification: ceetrap 1,1,1 (was 3,3,3). Held-out generalisation test - a
eulogy for a colleague's funeral, never mentioned in the rubric - also
scores 1, so judges applied the gate rather than matching the anchor. No
drift: vet still 3, tau still 2.

Example concreteness pass (all four PL/MSc rubrics), criteria taken from
v1: anchors name a specific situation the reader can picture, at instance
rather than class level, with the distinguishing detail stated. Edits:
PLp x4 (contest-programming anchors now describe the technique rather than
the tier; the two L5 anchors no longer share the "where the division into
X must itself be discovered" frame - near-duplicate phrasing between
adjacent anchors is itself a defect), PLe x2, PLs x2, and all MSc examples
written to this standard from the start.

## Round 13: consolidation pass over all four re-keyed rubrics

Revision of PLp, PLe, PLs and MSc together, stressed against the artifact,
the old v2 texts, and v1's form; validated with HAIKU as the primary judge,
since the requirement is that a weak model can annotate accurately.

Structural audit: all four now carry levels 0-5 with v1's intensity names
(None / Very low / Low / Intermediate / High / Very high), 3-4 anchors per
level, one preamble paragraph. Preamble lengths 173-227 words against v1's
range (MS 66, CEe 217) except PLe at 375, accepted: PLe carries four
definitional clauses no other rubric needs (action, feedback,
transcription-vs-construction, budgets/branches), each traceable to a
measured failure, and its tail was compressed again this round.

Changes made:
1. v1's scale-framing sentence was MISSING from all four and is now added
   ("The level of cognitive demands progresses from ... to ..."). This is a
   v1 hallmark (present in MS.txt and CEe.txt) and orients a weak judge
   before it reads any level.
2. PLp L4's contest-programming anchor no longer refers to "the hardest
   contest tier" - a property a judge cannot read off a task statement -
   and instead describes what makes it hard, parallel to the L3 anchor.
3. PLs L2's inventory anchor states the Volume contrast explicitly;
   PLe L0 replaces the dated "Google search from google.com".
4. MSc L3's doctor anchor made imperative for consistency with every other
   anchor in the set.

Cross-dimension weak-model sentinel (10 cells, haiku only): 8/10 exact,
both misses off-by-one at the MSc L3/L4 boundary on items that were
themselves ambiguous about resistance. Correct on: PLp 3 (chess), PLp 0
(300-step protocol - length is VO), PLe 1 (chess write-down), PLe 4
(charity ledger), PLs 0 (Sudoku), PLs 3 (intermittent web errors), PLs 4
(air-traffic control), MSc 1 (opinion essay).
Continuity note: air-traffic control was an L4 anchor in the OLD MSe too,
but for the wrong reason ("many flights, known procedures"); it is L4 here
because the state changes continuously and every change is visible.

Fix from the two misses - MSc L4 gains an anti-inflation clause: "being
displeased by the message is not itself resistance: what marks this level
is that the other party is holding out for a different outcome, not merely
that they dislike the one proposed." Post-fix: tau-0007 2 (haiku and
sonnet; was 3), vet 3 with haiku quoting the new clause verbatim
("distress is not resistance"), landlord still 4 - the clause does not
over-correct genuine resistance.

## Round 14: cross-dimension validation on real pilot tasks, against
## PRE-REGISTERED expectations

Corpus: whole tasks from pilot/tasks.csv, one per benchmark family
(swe-0090 SWE-bench, tau-0089 tau-bench retail, ab-0011 AssistantBench),
each annotated on all four re-keyed dimensions by haiku, sonnet and opus,
using the current rubric texts and the shared prompt. HAL trace
checkpoints were deliberately NOT used: round 9 showed checkpoint-relative
framing ("demand still required from this point") adds a disagreement
source orthogonal to rubric quality. Judges were required to write
numbered reasoning steps BEFORE stating any score.

Expected labels for all 12 task x dimension cells were written to
prereg_expected.json BEFORE any judge ran, so "do the models annotate as
we would" is measured rather than rationalised.

Result vs pre-registration: 9/12 EXACT, 12/12 within +-1.
Inter-judge: 62% of judge pairs exact, 92% within +-1, 3/8 full cells
unanimous, one cell with a 2-level spread.

Krippendorff alpha on these cells is 0.393 - far below rounds 11-13
(0.86-0.99) - and this is a RANGE-RESTRICTION artefact, not a regression:
real pilot tasks all land between 0 and 3 (SD 0.67, 18 of 28 labels are
exactly 2), so expected disagreement is tiny and alpha punishes any
deviation. The designed batteries spanned 0-5 and alpha was high there.
Two lessons: (i) report alpha only alongside the level distribution;
(ii) THE BATTERY IS THE PROBLEM, as the original audit suspected - these
benchmark families genuinely do not exercise the top of any scale, so
high-demand validation needs designed items or harder benchmarks.

Judge tendencies: haiku sits +0.25 above the cell median on average,
sonnet and opus -0.12 - haiku's mild inflation is consistent with earlier
rounds and is absorbed by the 3-judge median.

Cases where the judges were arguably RIGHT and the pre-registration wrong:
tau-0089 PLe - sonnet and opus scored 1, noting every tau-bench tool call
returns an immediate success/error signal, so the environment checks each
step; the pre-registered 2 assumed checkpoint-level feedback. Their
reading follows the rubric more exactly than mine did.

The one recurring rubric-level ambiguity: PLs L2/L3 on debugging tasks
where the source IS readable. swe-0090 split 3/3/2 - haiku and sonnet
treat "why does the check reject a working lookup" as hidden state to be
inferred from symptoms; opus treats the source as directly readable, so
gathered (L2), with the mechanism following by deduction. Both readings
are defensible under the current text. This is the same boundary that the
PLs L0 clause addresses for fully-given state ("deducing what known facts
imply is not situational understanding") and is a candidate for one
clarifying sentence at L2/L3 if it recurs at scale - not patched now,
because a single 3/3/2 split is not enough evidence to justify moving a
boundary that is otherwise behaving.

## Round 15: PLs L2/L3 sharpened - what "directly observable" means

Round 14 left the PLs L2/L3 split on debugging-with-readable-source
unpatched, on the grounds that one 3/3/2 split is thin evidence for moving
a boundary. That reasoning was wrong, for a reason worth recording: this
is not a boundary MOVE. PLs already lists "debug why a program crashes" as
its own Level 3 anchor, so the rubric had already decided the case; opus
nonetheless scored L2 because L2's phrase "directly observable once looked
at" can be read as "the source is there to read". The text under-determined
its own commitment - a wording defect, not a calibration question.

Patch: L2 now defines the term - "an observation is direct when looking in
the right place returns the fact itself, rather than evidence from which
the fact still has to be worked out" - and L3 states the complement -
"because no single observation returns it, even when everything needed to
work it out is there to be looked at". The L3 debugging anchor is reworded
to make the same point ostensively ("the whole source is there to read,
but no line of it announces the fault").

Verification (3 judges on swe-0090, plus three inflation controls):
- swe-0090 PLs: 3 (haiku), 3 (sonnet), 2 (opus) - the NUMBERS did not
  change, but opus's justification did, and that is the result. It no
  longer argues "the source is readable"; it argues that THIS issue report
  hands over the cause ("I believe it was fine until #29408 was
  implemented"), so for this particular task the state is given rather
  than hidden. That is a defensible task-specific reading, not a
  misreading of the gate. The wrong reading is now blocked; the residual
  split is genuine task ambiguity and stays within +-1 around a median of
  3, which matches the rubric's own anchor.
- Controls, all unchanged at 2: tau-0089 (opus), ab-0011 (sonnet),
  and a 4,000-item / sixty-shelf inventory (haiku) - the sharpened wording
  does not inflate ordinary gathering into inference.

Note on Krippendorff alpha, for whoever reads round 14: alpha 0.393 there
is a prevalence artefact (18 of 28 labels were exactly 2, so chance
agreement is already high and alpha over-penalises). Evidence that the
ladders do resolve where real tasks live comes from round 1: PLp over 8
pilot tasks spanned levels 1-4 with SD 0.85-1.15. Always report alpha with
the level distribution beside it.

## Round 16: final validation on the hardest real pilot task

usaco-0011 (USACO 2025 US Open, Platinum) annotated on all four
dimensions, expectations pre-registered (prereg_final.json).

  dimension  judges              median  pre-registered
  PLp        3 haiku, 4 sonnet, 4 opus   4       4  EXACT
  PLe        3 opus                      3       3  EXACT
  PLs        0 opus                      0       0  EXACT
  MSc        0 haiku                     0       0  EXACT

Profile 4 / 3 / 0 / 0 on a real benchmark task: high planning demand,
moderate execution demand, no situational or social demand at all. This
is the discriminant-validity claim demonstrated on a real task rather
than a designed one - under the OLD rubrics the same task would score
high on PLp, PLe and MSe together, because all three were keyed on
horizon and complexity.

haiku's 3 against sonnet/opus's 4 is the known L3/L4 offset first
diagnosed by the gate-walk in round 3: haiku reads "established methods
exist for tasks of this kind" at the class level. The 3-judge median
absorbs it, as designed.

## Round 17: NEGATIVE RESULT — our PLp underperforms on the rivercross
## solver-backed oracle (labs/rivercross)

`labs/rivercross/` was already in the repo and this work did not use it. It is a
controlled testbed with something none of our batteries have: an **exact BFS solver as
a value oracle**, so every judged state carries a true remaining cost-to-go. It also
already reports a rubric-revision result for PLp.

We ran OUR current PLp rubric on their 43 leak-free states, substituted into their own
prompt scaffold (dimension-agnostic, leak-free, demand-to-go), judged by haiku, and
correlated against the solver's cost-to-go.

| arm | Spearman vs cost-to-go | SD | label distribution |
|---|---|---|---|
| their v10 (prior wording), haiku | +0.374 | 0.42 | {1:33, 2:10} |
| their v11 (search-size rubric), haiku | **+0.826** | 0.78 | {0:12, 1:17, 2:14} |
| their v11, sonnet / opus | +0.855 / +0.894 | 0.87 / 0.79 | spans 0–3 |
| **OUR re-keyed PLp, haiku** | **+0.497** | **0.53** | **{1:39, 2:1, 3:3}** |

**Our rubric is much worse than theirs on this testbed, and only modestly better than
the wording we replaced.** 39 of 43 states collapse to Level 1.

Diagnosis — two causes, both real:

1. **Our bottom rung is keyed on PROVISION, not on absence of search.** L0 is "the plan
   is given". In these frames 12 states are one crossing from the goal: no plan is
   *given*, yet essentially no planning remains. Their v11 puts those at 0; our ladder
   has no natural home for them, so they pile into L1. Our L0 does say "completed by a
   single action", but every L0 example is a task *type* (a lookup, a conversion, a
   provided protocol) rather than a task *nearly finished*, so a judge does not read it
   that way.
2. **Our L1 gate is knowledge-based and swallows a whole puzzle family.** "A single
   standard, well-established routine covers the whole task" is true of river-crossing
   as a genre, so haiku applied it everywhere — ignoring the conjoined condition that
   "any reasonable order succeeds", which is plainly false when most orders strand a
   forbidden pair. A knowledge gate discriminates well ACROSS heterogeneous families and
   poorly WITHIN one homogeneous family, where the variation is in search size.

Scope of the problem: this is the **demand-to-go** framing — scoring the demand still
required from a mid-trajectory state. That is the framing rivercross calls its workhorse
(method 1b) **and the framing of the HAL cp25/cp50/cp75 frames we used in round 9**, so
this affects those results too. Our rubric was designed and validated for whole-task
annotation, and it has not been calibrated for demand-to-go.

This does not invalidate the whole-task results (rounds 1–16 stand), but it does mean
the claim "PLp is validated" must be qualified by framing until this is fixed.

Not patched here: the fix interacts with a methodology question — whether one rubric
should serve both framings, or whether demand-to-go needs its own calibration — which
is a decision for the team, not a wording tweak. Options and evidence in the response
to this round.

Convergence worth noting: rivercross independently reached several of our conclusions —
key PLp on search size; PLe's disagreement was caused by one ambiguous word, *feedback*,
fixed with an operational definition of reward ("the environment's success signal — not
observation, not legality"), which is nearly our own wording; levels should be a
mutually-exclusive logical partition; and the weakest judge lags for capability reasons
on dimensions whose annotation is itself a reasoning task. Two independent efforts
reaching the same fixes is evidence those fixes are right.

## Round 19: PLe checked against the rivercross calibration — one real
## defect found and fixed

Ran our PLe on rivercross's 49 captured-trajectory states (`ple/frame_PLe_1b.csv`),
substituted into their own prompt scaffold, judged by sonnet (their reference judge:
their sonnet and opus agree at QWK 1.00 there).

**The defect.** Our first run put 41 of 49 states at Level 1, with the judge's reason
given as "every move checked immediately; illegal ones rejected". That is the exact
failure mode rivercross documented and fixed — reading *legality* as reward. We had
already excluded observation from our feedback definition but not legality.

Adding "not a check that an action was legal or well-formed" to the **preamble** changed
nothing: the run came back at Level 1 again. The reason is worth recording, because it is
the third time this pattern has bitten in this project: **PLe's Level 1 text itself said
"or invalid actions are simply not accepted"**, so the preamble exclusion contradicted the
level it governed, and the judge — correctly — followed the level. A distinction stated
only in the preamble is not enforced.

Fix applied at the level: an environment that refuses invalid actions counts as
step-by-step checking *only where being accepted establishes that the step did what it was
for*; where an action can be accepted and still be useless — a legal move that makes no
progress — the refusal is not feedback and the task belongs higher.

| arm | distribution | modal level |
|---|---|---|
| ours, before fix | {0:8, 1:41} | 1 — **wrong regime** |
| ours, after fix | {0:8, 3:41} | 3 — "no feedback until goal" |
| their final PLe rubric (sonnet) | {0:8, 2:40, 3:1} | 2 |

After the fix our judge identifies the regime correctly: no informative signal until the
goal, errors reversible, so self-checked. The eight states scored 0 are the *same eight*
both rubrics single out.

**Correlation with the solver oracle is ~0 for everyone, and that is the expected
answer.** On the 26 states where the PLe frames overlap the method1b ground truth:
ours −0.098, their haiku −0.185, their sonnet −0.228. PLe is not supposed to track
remaining distance — rivercross themselves judge PLe by cross-model agreement, not by
oracle correlation, and reserve the oracle test for PLp. Our design predicts this
directly: horizon is routed to Volume, so within a fixed environment the error-detection
regime is invariant and PLe is near-constant by construction. Distance-to-go is carried
by VO and PLp, which is the anti-collinearity choice working as intended.

Residual: two states we score 0 have true remaining distance 3 and 5 — sonnet judged that
one crossing would finish when it would not. That is a solver error by the judge, the same
capability effect seen for haiku on PLp, not a rubric defect (n=2).

Net: PLe survives the rivercross check with one genuine wording fix, and the fix
reproduces rivercross's own independently-derived conclusion about legality.

## Round 20: systematic audit for the preamble-only failure mode, and
## binding what it found

Three of this project's failures had one shape: **a distinction stated in the preamble
but not echoed at any level, which judges then ignore** (PLe's action definition, MSc's
interactivity gate, PLe's legality clause). Rather than wait for a fourth, we audited all
four rubrics mechanically for the pattern. Seven clauses were preamble-only:

| rubric | clause | verdict |
|---|---|---|
| PLe | transcription vs construction | **bound at L3** |
| PLe | conditional plans | **bound at L4** |
| PLe | limited budgets, time pressure | **bound at L5** |
| PLe | memory routing | **bound at L3** |
| PLs | own-work vs world (the PLe boundary) | **bound at L4** |
| PLp | resource allocation | left — an inclusion in the concept, not a discriminator |
| MSc | self-control exclusion | left — excludes something no dimension scores |

Two were deliberately left: neither can change a level, so binding them would add text
without adding constraint. The other five were bound **at the level where the confusion
would occur**, not by extending the preamble further, and each was given the
anti-inflation half as well as the inclusion — e.g. L5 now says a deadline that still
allows each step to be verified does **not** put a task there.

Every binding was then tested, since untested clauses are exactly what caused the
problem. Sonnet, one item per clause:

| test | targets | designed | result |
|---|---|---|---|
| three final submissions, none graded until close | budgets → L5 | 5 | **5** ✓ |
| 400 records before a 5 p.m. deadline, each validated on entry | deadline must NOT inflate | 1 | **1** ✓ |
| router flowchart, each test immediate and unambiguous | conditional plan must NOT inflate | 1 | **1** ✓ |
| PLs, partway through: fault already found and confirmed | demand-to-go | ≤1 | **0** ✓ |
| MSc, partway through: terms agreed, only the date left | demand-to-go | ≤2 | **1** ✓ |

5/5. The judge quoted the new clauses verbatim ("spending one of a strictly limited
number of attempts", "the deadline still allows each entry to be verified").

Notable: PLs and MSc handled the **demand-to-go** framing correctly without any change.
The prediction going in was that PLs would show PLp's provision-vs-remaining bug — its L0
is also keyed on state being "given" — but judges read "already established" as
satisfying it. So the round-18 defect was specific to PLp's wording, not general to the
family. Prediction wrong, recorded as such.

Remaining known weaknesses after this round: the weak-judge gap on PLp (haiku 0.647 vs
sonnet 0.857); no human anchor; separation on real traces unproven pending a mixed-family
battery; MSc has no external ground truth of any kind; and the rivercross-1b-refactor
fork is unreviewed.

## Round 21: language naturalised to v1 register — no degradation, small gain

Two constructions were more stilted than v1 and were changed:

1. **"This criterion assesses …" → "This rubric assesses …"**. A survey of all 19 v1
   rubrics shows "rubric" is the house style (15 of 19: *This rubric assesses / evaluates /
   defines*, *The following rubric is designed to*); only AS, MS and QLq say "criterion". We
   had picked the minority form.
2. **"This demand level is characterized by the plan being assembled: …" → "Tasks at this
   level require the plan to be assembled: …"**, and for Level 0, "The task requires no
   planning: the plan is given — …". No v1 rubric talks about *the demand level*; they talk
   about *the task* ("Tasks at this level require …", "The task involves …", "Performance in
   this task is improved by …"). The verb spine is preserved and now sits immediately after
   "require", where it is at least as prominent as before.

Regression, run on the naturalised text:

| check | before | after |
|---|---|---|
| PLp vs solver oracle (sonnet, 43 states) | +0.857 | **+0.894** |
| PLp label agreement before/after | — | 41/43 identical |
| PLp Level 0 partition | exact (all true distance 1) | still exact |
| PLe chess trap (plan-hard, execution-trivial) | ≤1 | 1 ✓ |
| PLe ledger (silent propagation) | 4 | 4 ✓ |
| PLs stable hidden fault | 3 | 3 ✓ |
| MSc opinion column (the CEe trap) | 1 | 1 ✓ |
| MSc grave-but-trusting diagnosis (the stakes trap) | 3 | 3 ✓ |

No degradation anywhere; the oracle correlation improved from 0.857 to 0.894, which now
exceeds rivercross's own v11 with the same judge (0.855) and matches their opus (0.894). The
gain is within noise for n=43 and is not claimed as an effect — what matters is that
naturalising the register cost nothing.

## Round 22: final polish pass — five small fixes, three deliberate non-fixes

A fresh end-to-end read of all four rubrics as a reviewer would encounter them.

Fixed (sentinel-checked where load-bearing):
1. **Metadata lines** were stale ("revised: 2026-07-25/26") and still said "DRAFT,
   unvalidated" — no longer true after 21 rounds and an oracle validation, and the `#!`
   line is text the judge reads: telling a judge its rubric is unvalidated is not
   neutral. Now "DRAFT for team review", dated, with a pointer to the validation and
   with MSc's weaker evidence base ("designed items only") flagged honestly rather
   than papered over.
2. **PLp mixed US/UK spelling within one file** ("recognising" at L1, "Recognizing" at
   L3/L4); unified to UK, matching the rest of the set.
3. **PLe L0's chess anchor** kept old-v2 phrasing ("Evaluate the possibility of
   achieving checkmate in chess in a single move") — awkward, and domain-colliding with
   L1's chess contrast anchor without being a deliberate pair. Now "Say whether
   checkmate can be delivered in one move in a given chess position."
4. **PLe's feedback sentence** nested three em-dash clauses; the inner one is now
   parenthesised. No semantic change.
5. **PLs preamble** said consequences are "assessed by reasoning and Planning (PLp)",
   which reads as if "reasoning" were a dimension; now "by the reasoning dimensions and
   by Planning (PLp)".

Sentinels on the two load-bearing edits (3 and 4): the chess trap still scores 1, and a
purpose-built legality probe (a referee that rejects illegal moves but accepting a move
says nothing about progress) scores 3 with the judge explicitly citing
"legality, not progress". Both clauses still bind after the rewording.

Deliberately NOT changed, with reasons:
- **No "Critically" clause at any Level 5.** Top levels have nothing above them to
  protect against; adding floors there is text without constraint. (PLe L5's
  budget/deadline sentence is a routing, not a floor.)
- **No further anchors anywhere.** Every level holds 3-5; the remaining known gaps
  (MSc external ground truth, weak-judge PLp) are not anchor problems.
- **PLe's preamble stays long** (406 words). Position unchanged from round 13: every
  clause maps to a measured failure, compression has been done twice, and further
  cutting without a new failure signal is risk without payoff. Flagged for the team in
  the report instead.

With this pass the rubrics are, to our knowledge, out of known textual defects; what
remains (report §6) requires new evidence, not new wording.

## Round 23: red-team of v2 against v1 — three findings, one of which is a
## power analysis that closes a question we could not otherwise answer

### 23.1 Criterion validity cannot be tested on the data we have (and never could)

The strongest attack on this work is that we optimised *discriminant* validity —
separation, agreement, oracle-tracking — and never tested *criterion* validity, i.e.
whether the labels predict solver success. If the old multi-driver labels predicted
success better despite being psychometrically uglier, the redesign would be in trouble.

We checked whether the HAL trace set can answer this, using the OLD labels, which costs
nothing. It cannot:

- 60 frames, but only **12 trajectories** — the cp25/cp50/cp75 frames of one attempt share
  one outcome, so the effective n is 12, not 60.
- **o3mini succeeds on 0 of 20 frames.** With zero outcome variance in that agent, pooling
  across agents is pure confounding: any demand difference between agents is read as a
  success effect.
- Pooled AUC for the old labels runs 0.32–0.48 — at or below chance, and in the *wrong
  direction* (demand slightly higher on successes). Within opus41 alone (~8 trajectories)
  old PLp gives AUC 0.657, right-direction but far too small to mean anything.

Two consequences, and the second is the important one:

1. Spending judge calls to produce new labels for this comparison would have been wasted;
   we did not.
2. **The old rubrics were never criterion-validated either.** So the attack is currently
   unanswerable *in both directions* — this is not a case of replacing a criterion-validated
   instrument with an unvalidated one. Both stand on the same (absent) evidence, and the
   redesign is ahead on every axis anyone has actually measured.

What would be needed: outcomes from many more trajectories, and agents with intermediate
success rates (an agent at 0% or 100% contributes nothing). `pilot/tasks.csv` × several
agents is the natural vehicle, but it requires running agents, which this validation
deliberately never needed.

### 23.2 Our style is closer to v1 than it looks — except in one respect that cannot change

Asked whether the v2 rubrics could be rewritten in v1's flowing register, we checked what
v1 actually does rather than trusting impressions:

| device | v1 usage |
|---|---|
| `Critically, …` constraint flags | **present in v1** — MS.txt, 1 of 19 files |
| negative constraints ("does not …") | 9 of 19 files |
| contrastive phrasing ("rather than") | 9 of 19 files |
| **naming another dimension by code** | **0 of 19 files** |

So the "Critically" convention is inherited from v1, not invented here, though it is rare
there; it could be dissolved into the "does not / rather than" phrasing that *is* v1 house
style, at some risk to salience.

The real deviation is the last row: **v1 never cross-references another dimension, and our
routing sentences do so constantly.** That difference is not stylistic. Routing is the
mechanism that fixes the collinearity — v1 could omit it because v1 was never built to be
non-collinear. Removing the dimension names to match v1's register would revert the fix.
Recommended position: keep the routing, and treat any register alignment as optional
polish confined to the `Critically` flags.

### 23.3 Cross-family level comparison was never valid, and we should say so

v1 anchors levels implicitly on human populations ("graduate-level textbook section"),
v2 on procedure coverage and structural gates, so v1-Level-4 and v2-Level-4 need not sit
at the same difficulty altitude. This is real but **pre-existing and not introduced here**:
v1 VO is defined by wall-clock bands and v1 CEe by expression sophistication, so VO-4 and
CEe-4 were already incommensurable. A demand profile is a vector of per-dimension
positions, not a set of comparable magnitudes, and ADeLe's method — fitting a success
curve per dimension — never requires commensurability. The fix is therefore documentation,
not re-anchoring: profiles must not be read across dimensions ("this task is 4 on CEe but
only 2 on PLp" is not a statement about relative difficulty). A cheap optional measurement
would quantify any systematic v1/v2 offset: annotate one task set on both families and
compare level distributions.

### 23.4 MSm/MSc are siblings, and their relationship should be expected, not discovered

Correction from Pablo: v1's `MS` becomes `MSm` within an `MS` family that also contains
`MSc`. All four rubrics now route to **MSm** rather than the family code. The two are
siblings, and they stand in an *asymmetric dependency*: high MSc essentially requires high
MSm (stances cannot be moved without being read), while high MSm without MSc is common
(read a poker opponent you never speak to). Note that v1 MS's own Level 5 example is a
multi-party negotiation — nearly our MSc Level 5 scenario — so the two will correlate on
exactly those tasks. This is reading-versus-moving, a functional dependency, **not** a
shared driver, and per the original audit's decision rule an expected asymmetric
correlation is reading (4), not a merge candidate. Recording it here so that whoever first
computes an MSm/MSc correlation finds it predicted rather than alarming.

## Round 24: is v1 multi-driver? No — and a hypothesis of ours failed its test

Prompted by the worry that going single-driver puts v2 out of step with v1.

### 24.1 v1 ladders are single-driver too

Reading the level ladders (not the preambles) of VO, AS, CL, MCu, QLl, SNs, MS: **every one
moves on a single quantity.** VO on elapsed time; AS on amount of attention; CL on depth of
conceptualisation; MCu on metacognitive effort; QLl on logical complexity; SNs on spatial
transformation complexity; MS on depth of mentalising. Preambles enumerate *facets* or
*manifestations* of the ability, but the ladder never conjoins independent drivers.

This matters for how the redesign should be described. **The old v2 agentic rubrics were the
anomaly, not v1.** Their ladders genuinely conjoined horizon AND agent count AND
open-endedness AND environment dynamics, which is what made them collinear. Going
single-driver did not deviate from v1 — it brought v2 back into line with it. The report and
PR should say this, because "we did something v1 doesn't do" is a natural reviewer objection
and it is simply false.

### 24.2 A hypothesis of ours failed: operationalisation quality did not predict agreement

Having found v1 single-driver, we tested a follow-up: v1 dimensions differ in how well the
single quantity is *operationalised*. Some use unanchored gradables ("minimal / some /
moderate / substantial"), others name concrete constructs. Hypothesis: the anchored ones
should show better inter-judge agreement, which would localise where v1 could be improved.

A/B on 10 pilot tasks, haiku vs sonnet, CL (vague magnitudes) against QLl (named constructs
— syllogisms, conditionals, biconditionals, nested structures):

| v1 dim | style | exact | within ±1 | α |
|---|---|---|---|---|
| CL | vague magnitudes | 2/10 | 10/10 | 0.696 |
| QLl | named constructs | 2/10 | 9/10 | 0.501 |

**The hypothesis is not supported** — the vaguer rubric agreed slightly *better*, and exact
agreement was 2/10 for both. Recorded as a failed prediction rather than dropped. Caveats
that stop this being evidence in the other direction either: n=10, two judges, one seed,
severe range restriction (all labels 0–3), and SWE-bench/AssistantBench tasks are not
obviously well-suited to either dimension.

What can be said: both v1 dimensions show low *exact* agreement on this set with most
disagreement off-by-one, i.e. a judge-offset pattern rather than disorder. Whether v1's
boundaries would benefit from sharpening is **open**, and this test does not settle it.

### 24.3 Whether to act on it is a different question from whether it is true

Even if a v1 dimension were shown to be improvable, the cost–benefit differs sharply from
v2's. v2 agentic is an unpublished draft: rewriting it costs a re-validation we were doing
anyway. v1 is published, has empirical results built on it, and existing label sets assume
it; changing it breaks comparability with those results and invalidates the labels. The
responsible sequence is measure first, on a proper battery, and only then ask the v1 owners
whether any finding is worth that price. Nothing here justifies touching v1, and this work
proposes no change to it.

## Round 25: the example-placement test — do the examples obviously belong to the levels they claim?

A rubric's examples do most of the annotation work: a judge reaches for the example that
resembles the task in front of it long before it parses a "Critically" clause. Rounds 1–24
tested the *level descriptions*. This round tests the *examples*, and it found errors the
earlier rounds could not.

### 25.1 The test

Strip every `Examples:` block out of a rubric, shuffle its examples into one pool, hand a
judge the full level descriptions plus the pool, and ask it to put each example back on the
level it illustrates — reasoning first, level second. An example that is "obviously the level
it claims" is one a judge with the rubric in hand can return to its own level.

Three judges (haiku, sonnet, opus), 77 examples across `PLp PLe PLs MSc`, 231 decisions per
run. Explicit `at Level N` cross-references inside example text were rewritten to "at the
level below" so they could not leak the answer. Pre-registration in `prereg_r25.json`;
all 468 decisions across three runs in `example_placement_labels.csv`.

Scoring: per example, how many of three judges recover the true level. 3/3 clean, 2/3 soft,
≤1/3 defective. Pre-registered decision rule: rewrite at ≤1/3.

### 25.2 Result: 75% clean before, 92% after

| | PLp | PLe | PLs | MSc | all |
|---|---|---|---|---|---|
| before | 13/20 | 13/19 | 17/18 | 15/20 | **58/77 (75%)** |
| after | 17/20 | 18/19 | 17/18 (untouched) | 19/20 | **71/77 (92%)** |

`PLs` needed no example changes at all — 17/18 first time.

### 25.3 Three examples were on the wrong level, and the judges were right

The valuable failures were not vague examples but examples that *contradicted their own
level description*. In each case the judges' reasoning derived the correct level from the
rubric text, and the rubric was wrong.

- **`PLe` L1, "Find the winning line in a chess position and write it down"** — 0/3, all three
  said L0. The example's own parenthetical said "carrying it out is a single step", which is
  L0's defining condition verbatim. Moved to L0.
- **`MSc` L5, "Negotiate the release of hostages with a captor"** — 0/3, all three said L4.
  L5 requires *several* parties with mutually exclusive positions; a captor is one
  counterpart, which is L4's "the opposition comes from a single counterpart". Rewritten so
  the captor, the police commander and the families each demand a different course.
- **`PLp` L1, "Decide the order in which to run three independent errands"** — 0/3, all three
  said L2. Three errands *are* a decomposition into a few independent subtasks, which is L2's
  definition. Replaced.

Two more were genuinely mis-levelled rather than merely ambiguous: `MSc` L3's
doctor-delivering-a-diagnosis (3/3 said L2 — nothing was being moved, so the example was
rewritten to include a treatment the patient is at first reluctant to start), and `PLp` L4's
mountaineering expedition (expedition planning has established methods and the subtasks *can*
be listed at the outset, i.e. L3 — replaced with a first ascent of an unclimbed face, where
the decomposition itself is undiscovered).

### 25.4 The L4/L5 boundary is the residual soft spot, and it is not an example defect

Pooling the two `PLp` runs that share 18 items (6 votes each), four items fall short of
unanimous, and three of them sit at the top of the ladder: the synthesis route (L5, 3/6),
the multi-year research programme (L5, 4/6) and the ML-paper replication (L4, 4/6). The
dissent is always downward and always by one level, and the losing reading is defensible —
retrosynthesis *is* an established procedure, replication *is* an established activity. This
is a property of where "no established procedure exists at all" stops being crisp, not of
these three sentences. Recorded rather than patched; chasing it further would overfit the
examples to this test.

### 25.5 A cross-dimension note made one example *harder* to place

Following the aim of making examples separate confusable dimensions, a note was added to
`PLp` L5's synthesis route saying that carrying out such a synthesis is `PLe`. It had been
3/3 before the note and fell to 3/6 after. The mirror-image note on the `PLe` L5 synthesis
example cost nothing (18/19 for that run). So the note was kept on the `PLe` side and
reverted on the `PLp` side.

The general lesson: a contrast note helps when it names what the example is **not**, and
hurts when it invites the judge to weigh a *different* dimension's difficulty while placing
the item. Reported because it contradicts the intuition that more signposting is always
better.

### 25.6 Separating examples now in the set

Twelve examples carry an explicit cross-dimension contrast, including two families of
minimal pairs that differ only in which dimension owns the difficulty:

- **chess**: `PLp` L0 (only one legal continuation) · `PLp` L3 (middlegame, look-ahead) ·
  `PLe` L0 (find the line, write it down) · `PLs` L0 (position fully shown)
- **chemical synthesis**: `PLp` L5 (devise the route) · `PLe` L5 (carry it out, no step
  retriable)

Both pairs hold the domain constant and move only the driver, which is what lets a judge see
that the dimensions are asking different questions about the same task.

## Round 26: does the round-25 example surgery survive an adversarial battery?

Round 25 changed fifteen examples across `PLp`, `PLe` and `MSc`. Every earlier validation —
the rivercross solver oracle, the designed batteries, the trap batteries of rounds 5–21 —
was run against the *old* examples, and examples drive judges harder than level text does.
So the edits had to be treated as a possible regression, not an improvement to be assumed.

### 26.1 The battery

24 held-out designed items, none of them a rubric example, each scored on **all four**
dimensions by haiku, sonnet and opus: 288 decisions. Pre-registration in `prereg_r26.json`,
all 450 decisions across three rubric versions in `stress_battery_labels.csv`.

- **8 trap-regression items** — held-out re-wordings of the traps that earlier rounds
  established: deliberation-is-not-execution, legality-is-not-feedback, stakes-without-an-
  exchange, volume-without-planning, deduction-without-observation, transcription.
- **10 attractor probes** — each sits one level *above* a newly written round-25 example on
  the same dimension. A new example is a new attractor, and the risk is that a vivid one
  drags its neighbours. The unclimbed-face item at `PLp` L4 was the main worry: a very
  extreme L4 anchor could raise the L4 bar and push genuine L4 tasks down to 3.
- **6 sentinels** — analogues, never copies, of the levels the rubrics are meant to nail.

### 26.2 Result: the surgery holds

**23 of 24 items pass on their target dimension with 3/3 judges.** All eight traps hold. All
six sentinels are exact. Every attractor probe holds: `PLp` L4 replication stays at 4 (it had
wobbled to 3/3/4 during round 25's placement runs, so the vivid new L4 anchor did *not* raise
the bar), standard-technique contest problems stay at 1, per-screw assembly stays at `PLe` 1,
and two-party custody stays at `MSc` 5 despite the new three-party L5 example.

The single miss is `N10` — converting a thousand temperature readings and producing monthly
means — where opus scored `PLp` 0 against a pre-registered 1–2. The sharpened L0 conversion
example ("a single computation; there is nothing to sequence or decide") is the likely pull.
2/3, one judge, left as recorded rather than patched.

### 26.3 A real defect the battery found: `PLs` was absorbing self-inflicted errors

The off-target cells are where the battery earned its keep. `S06` — hand-typesetting a book
where a style defined wrongly in an early chapter silently mis-formats every later chapter —
was pre-registered `PLe` 4 and `PLs` ≤1. `PLe` came back 4/4/4. **`PLs` came back 3/3/4.**

The judges' reasoning was explicit: sonnet placed it at "the Level 3 debugging pattern",
opus at L4 because "the object that changes is the document (the environment), not merely
the solver's progress". But the corruption was *caused by the solver's own earlier action*.
`PLs`'s preamble already routes "monitoring one's own work" to `PLe` — and, for the fourth
time in this project, **a distinction stated only in the preamble did not bind.**

Two fixes, measured separately:

| | `S06` (self-caused, delayed) | `P2` (self-caused, delayed) | `P1` (world-caused) | `P3` (world changes visibly) |
|---|---|---|---|---|
| baseline | 3 / 3 / 4 | — | — | — |
| + clause bound at L3 and L4 | 3 / **0** / **0** | 3 / **0** / 2 | 3 / 3 / 4 ✓ | 4 / 4 / 4 ✓ |
| + discriminator in the L3 example | 3 / **0** / **0** | **2** / **0** / **0** | 3 / 3 / 4 ✓ | 4 / 4 / 4 ✓ |

Sonnet and opus now separate a fault the solver introduced from one the world introduced;
haiku does not, and further edits would be chasing one judge. Recorded as a judge-capability
limit rather than a rubric ambiguity, since both stronger judges follow the clause and the
`P1`/`P2` minimal pair separates cleanly for them. `T08` (debugging code the solver did not
write) held at 3/3/5 throughout, so the fix did not over-correct.

### 26.4 An open question, not a defect: any exogenously changing world scores `PLs` 4

`N05` — playing out a 40-move endgame against an opponent — came back `PLs` 4/4/4 against a
pre-registered 0–1, and all three judges reasoned correctly from the rubric: the opponent
alters the world between the solver's actions, and each change is visible when looked at,
which is L4's condition verbatim. Against `PLs` L0's static chess position this is arguably
an elegant pair: the same domain, moved only by whether the world changes.

But it means **`PLs` ≥ 4 fires on essentially any interactive task**, which risks making the
dimension read as "is this task dynamic" and re-introducing coupling with `PLe`. Not patched:
a floor excluding fully displayed change would also drop the city-traffic and control-room
anchors, and the right test is a battery that varies interactivity and hiddenness
independently. Flagged for the team as the one substantive open question in the set.

### 26.5 A note on pre-registration quality

18 of the 96 cells fell outside their pre-registered set, and nearly all were **off-target
dimensions where the pre-registration was a guess rather than a derivation** — e.g. `PLe` for
"design the plan for replicating a paper", pre-registered 3–4 and scored 0/3/0 because
designing is deliberation, which the rubric assigns to `PLp`. The judges were right and the
pre-registration was wrong. Recorded because the honest denominator for "did the rubrics
hold" is the target dimension (23/24), not the full cross-product (65/96).

## Round 27: the seven predicted overlaps are co-occurrence, not construct confound

The pre-PR audit (`docs/pre-pr-audit.md`) found that routing had only ever been tested
against 5 of the 18 v1 dimensions, and predicted nine overlaps — two of them high severity.
Its recommendation was to add a routing clause to each. This round measured them first,
because a clause written without measurement is exactly what this project has repeatedly
found does not bind.

### 27.1 Design: dissociation, not correlation

Correlation on a natural battery cannot tell overlap from co-occurrence: hard tasks are hard
in several ways at once. So the battery is built to **vary the two constructs
independently**. For each pair, three items:

- **A** — designed high on ours, low on theirs
- **B** — designed low on ours, high on theirs
- **C** — the exact collision the audit named

Plus five sentinels. 20 items, 7 dimensions, 160 decisions
(`overlap_dissociation_labels.csv`). Our dimensions scored by sonnet and opus; the v1
dimensions by opus. The measure is the **crossover**: `(A_ours − A_theirs) − (B_ours −
B_theirs)`. If the constructs are one quantity wearing two names, the crossover is ~0.

### 27.2 Result: every pair separates

| pair | audit severity | A (ours/theirs) | B (ours/theirs) | C (collision) | crossover | ρ over all 20 |
|---|---|---|---|---|---|---|
| `PLp` × `MCr` | **high** | 3.0 / 0.0 | 1.0 / 3.0 | 4.0 / 4.0 | **5.0** | 0.63 |
| `PLs` × `MCu` | **high** | 4.0 / 2.0 | 0.0 / 3.0 | 3.0 / 4.0 | **5.0** | **0.07** |
| `PLp` × `AT` | medium | 3.0 / 2.0 | 1.0 / 3.0 | 5.0 / 4.0 | 3.0 | 0.49 |
| `PLp` × `CL` | medium | 2.5 / 0.0 | 1.0 / 2.0 | 4.0 / 4.0 | 3.5 | 0.67 |
| `PLp` × `QLl` | medium | 2.5 / 2.0 | 1.0 / 4.0 | 1.5 / 4.0 | 3.5 | 0.85 |

**No routing clauses are needed.** The audit's central recommendation is not supported. Each
pair has tasks that load heavily on one dimension and not at all on the other, which is what
separability means; the C items load on both because those tasks genuinely make both demands,
which is co-occurrence and is supposed to happen.

The two the audit rated **high** are the two with the largest crossover, and `PLs` × `MCu` —
called high severity — measures **ρ = 0.07**, essentially independent across the battery.

### 27.3 The pair that deserved attention was ranked lowest

`PLp` × `QLl`, rated medium, has the highest correlation at ρ = 0.85. But the crossover is
3.5 and the direction is informative: item B5 (deduce a seating arrangement, standard method
given) scores `PLp` 1 / `QLl` 4, and even the collision item C5 (schedule seven albums under
five ordering constraints) scores `PLp` 1.5 / `QLl` 4.0. **`QLl` fires where `PLp` does not.**
The high ρ comes from `QLl` scoring ≥1 on 17 of 20 items, not from `PLp` leaking into it.

### 27.4 A v1 property worth recording: loose floors

Zeros across the 20 items: `PLs` 14, `CL` 8, `MCr` 5, `QLl` 3, `PLp` 2, `MCu` 2, `AT` 2.

Four of the five v1 dimensions tested score ≥1 on almost everything on this battery. A
dimension with a loose floor correlates with anything that tracks overall difficulty, which
inflates every ρ it appears in — so correlations *between* v1 dimensions and anything else
should be read with that in mind. Stated neutrally: it is a property of the v1 scales on this
battery, this work proposes no change to them, and `PLs`'s tight floor (14/20 zeros) is
evidence the v2 gates are doing their job rather than evidence against v1.

### 27.5 What the audit was actually worth

Combined with §25's finding that four of five of its example-level claims were false against
data already held, the pre-PR audit's value lay entirely in its **checkable facts** — that
`MSm` does not exist, and that `PLe` L5 conjoins irreversibility with sparse feedback — and
not in its severity judgments, which measurement inverted. Worth remembering the next time a
confident structural read arrives without numbers attached.
