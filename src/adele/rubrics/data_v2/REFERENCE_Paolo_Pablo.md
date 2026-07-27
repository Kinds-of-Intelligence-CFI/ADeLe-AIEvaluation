# Reference — factor tables & notes for the "Paolo_Pablo" rubrics

> **HISTORICAL — this describes the rubrics as they were BEFORE the re-key, and no longer
> describes any shipped rubric.** `PLp`, `PLe` and `PLs` are each now keyed on a single
> driver; `MSe` became `PLs`; `ECc` was withdrawn. Do not read the tables below as current.
>
> They are kept deliberately, because they are the **exhibit for why the re-key happened**:
> read across the `PLp`, `PLe` and `MSe` tables and the same four columns appear in all three
> — temporal horizon, agent interactions, open-endedness, environment dynamics. Three
> "abilities" sharing their difficulty factors cannot separate on any battery, which is
> exactly the collinearity the taxonomy audit diagnosed and rounds 1–29 removed. Deleting
> this file would destroy that evidence.

Reference only. The rubric `.txt` files in `Paolo_Pablo/` are the source of truth used by
the judge (one polished definition per level, ADeLe v1.0 style). This file keeps the
**difficulty-factor tables** and side notes that were dropped from those files, so
they're available without opening the source Google Doc. **Droppable** — nothing in
the codebase reads it. (`≤` shown where the source had escaped `\<=`.)

Covers the 5 non-memory dimensions **as they stood before the re-key**. The deferred
sensory/motor dimensions (`SNp/SNk/SPa/SPv`) keep their tables in the source Doc.

---

## PLp — Planning

|  | Temporal horizon | Subtask decomposition | Agent interactions | Open-endedness | Env. uncertainty & dynamics |
|---|---|---|---|---|---|
| L0 | 1 | — | — | — | — |
| L1 | ≤3 | No subtasks | No | No | No |
| L2 | ≤10 | Yes (<3, well-defined) | No | No | No |
| L3 | ≤100 | Yes (well-defined) | Yes (known goals) | No | No |
| L4 | Arbitrary | Yes | Yes (known goals) | Yes | No |
| L5+ | Arbitrary | Yes | Yes — goals unknown, coordination needed | Yes | Yes |

## PLe — Action control and execution

|  | Temporal horizon | Subtasks | Well-defined plan | Feedback loops | Open-endedness | Dynamic env |
|---|---|---|---|---|---|---|
| L0 | 1 | — | — | — | — | — |
| L1 | ≤10 | No subtasks | Yes | — | No | No |
| L2 | ≤10 | Yes (<3, well-defined) | Yes | Yes | No | No |
| L3 | ≤100 | Yes (well-defined) | No | Sparse | No | No |
| L4 | Arbitrary | Yes | No | Very sparse | Yes | No |
| L5+ | Arbitrary | Yes | No | Very sparse & ambiguous | Yes | Yes |

## MSe — Environmental and situational understanding

|  | Open-endedness | Agents present | Complex env. dynamics | Dynamic & unpredictable env |
|---|---|---|---|---|
| L0 | — (no environment) | — | — | — |
| L1 | No | No | No | No |
| L2 | Yes | No | No | No |
| L3 | Yes | Yes | No | No |
| L4 | Yes | Yes | Yes | No |
| L5+ | Yes | Yes — goals unknown, coordination needed | Yes | Yes |

Notes:
- Classical situational-awareness research emphasises three stages: perception of
  relevant elements, comprehension of their significance, and projection of future states.
- Agentic-evaluation research defines environmental tasks as those that require
  interaction with an external environment, are under-specified, involve multiple
  steps, and can be quantitatively scored by an external party.

## MSc — Communication and social interaction

|  | Lack of shared knowledge / cultural context | Complexity of social dynamics | Strong emotional context | Stakes | Difficulty of intervention |
|---|---|---|---|---|---|
| L0 | — | — | — | — | — |
| L1 | No | Basic | No | Low | Low |
| L2 | Yes | Basic | No | Low | Low |
| L3 | Yes | Complex | Yes | Low | Low |
| L4 | Yes | Complex | Yes | High | Low |
| L5+ | Yes | Complex | Yes | High | High |

Does not include:
- Understanding other agents' emotions (covered by mind modelling).
- Understanding cultural environments (covered by environmental & situational understanding).
- The distinction is that this dimension is **active** (requires communication), not passive.

## ECc — Behavioral inhibition and self-control

|  | Strength of the trigger | Immediacy of competing propensity | Social influence & peer presence | Effort required & cognitive load | Emotional state & stress |
|---|---|---|---|---|---|
| L0 | — | — | — | — | — |
| L1 | Weak | Far | No | Low | Good |
| L2 | Weak | Immediate | No | Low | Good |
| L3 | Strong | Immediate | No | Intermediate | Fair |
| L4 | Strong | Immediate | No | High | Possibly bad |
| L5+ | Strong | Immediate | Yes | High | Possibly bad |

Does not include: pure cognitive difficulty without conflict (hard puzzles, complex
calculations); ethical/moral reasoning where there is no immediate impulse to resist.
Open methodological question: this dimension straddles capability vs **propensity**
(several examples are dispositional) — see `AGENTIC_METHODOLOGY.md` §5 and `todo.md`.
