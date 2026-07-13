from dataclasses import dataclass, field

import pandas as pd

from core.conflicts import analyze_conflicts
from core.io import dataframe_to_links
from core.models import Link, ScenarioParameters
from core.solvers import get_solver
from core.solvers.base import SolverResult


@dataclass
class DesktopState:
    scenario: ScenarioParameters | None = None
    links: list[Link] = field(default_factory=list)
    optimized_links: list[Link] = field(default_factory=list)
    analysis_records: list = field(default_factory=list)
    solver_result: SolverResult | None = None
    source_frame: pd.DataFrame | None = None
    source_name: str = "未导入"
    distance_threshold: float = 10.0
    guard_band: float = 20.0

    def load_frame(self, frame: pd.DataFrame, source_name: str) -> None:
        self.source_frame = frame.copy()
        self.links = dataframe_to_links(frame)
        self.source_name = source_name
        self.optimized_links = []
        self.analysis_records = []
        self.solver_result = None

    def detect_conflicts(self, use_optimized: bool = False) -> list:
        links = self.optimized_links if use_optimized and self.optimized_links else self.links
        self.analysis_records = analyze_conflicts(links, self.distance_threshold, self.guard_band)
        return self.analysis_records

    def optimize(self, algorithm: str) -> SolverResult:
        self.solver_result = get_solver(algorithm).solve(
            self.links, self.distance_threshold, self.guard_band
        )
        self.optimized_links = self.solver_result.links
        return self.solver_result
