# plp-b2 — PLp candidate B2: only choices that could go wrong add to planning demand

Owner: Pablo. The candidate adds two sentences to PLp's description and a contrasting pair of examples.
It is tested first on the rivercross grid of `rivercross-v2` amendment 2, which separates search from
length.

**Status.** B2 failed. Structural candidate S passed the rivercross test narrowly (amendment 1) and the SWE-bench sanity check (amendment 2, ρ = −0.73 against −0.55). The lab regression comes next. See `RESULTS.md`.

| | |
|---|---|
| candidate | `PLp_B2.txt` (`make_b2.py`) |
| design, predictions | `PREREGISTRATION.md` |
| runs | `labels/b2-search/` |
| analysis | `analysis/analyse.py` → `results/b2_search.json` |
| results | `RESULTS.md` |
