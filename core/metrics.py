from dataclasses import dataclass
from typing import Iterable

from core.conflicts import analyze_conflicts
from core.models import Link


@dataclass(frozen=True)
class AssignmentMetrics:
    conflict_count: int
    unique_frequency_count: int
    channel_occupancy_pct: float
    span_ghz: float
    span_ratio_pct: float


def calculate_metrics(
    links: Iterable[Link],
    distance_threshold_km: float = 10.0,
    guard_band_mhz: float = 20.0,
    frequency_precision: int = 9,
) -> AssignmentMetrics:
    link_list = list(links)
    frequencies = {round(link.frequency_ghz, frequency_precision) for link in link_list}
    span_ghz = max(frequencies) - min(frequencies) if frequencies else 0.0
    conflict_count = sum(
        record.is_conflict
        for record in analyze_conflicts(link_list, distance_threshold_km, guard_band_mhz)
    )
    return AssignmentMetrics(
        conflict_count=conflict_count,
        unique_frequency_count=len(frequencies),
        channel_occupancy_pct=len(frequencies) / 81 * 100,
        span_ghz=span_ghz,
        span_ratio_pct=span_ghz / 8 * 100,
    )
