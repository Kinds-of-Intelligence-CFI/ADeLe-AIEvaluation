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
