### Cost vs precision (reference subset: 150 tasks × PL, 40 tau2 tasks × MS)

| arm | judge | $/label (harness) | s/call | $/label (API, batch) | coverage | PLp exact | PLe exact | PLs exact | MSm exact | MSc exact | ρ swe-bench-verified | ρ programbench | ρ tau2 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| R' | Opus 5.5 low, reasoning | 0.0409 | 11.0 | 0.0101 | 1.000 | 0.89 | 0.93 | 0.93 | 0.78 | 0.97 | — | — | — |
| NR | Opus 5.5 low, bare digit | 0.0320 | 7.2 | 0.0087 | 0.999 | 0.83 | 0.94 | 0.93 | 0.75 | 0.97 | -0.56 | -0.55 | -0.34 |
| SNR | Sonnet 5.5 low, bare digit | 0.0167 | 4.5 | 0.0044 | 0.999 | 0.81 | 0.86 | 0.81 | 0.40 | 0.93 | -0.52 | -0.39 | -0.23 |
| SR | Sonnet 5.5 low, reasoning | 0.0201 | 6.8 | 0.0057 | 0.999 | 0.75 | 0.83 | 0.81 | 0.38 | 0.93 | -0.42 | -0.27 | -0.26 |
| released | Opus 5.5 low, reasoning (relabel-v2/v3) | — | — | — | — | (target) | (target) | (target) | (target) | (target) | -0.55 | -0.49 | -0.28 |

### All cells: agreement with the released labels (exact / mean shift)

| rubric | n (NR) | NR | SNR | SR | SNR vs NR | SR vs SNR |
|---|---|---|---|---|---|---|
| PLp | 1410 | 0.88 / -0.04 | 0.84 / 0.07 | 0.81 / -0.06 | 0.79 / 0.11 | 0.83 / -0.13 |
| PLe | 1411 | 0.92 / -0.02 | 0.84 / 0.04 | 0.85 / -0.01 | 0.83 / 0.06 | 0.92 / -0.05 |
| PLs | 1410 | 0.90 / -0.00 | 0.75 / -0.21 | 0.74 / -0.21 | 0.76 / -0.21 | 0.82 / 0.01 |
| MSm | 1412 | 0.92 / -0.04 | 0.80 / -0.18 | 0.84 / -0.15 | 0.84 / -0.14 | 0.88 / 0.03 |
| MSc | 1411 | 0.98 / -0.00 | 0.97 / -0.00 | 0.95 / -0.02 | 0.97 / 0.00 | 0.97 / -0.02 |

### Criterion validity: Spearman ρ of level with outcome (all tasks)

| cell | n | released | NR | SNR | SR | SNR − released (95% CI) | SR − released (95% CI) |
|---|---|---|---|---|---|---|---|
| swe-bench-verified/PLp | 443 | -0.55 | -0.56 | -0.52 | -0.42 | [-0.03, 0.08] | [0.06, 0.19] |
| programbench/PLp | 129 | -0.49 | -0.55 | -0.39 | -0.27 | [-0.04, 0.25] | [0.04, 0.41] |
| tau2/PLp | 242 | -0.28 | -0.34 | -0.23 | -0.26 | [-0.05, 0.14] | [-0.08, 0.12] |

### Decision rules (amendments 4 and 4b)

- **SNR**: mixed before cost. Agreement gaps against the yardstick (points): PLp -8, PLe -7, PLs -12. Signal cells close: 2; weaker by 0.10: 1. Coverage 0.999.
- **SR**: not usable before cost. Agreement gaps against the yardstick (points): PLp -14, PLe -10, PLs -12. Signal cells close: 1; weaker by 0.10: 2. Coverage 0.999.
