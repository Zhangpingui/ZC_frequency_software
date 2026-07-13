from dataclasses import dataclass
from enum import Enum
from itertools import combinations
from math import hypot
from typing import Iterable, Iterator

from core.models import Link


class ConflictType(Enum):
    NONE = "无冲突"
    COCHANNEL = "同频冲突"
    ADJACENT = "邻频冲突"


@dataclass(frozen=True)
class ConflictRecord:
    left: Link
    right: Link
    conflict_type: ConflictType
    distance_km: float

    @property
    def is_conflict(self) -> bool:
        return self.conflict_type is not ConflictType.NONE


def enumerate_link_pairs(links: Iterable[Link]) -> Iterator[tuple[Link, Link]]:
    return combinations(links, 2)


def _distance(left, right) -> float:
    return hypot(left.x_km - right.x_km, left.y_km - right.y_km)


def cross_link_distance_km(left: Link, right: Link) -> float:
    return min(
        _distance(left.transmitter, right.receiver),
        _distance(right.transmitter, left.receiver),
    )


def detect_conflict(
    left: Link,
    right: Link,
    distance_threshold_km: float = 10.0,
    guard_band_mhz: float = 20.0,
) -> ConflictRecord:
    distance_km = cross_link_distance_km(left, right)
    conflict_type = ConflictType.NONE
    if distance_km <= distance_threshold_km:
        left_low, left_high = left.frequency_interval_ghz
        right_low, right_high = right.frequency_interval_ghz
        if max(left_low, right_low) <= min(left_high, right_high):
            conflict_type = ConflictType.COCHANNEL
        else:
            gap_ghz = max(left_low, right_low) - min(left_high, right_high)
            if gap_ghz * 1000 < guard_band_mhz:
                conflict_type = ConflictType.ADJACENT
    return ConflictRecord(left, right, conflict_type, distance_km)


def analyze_conflicts(
    links: Iterable[Link],
    distance_threshold_km: float = 10.0,
    guard_band_mhz: float = 20.0,
) -> list[ConflictRecord]:
    return [
        detect_conflict(left, right, distance_threshold_km, guard_band_mhz)
        for left, right in enumerate_link_pairs(links)
    ]
