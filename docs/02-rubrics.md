# 02 — Rubrics: the active v2 agentic set

## Two rubric generations

- **v1** (`src/adele/rubrics/data_v1/`) — the established, published set. **Frozen
  and untouched** by the agentic work.
- **v2 agentic** (`src/adele/rubrics/data_v2/`) — for tasks where a system acts
  over time. Two authoring streams: `Paolo_Pablo/` (planning, execution,
  simulation, social) and `Marko/` (the memory triad).

`MANIFEST.tsv` is the source of truth for which rubrics are **active**. It records,
per dimension, the source document, the heading, a version date and a sha256 of
the file. `verify_manifest()` and a test flag drift. Regenerate after editing a
rubric:

```bash
python -c "from adele.agentic import build_manifest; build_manifest()"
```

## The active set

| code | dimension | source |
|---|---|---|
| `PLp` | Planning | Paolo_Pablo |
| `PLe` | Action control and execution | Paolo_Pablo |
| `MSm` | Mind Modelling and Social Cognition | Paolo_Pablo |
| `MSc` | Communication and social interaction | Paolo_Pablo |
| `MMe` | Episodic memory | Marko |
| `MMp` | Long-term procedural memory | Marko |
| `MMs` | Working and short-term memory | Marko |

Present in the tree but **not in the manifest**, so the loader cannot see them:
`PLs` (Simulating), and the four sensory/motor rubrics `SNp SNk SPa SPv`. The
sensory four are deliberately deferred — text and tool-based tasks do not exercise
vision, audio or dexterity, so annotating them would buy all-zero columns at full
cost. `PLs` is a live dimension whose manifest row has not been added yet; see
*Open items* below.

## The one-driver principle

The v2 agentic rubrics were re-keyed in mid-2026 after a specific failure. On
three-judge labels of HAL agent traces, **PLp and PLe never separated**: no task
scored high on one and low on the other, for any judge, in any label set. The two
differed by a near-constant offset of +0.9 to +1.1 with a standard deviation of
0.28 — the signature of two scales measuring one quantity with different
intercepts.

The cause was visible in the rubric text without any data. Each rubric declared
five to seven difficulty drivers, and neighbouring rubrics declared *overlapping*
ones. A task that was long, multi-agent and dynamic scored high on everything at
once: the drivers were doing the work, the dimensions were passengers.

Every rubric was rebuilt to the same rules:

1. **One driver per dimension.** Every other difficulty feature is explicitly
   *routed* in the preamble to the dimension that owns it.
2. **A verb spine.** Each level's text names where the driver stands, so a judge
   classifies rather than impressions.
3. **Categorical gates readable from the task statement** — yes/no questions, not
   magnitudes to estimate.
4. **Quantify only what a judge can count.** `PLe`'s reward ratio is manifest and
   gets numeric bands; `PLp`'s search sparsity is latent — estimating it means
   solving the task — so it gets none.

Set-level consequences: `ECc` (self-control) was removed as a propensity rather
than a task demand; `MSe` was re-keyed and re-filed into the planning family; v1's
`MS` was carried in as `MSm`.

## Where to read more

- **`agentic-rubric-redesign.md`** — the full account of the re-key, with the
  measurements behind each decision.
- **`rubric-provenance/`** — a per-dimension changelog. Start here when you want
  to know why one rubric says what it says.
- **`PL-family-close-out.md`** — what is settled for the PL family and what is not.
- **`lab-record.md`** — the 36 pre-registered QA rounds live on a separate branch;
  this file says where and what is worth reading there.

## Open items

- **`PLs` is not in `MANIFEST.tsv`.** The file is on the branch and the PL-family
  close-out treats it as one of the five, but the loader will not return it.
  Either the manifest needs regenerating or the omission is deliberate — unresolved.
- **Three tests are red on the rubric branch** (`test_manifest_has_no_drift`,
  `test_active_catalog_is_single_version`,
  `test_MSm_adds_only_the_MSc_carve_out_to_v1`). They predate this branch: the
  manifest was not regenerated after the late-August rubric edits.
- **No frozen tag yet.** Both experiment arms must annotate against the same
  rubric text for their numbers to be comparable. The intent is a `rubric-v2.0`
  tag, with each annotation run recording the tag plus the sha256 of the rubric
  text it actually read. Not yet cut.
- **Memory taxonomy.** The Marko source has more memory types than our three-way
  split — Semantic and Prospective — with no codes assigned. Undecided.
