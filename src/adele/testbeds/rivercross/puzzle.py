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

    def legal_configuration(self, left_bank: frozenset[str]) -> bool:
        """Whether the configuration given by ``left_bank`` is legal.

        With a ferryman only the bank they are *not* on is checked (the attended
        bank is always safe); without one, both banks are checked.
        """
        right_bank = frozenset(self.items) - left_bank
        if self.ferryman is None:
            banks = (left_bank, right_bank)
        elif self.ferryman in left_bank:
            banks = (right_bank,)
        else:
            banks = (left_bank,)
        return all(self.legal_bank(bank) for bank in banks)

    def to_dict(self) -> dict:
        """JSON-serializable form, e.g. for ``Sample.metadata``."""
        return {
            "items": list(self.items),
            "boat_capacity": self.boat_capacity,
            "ferryman": self.ferryman,
            "conflicts": [sorted(pair) for pair in self.conflicts],
            "predators": sorted(self.predators),
            "prey": sorted(self.prey),
            "name": self.name,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "PuzzleSpec":
        return cls(
            items=tuple(data["items"]),
            boat_capacity=data["boat_capacity"],
            ferryman=data["ferryman"],
            conflicts=frozenset(frozenset(pair) for pair in data["conflicts"]),
            predators=frozenset(data["predators"]),
            prey=frozenset(data["prey"]),
            name=data["name"],
        )


def describe_rules(spec: PuzzleSpec) -> str:
    """The boat and constraint rules, without start/goal framing.

    Shared by the full puzzle prompt and the per-state / per-transition framings
    used by the annotation methods, so the rules read identically everywhere.
    """
    lines: list[str] = []
    if spec.ferryman:
        cap = spec.boat_capacity
        lines.append(
            f"The boat carries the {spec.ferryman} and at most {cap} "
            f"item{'s' if cap != 1 else ''} per crossing."
        )
    else:
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
    return " ".join(lines)


def render_prompt(spec: PuzzleSpec) -> str:
    """A natural-language statement of the puzzle for an agent or annotator."""
    cargo = [it for it in spec.items if it != spec.ferryman]
    if spec.ferryman:
        intro = (
            f"A {spec.ferryman} must ferry the following across a river from the "
            f"left bank to the right bank: {', '.join(cargo)}."
        )
    else:
        intro = (
            "Move the following across a river from the left bank to the right "
            f"bank: {', '.join(spec.items)}."
        )
    goal = "Find a sequence of crossings that gets everything to the right bank."
    return " ".join([intro, describe_rules(spec), goal])


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


CONFLICT_TOPOLOGIES = ("chain", "star", "cycle", "complete")


def _topology_edges(
    cargo: tuple[str, ...], topology: str
) -> tuple[tuple[str, str], ...]:
    n = len(cargo)
    if topology == "chain":
        return tuple((cargo[i], cargo[i + 1]) for i in range(n - 1))
    if topology == "star":
        return tuple((cargo[0], cargo[i]) for i in range(1, n))
    if topology == "cycle":
        if n < 3:
            return tuple((cargo[i], cargo[i + 1]) for i in range(n - 1))
        return tuple((cargo[i], cargo[(i + 1) % n]) for i in range(n))
    if topology == "complete":
        return tuple(
            (cargo[i], cargo[j]) for i in range(n) for j in range(i + 1, n)
        )
    raise ValueError(f"unknown topology {topology!r}; choose from {CONFLICT_TOPOLOGIES}")


def conflict_topology_spec(
    n_cargo: int,
    topology: str = "chain",
    boat_capacity: int = 1,
    name: str | None = None,
) -> PuzzleSpec:
    """A wolf-goat-cabbage generalization whose conflict graph has a named shape.

    ``chain`` (consecutive pairs conflict; ``n_cargo == 3, boat_capacity == 1``
    reproduces wolf-goat-cabbage), ``star`` (one item conflicts with all others),
    ``cycle``, or ``complete`` (every pair conflicts). Different shapes stress
    different difficulty regimes at the same item count.
    """
    cargo = tuple(f"item{i + 1}" for i in range(n_cargo))
    return conflict_graph_puzzle(
        cargo=cargo,
        conflicts=_topology_edges(cargo, topology),
        boat_capacity=boat_capacity,
        name=name or f"{topology}-{n_cargo}-boat-{boat_capacity}",
    )


def linear_conflict_spec(
    n_cargo: int, boat_capacity: int = 1, name: str | None = None
) -> PuzzleSpec:
    """The ``chain`` topology (alias). ``n_cargo == 3, boat_capacity == 1``
    reproduces wolf-goat-cabbage (optimal length 7)."""
    return conflict_topology_spec(n_cargo, "chain", boat_capacity, name=name)
