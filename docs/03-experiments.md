# 03 — The two experiments

Two arms, deliberately different in kind. Neither substitutes for the other.

| | `experiments/rivercross/` | `experiments/benchmarks/` |
|---|---|---|
| owner | Mingqian | Pablo |
| what it buys | **internal validity** — the instrument measures what we say it measures | **external validity** — the instrument predicts real success and failure at scale |
| ground truth | an exact BFS solver: true cost-to-go for every state | none; per-instance success flags for many models |
| scale | tens of states, fully controlled | thousands of instances, real agents |

The link between them is that both annotate through the same rubrics, the same
dimension-agnostic prompt, and the same demand-to-go framing (`01-method.md`).
For their numbers to be comparable they must run against the same frozen rubric
text — see *Open items* in `02-rubrics.md`.

---

## Arm 1 — rivercross (solver-backed testbed)

Parametrized river-crossing puzzles (conflict-graph generalizations of
wolf-goat-cabbage across chain / star / cycle / complete topologies, plus
missionaries-cannibals) with an **exact BFS solver as a value oracle**. Because
the solver knows true remaining work, a rubric's labels can be scored against
ground truth rather than only against other judges.

Library: `src/adele/testbeds/rivercross/`. Experiment record:
`experiments/rivercross/`.

### What is established

**`PLp` (planning)** — rubric re-keyed to score demand by search size: depth,
breadth, and the fraction of action-sequences that succeed. On 43 leak-free
states: annotations track the solver's remaining search depth at Spearman
0.83–0.89, QWK 0.74–0.90, within-1 = 100%. Headline: planning demand *falls* as
the task progresses, in proportion to remaining search.

**`PLe` (action control)** — calibrated against captured real agent play against a
rule-enforcing referee. The disagreement turned out to hinge on one ambiguous
word, *feedback*. Three changes fixed it: `feedback` → `reward` throughout, levels
recast as a mutually-exclusive partition on horizon × reward-density, and an
operational definition of reward. On 49 trajectory states the two strongest judges
produced identical labels (QWK 1.00); all-three agreement rose 22% → 65%.

**`MMs` (working / short-term memory)** — six protocol versions. The design is
paired: each state appears once with the current configuration shown and once with
only the move history, and the signal is the paired delta.

- v3 contrast set: holds history length fixed while varying object-location
  updates. All gates pass for the strong judges.
- v4 verbosity control: refutes the "the judge is just counting tokens"
  explanation of v3.
- v5 on the 43 **real** method-1b rollout states: all gates pass for all three
  judges; paired Wilcoxon p = 1.1e-13. `MMs` delta is uncorrelated with the `PLp`
  labels on the same states (ρ −0.03 to −0.05) while tracking update complexity
  (0.68–0.77) — it is measuring something `PLp` and `PLe` do not.
- v6 widened contrast: gates pass, with two flags — the top of the scale saturates
  at 4 for two judges, and the level-5 anchor was exercised by one judge only, so
  the 4/5 boundary is not yet calibrated.

v5 and v6 were **pre-registered before any label collection**
(`experiments/rivercross/memory/PREREGISTRATION_v5_v6.md`); the commit order is
the audit trail.

**Cross-family check** — GPT-5 replicates the demand-to-go gradient, but the
**level-0 anchor does not transfer**: on every state the Claude panel unanimously
calls 0 (near-terminal), GPT-5 assigns 1 for `PLp` and 2 for `PLe`. Fix drafted,
not yet applied: a contrastive level-0 example ("a single forced or immediately
obvious final move is 0").

### What is not done

1. **No human annotation has been collected.** Blind annotation pages are built
   (`experiments/rivercross/memory/annotation_ui/`) for the full v3 set, v5 and
   v6, with the rubric and scoring guide embedded, but zero labels exist. The
   pre-registration requires a human pass before any external claim, and a
   **second annotator** for a human–human ceiling — without one, judge–human
   agreement has no scale to be read against.
2. **No ability side.** Everything above measures annotation quality against the
   oracle. There is no success/failure data: 6 captured agent trajectories, and
   the frames carry no outcome column. Planned next: generate puzzles at
   controlled demand levels using the solver, run real agents, and test whether
   demand-to-go predicts step-level success. To be pre-registered before
   collection.
3. **`PLp`/`PLe` labels are stale.** They were produced against the pre-re-key
   rubric text and need re-running against the frozen tag. `MMs` is unaffected —
   `Marko/MMs.txt` was not changed by the re-key.

---

## Arm 2 — benchmarks (real agents at scale)

Per-instance success/failure for many models across public benchmarks, joined to
demand annotations of the same instances, then used to fit ability curves and test
extrapolation to new models.

Code: `src/adele/results/` (success matrices from SWE-bench experiments,
MathArena, ARC Prize, tau2, Inspect scores) and `src/adele/instances.py`
(instance freezing, id canonicalization, sha256 manifest, cost estimation before
any spend).

The step-by-step procedure is `docs/runbook-benchmarks.md`. In outline: fetch the
bulk per-instance flags → freeze the instances to annotate and verify they join
the flags → request partner data → **pass the rubric regression gate** → run
production annotation → fit per-dimension ability curves and validate
extrapolation on current-generation models.

### Status

The pipeline is built and the instance sets for tau2 are frozen. Production
annotation has not started; the runbook gates it behind the rubric regression
check, which is the right place to pin the frozen rubric tag.

### Open

- **Criterion validity is the top unclosed item** for the rubrics: no demand label
  has yet been joined to a solver outcome. That is what arm 1's ability experiment
  is designed to supply, with outcomes that come free from the solver.
- Ownership of the runbook's data-fetching steps is unconfirmed.
