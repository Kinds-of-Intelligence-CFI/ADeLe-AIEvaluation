# tau2-clean — pre-registration

Committed and pushed before any label of run `tau2-clean-new-pl`.

**Question.** Do the PL results on tau2 hold on a clean task set, with banking solve rates from one grading version?

## The clean set (Pablo's rule, 2026-10-01; `make_set.py` → `tasks.csv`)

tau2 airline, retail and banking_knowledge tasks with results on the frozen text, minus the tasks no configuration has
solved. Telecom is excluded: all its tasks share 5 texts, so the judge cannot tell them apart. **Banking:** tau2 v1.0.1
(2026-07-15) changed its grading, so only post-change runs count, for the keep rule and for solve rates (10 of 29
configurations). 242 tasks remain: airline 49, retail 114, banking 79. 232 have PL labels (`plp-o-relabel`,
`pl-relabel-v2`); 10 banking tasks are labelled here (`mass-annotation/specs/tau2-clean-new-pl.toml`, 30 calls, Opus low,
v2 prompt, PLp text O). The runner's prompts were checked byte-identical to the earlier runs on all 696 labelled cells.

## Analysis (`analysis/analyse.py`)

`tau2-tb4-pl`'s within-domain combined test for PLp, PLe, PLs against solve rate (common configurations), per domain,
and against the all-configurations rate. Banking: the same test with post-change and with the old mixed-grading rates.

## Predictions (sealed)

- PLp within-domain combined ρ negative with p < 0.05 on the 242: 0.9. Within ±0.10 of −0.35 (the 232-task value): 0.75.
- Banking PLp: more negative with post-change rates than with mixed rates: 0.5.
- PLe and PLs within domain: negative with p < 0.05: 0.5 each.

Caveat: the 232 labelled tasks and their outcomes were analysed before (`tau2-tb4-pl`, `plp-o-relabel`); only the 10 new
labels and the banking re-grading are new.
