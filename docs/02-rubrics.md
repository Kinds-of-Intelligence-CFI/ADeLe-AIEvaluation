# 02 — Rubrics: the active v2 agentic set

## Two rubric generations

- **v1** (`src/adele/rubrics/data_v1/`) — the established, published set. **Frozen
  and untouched** by the agentic work.
- **v2 agentic** (`src/adele/rubrics/data_v2/`) — for tasks where a system acts
  over time. Two authoring streams: `Paolo_Pablo/` (planning, execution,
  simulation, social) and `Marko/` (the memory triad).

Which rubrics are **active** is defined by `_ACTIVE` in `adele/agentic/__init__.py`;
`MANIFEST.tsv` is generated from it and records, per dimension, the source document,
the heading, a version date and a sha256 of the file. `verify_manifest()` and a test
flag drift. Regenerate after editing a rubric:

```bash
python -c "from adele.agentic import build_manifest; build_manifest()"
```

## The active set

| code | dimension | source |
|---|---|---|
| `PLp` | Planning | Paolo_Pablo |
| `PLe` | Action control and execution | Paolo_Pablo |
| `PLs` | Simulating | Paolo_Pablo |
| `MSm` | Mind Modelling and Social Cognition | Paolo_Pablo |
| `MSc` | Communication and social interaction | Paolo_Pablo |
| `MMe` | Episodic memory | Marko |
| `MMp` | Long-term procedural memory | Marko |
| `MMs` | Working and short-term memory | Marko |

Present in the tree but deliberately **deferred**: the four sensory/motor rubrics
`SNp SNk SPa SPv`. Text and tool-based tasks do not exercise vision, audio or
dexterity, so annotating them would buy all-zero columns at full cost.

**A warning about `PLs`.** The code has carried two different dimensions. It was
first *Situational and Environmental Understanding*, re-filed there from `MSc`'s
family; that was withdrawn on 2026-08-16 and the file deleted. `PLs` was then
re-introduced on 2026-08-24 as *Simulating*, at Jose's suggestion. Only the second
is live. Anything in git history or a lab record before 2026-08-24 that mentions
`PLs` means the first one.

**Rubric files carry no version marker.** They used to open with a `#!` comment
line holding a per-dimension revision (`v2-r43`, `v2-r45`, `v2-draft`). Those were
internal to the rubric-QA rounds and have been removed. A rubric's generation now
comes from the directory it lives in — `data_v1` or `data_v2` — which is where that
fact actually lives, so the v1-vs-v2 guard and the version recorded in run metadata
work with no in-file marker. The `#!` line was never sent to a judge in any case;
the loader stripped it before building the prompt.

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

- **No frozen tag yet.** Both experiment arms must annotate against the same
  rubric text for their numbers to be comparable. The intent is a `rubric-v2.0`
  tag, with each annotation run recording the tag plus the sha256 of the rubric
  text it actually read. Not yet cut. Cut it before any production annotation
  spend — removing the `#!` lines changed every rubric's sha256, so a tag cut
  earlier would already be stale.
- **Memory taxonomy.** The Marko source has more memory types than our three-way
  split — Semantic and Prospective — with no codes assigned. Undecided.
