"""Parametrized river-crossing puzzles (generalizations of wolf-goat-cabbage).

A puzzle moves a set of items from the left bank to the right bank using a boat
of bounded capacity. Two constraint families are supported:

* conflict-graph (generalizes wolf/goat/cabbage): named pairs of items may not
  be left together on a bank the ferryman is not currently on.
* threshold (generalizes missionaries-and-cannibals): on any unattended bank,
  the number of "predator" items may not exceed the number of "prey" items
  whenever at least one prey item is present.

The state space is finite and fully enumerable, which lets ``solver.py`` compute
the exact optimal cost-to-go for every state -- the value oracle that replaces a
learned value model in the annotation methods.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class PuzzleSpec:
    """A generalized river-crossing puzzle.

    ``items`` holds every entity (including the ``ferryman`` if there is one).
    With a ferryman, every crossing must include them and the boat carries up to
    ``boat_capacity`` *other* items; legality is checked only on the bank the
    ferryman just left. Without a ferryman, a crossing carries 1..``boat_capacity``
    items and legality is checked on both banks.
    """

    items: tuple[str, ...]
    boat_capacity: int = 1
    ferryman: str | None = None
    conflicts: frozenset[frozenset[str]] = field(default_factory=frozenset)
    predators: frozenset[str] = field(default_factory=frozenset)
    prey: frozenset[str] = field(default_factory=frozenset)
    name: str = "river-crossing"

    def __post_init__(self) -> None:
        items = set(self.items)
        if len(items) != len(self.items):
            raise ValueError("items must be unique")
        if self.ferryman is not None and self.ferryman not in items:
            raise ValueError(f"ferryman {self.ferryman!r} not among items")
        for pair in self.conflicts:
            if not pair <= items:
                raise ValueError(f"conflict {set(pair)} references unknown items")
        if not (self.predators <= items and self.prey <= items):
            raise ValueError("predators/prey reference unknown items")
        if self.boat_capacity < 1:
            raise ValueError("boat_capacity must be >= 1")

    def legal_bank(self, bank: frozenset[str]) -> bool:
        """Whether an unattended bank holding ``bank`` violates no constraint."""
        for pair in self.conflicts:
            if pair <= bank:
                return False
        if self.prey:
            preys = len(self.prey & bank)
            preds = len(self.predators & bank)
            if preys and preds > preys:
                return False
        return True


def render_prompt(spec: PuzzleSpec) -> str:
    """A natural-language statement of the puzzle for an agent or annotator."""
    cargo = [it for it in spec.items if it != spec.ferryman]
    lines: list[str] = []
    if spec.ferryman:
        cap = spec.boat_capacity
        lines.append(
            f"A {spec.ferryman} must ferry the following across a river from the "
            f"left bank to the right bank: {', '.join(cargo)}."
        )
        lines.append(
            f"The boat carries the {spec.ferryman} and at most {cap} "
            f"item{'s' if cap != 1 else ''} per crossing."
        )
    else:
        lines.append(
            "Move the following across a river from the left bank to the right "
            f"bank: {', '.join(spec.items)}."
        )
        lines.append(
            f"The boat holds at most {spec.boat_capacity} and needs at least one "
            "aboard to row."
        )
    who = f"without the {spec.ferryman}" if spec.ferryman else "on an unattended bank"
    for pair in sorted(sorted(p) for p in spec.conflicts):
        a, b = pair
        lines.append(f"The {a} and the {b} must not be left together {who}.")
    if spec.prey:
        lines.append(
            f"On an unattended bank, the {'/'.join(sorted(spec.predators))} must "
            f"never outnumber the {'/'.join(sorted(spec.prey))} when any of the "
            "latter are present."
        )
    lines.append("Find a sequence of crossings that gets everything to the right bank.")
    return " ".join(lines)


def wolf_goat_cabbage() -> PuzzleSpec:
    """The classic puzzle (optimal solution: 7 crossings)."""
    return PuzzleSpec(
        items=("farmer", "wolf", "goat", "cabbage"),
        boat_capacity=1,
        ferryman="farmer",
        conflicts=frozenset(
            {frozenset({"wolf", "goat"}), frozenset({"goat", "cabbage"})}
        ),
        name="wolf-goat-cabbage",
    )


def missionaries_cannibals(n: int = 3, boat_capacity: int = 2) -> PuzzleSpec:
    """Missionaries and cannibals ((3, 3) with boat 2 is optimal at 11 crossings)."""
    missionaries = tuple(f"M{i + 1}" for i in range(n))
    cannibals = tuple(f"C{i + 1}" for i in range(n))
    return PuzzleSpec(
        items=missionaries + cannibals,
        boat_capacity=boat_capacity,
        ferryman=None,
        predators=frozenset(cannibals),
        prey=frozenset(missionaries),
        name=f"missionaries-cannibals-{n}",
    )


def conflict_graph_puzzle(
    cargo: tuple[str, ...],
    conflicts: tuple[tuple[str, str], ...],
    boat_capacity: int = 1,
    ferryman: str = "farmer",
    name: str = "conflict-graph",
) -> PuzzleSpec:
    """A wolf-goat-cabbage generalization: arbitrary cargo and conflict pairs."""
    items = (ferryman, *cargo) if ferryman not in cargo else tuple(cargo)
    return PuzzleSpec(
        items=items,
        boat_capacity=boat_capacity,
        ferryman=ferryman,
        conflicts=frozenset(frozenset(pair) for pair in conflicts),
        name=name,
    )


def linear_conflict_spec(
    n_cargo: int, boat_capacity: int = 1, name: str | None = None
) -> PuzzleSpec:
    """Wolf-goat-cabbage generalized to a chain of ``n_cargo`` items in which each
    consecutive pair conflicts. ``n_cargo == 3, boat_capacity == 1`` reproduces
    the structure of wolf-goat-cabbage (optimal length 7)."""
    cargo = tuple(f"item{i + 1}" for i in range(n_cargo))
    conflicts = tuple((cargo[i], cargo[i + 1]) for i in range(n_cargo - 1))
    return conflict_graph_puzzle(
        cargo=cargo,
        conflicts=conflicts,
        boat_capacity=boat_capacity,
        name=name or f"chain-{n_cargo}-boat-{boat_capacity}",
    )
