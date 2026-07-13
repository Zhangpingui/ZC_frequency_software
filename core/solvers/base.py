from dataclasses import dataclass
from typing import Protocol, Sequence

from core.metrics import AssignmentMetrics
from core.models import Link


@dataclass(frozen=True)
class SolverResult:
    algorithm_name: str
    links: list[Link]
    before_metrics: AssignmentMetrics
    after_metrics: AssignmentMetrics
    elapsed_seconds: float
    is_demo: bool


class Solver(Protocol):
    algorithm_name: str

    def solve(
        self,
        links: Sequence[Link],
        distance_threshold_km: float = 10.0,
        guard_band_mhz: float = 20.0,
    ) -> SolverResult: ...
