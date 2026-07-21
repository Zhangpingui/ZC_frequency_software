from dataclasses import dataclass
from typing import Mapping

import pandas as pd


@dataclass(frozen=True)
class DemandDataset:
    frame: pd.DataFrame
    source_bytes: bytes | None
    sheet_name: str
    header_row: int


@dataclass(frozen=True)
class ProtectionRule:
    expression: str
    lower_mhz: float
    upper_mhz: float
    category: str = ""
    requirement: str = ""


@dataclass(frozen=True)
class ProtectionRuleSet:
    rules: tuple[ProtectionRule, ...]
    source_name: str
    warnings: tuple[str, ...] = ()

    @property
    def valid_count(self) -> int:
        return len(self.rules)

    @property
    def invalid_count(self) -> int:
        return len(self.warnings)


@dataclass(frozen=True)
class DemandConflictPair:
    left_row: int
    right_row: int
    left_name: str
    right_name: str
    is_conflict: bool


@dataclass(frozen=True)
class DemandOptimizationResult:
    algorithm_name: str
    dataset: DemandDataset
    before_pairs: tuple[DemandConflictPair, ...]
    after_pairs: tuple[DemandConflictPair, ...]
    suggestions: Mapping[int, str]
    before_conflict_count: int
    after_conflict_count: int

    @property
    def source_frame(self) -> pd.DataFrame:
        return self.dataset.frame

    @property
    def reduction_pct(self) -> float:
        if not self.before_conflict_count:
            return 0.0
        return round(
            (self.before_conflict_count - self.after_conflict_count)
            / self.before_conflict_count
            * 100,
            1,
        )
