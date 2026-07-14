"""The stage-gate engine — the backbone of SellerCompass.

The engine is a state machine: each stage runs on collected data and produces a
``GateResult``. A failed gate blocks progression (the caller routes the user to
pivot). Stage *logic* lands incrementally; this module fixes the contract so
every gate is forced to cite the data behind its verdict.

See METHODOLOGY.md for the definition of each stage and its gate.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class Stage(str, Enum):
    DISCOVER = "discover"
    VALIDATE_DEMAND = "validate_demand"
    COMPETITION = "competition"
    UNIT_ECONOMICS = "unit_economics"
    DECIDE = "decide"


ORDER: list[Stage] = [
    Stage.DISCOVER,
    Stage.VALIDATE_DEMAND,
    Stage.COMPETITION,
    Stage.UNIT_ECONOMICS,
    Stage.DECIDE,
]


@dataclass
class GateResult:
    stage: Stage
    passed: bool
    score: float | None = None
    reasons: list[str] = field(default_factory=list)
    evidence: dict = field(default_factory=dict)  # every verdict must cite its data

    def next_stage(self) -> Stage | None:
        """The stage to run next, or ``None`` if blocked (failed) or finished."""
        if not self.passed:
            return None
        i = ORDER.index(self.stage)
        return ORDER[i + 1] if i + 1 < len(ORDER) else None
