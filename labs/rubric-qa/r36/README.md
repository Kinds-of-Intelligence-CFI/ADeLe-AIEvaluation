# Round 36 — close the three fixable gaps, in one pass

Three things were outstanding after r34/r35. All three are settled here, and one of them
turned out not to need fixing at all.

## Desideratum 3 — is each demand driven by its stated primary factor?

Only `MSc` had ever been tested this way (r30's C-set). Six minimal pairs, each holding
everything fixed and moving one thing:

```
  PLp   search size up,  A1 -> A2      1 -> 3   rises      OK
  PLp   VOLUME up 40x,   A1 -> A3      1 -> 1   flat       OK
  PLe   feedback removed, B1 -> B2     1 -> 4   rises      OK
  PLe   VOLUME up 10x,   B1 -> B3      1 -> 1   flat       OK
  PLs   hidden+changing, C1 -> C2      1 -> 4   rises      OK
  PLs   ...while the amount of state falls from forty rooms to one
```

Six of six. Each dimension moves with its own driver and refuses to move with volume — which
is the disclaimer the taxonomy artifact asks for, measured rather than asserted. `PLs`'s pair
is the sharpest: the demand rises from 1 to 4 while the quantity of state *falls* forty-fold,
which is exactly what "how hidden it is, not how much of it there is" claims.

## Does `PLp` fire on sociality? No — it was the registration that was wrong

`PLp` scored 2 on pure-negotiation items where battery-v1 registered 0, and I had flagged
this as the same defect `PLe` had before its L2 carve-out. The discriminating pair says
otherwise:

```
  D1  one colleague, exactly one thing to offer, no search   PLp 1   MSc 4
  D2  dozens of custody splits, most unworkable              PLp 3   MSc 5
```

`PLp` tracks plan-search, not the presence of another person. **No carve-out was added.** My
registration of 0 was too strict, and this is why the rule in this lab is to measure before
editing — the "obvious" fix would have broken a dimension that was working.

## `X06` replaced

The old item's hidden state was entirely mental, which our own routing assigns to `MSm`, so
`PLs` correctly scored it 0 and it could never have been a `PLs`+`MSc` co-occurrence test.
`X06R` — restore power after a storm, where which lines are live is unknown and shifting,
while three depot managers each demand their area first — scores **`PLs` 5, `MSc` 5**. It is
now in the standing battery; `X06` is retired.

## Regression

```
  separation      10/12 -> 11/12 at gap 3+
  co-occurrence   6/6 with X06R in place of X06
  anchors         clean
```

The one remaining partial is `MSc`>>`PLp` at a consistent gap of 2 — and the D1/D2 pair above
explains it: multi-party negotiation genuinely carries plan-search, so `PLp` 2 is right and
the registered 0 was not.

## What did NOT work, recorded as such

The `PLs` carve-out **did not bind for haiku.** The diagnosis was sound — 8 of 12 disputed
items were haiku scoring 3-5 on social items where sonnet and opus scored 0-1 — and the
carve-out went at L3 and L5, where those items land. Judge spread went 12/36 to 13/36: no
improvement. Sonnet and opus never needed it; haiku still reads a concealed human position as
hidden world state.

This is a weak-model binding problem (desideratum 5), not a construct problem, and it is the
first carve-out in this lab that failed to take. It is left in place — it is correct, and
harmless to the two judges that already got it right — and flagged rather than iterated on.
