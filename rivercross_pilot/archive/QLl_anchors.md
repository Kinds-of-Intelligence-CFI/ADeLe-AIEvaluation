# QLl (Logical Reasoning) — river-crossing calibration anchors

Rate the **deductive/inferential reasoning** needed to find valid moves and finish
the puzzle FROM the current state.

**Governing rule (resolves most borderline cases):** the level reflects the
reasoning the *current state actually requires* — **not** the number of conflict
rules printed. Constraints that cannot bind right now (boat capacity is ample, or
few items remain) do **not** raise the level.

## Operational boundaries for this task family

- **Level 1 — trivial / forced.** The finish is essentially forced: the boat can
  carry all remaining items at once, or only one obviously-safe move exists.
  Single-step, no real deduction.
  - *Anchor:* Left = farmer,item1,item2,item3; boat capacity 4; boat on left.
    → **1.** All remaining items cross in one trip; the listed conflict rules
    never bind. (Do **not** rate 2+ just because rules are written down.)

- **Level 2 — simple, no lookahead.** A few constraints genuinely bind; the safe
  progressing move is found by directly checking which immediate combinations are
  allowed. No need to foresee future states.
  - *Anchor:* Left = farmer,item1,item2,item3; Right = item4; capacity 2; item1
    conflicts with all others. → **2.** You must choose a safe pair to send, but
    each step is decided by checking conflicts now — no trap to anticipate.

- **Level 3 — moderate, requires lookahead.** Constraints interact so the
  locally-obvious move can be a trap; finishing requires looking one+ moves ahead,
  or realizing a non-obvious item must move first or be ferried **back**.
  - *Anchor:* wolf-goat-cabbage mid-puzzle, capacity 1 — you must realize the
    just-delivered item has to be brought BACK to avoid a forbidden pair.
    → **3.** Non-obvious lookahead / backtracking.

## Borderline tie-break
Ask, in order:
1. Is the finish essentially forced (capacity ample / one obvious move)? → **1**
2. Else, is each move decided by just checking current legality? → **2**
3. Else, must you foresee a trap or a bring-back? → **3** (4–5 only for
   argument/proof-level reasoning, which these puzzles do not reach).
