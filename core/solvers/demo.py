from dataclasses import replace
from typing import Sequence

from core.models import Link
from core.solvers.base import SolverResult
from core.solvers.greedy import GreedySolver


class DemoSolver:
    def __init__(self, algorithm_name: str):
        self.algorithm_name = algorithm_name

    def solve(
        self,
        links: Sequence[Link],
        distance_threshold_km: float = 10.0,
        guard_band_mhz: float = 20.0,
    ) -> SolverResult:
        result = GreedySolver().solve(links, distance_threshold_km, guard_band_mhz)
        return replace(result, algorithm_name=self.algorithm_name, is_demo=True)
