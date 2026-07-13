from dataclasses import replace
from time import perf_counter
from typing import Sequence

from core.conflicts import analyze_conflicts, detect_conflict
from core.metrics import calculate_metrics
from core.models import Link
from core.solvers.base import SolverResult


class GreedySolver:
    algorithm_name = "贪心算法"
    candidate_frequencies = tuple(round(1.0 + index * 0.1, 1) for index in range(81))

    def solve(
        self,
        links: Sequence[Link],
        distance_threshold_km: float = 10.0,
        guard_band_mhz: float = 20.0,
    ) -> SolverResult:
        started = perf_counter()
        originals = list(links)
        before = calculate_metrics(originals, distance_threshold_km, guard_band_mhz)
        degrees = {link.link_id: 0 for link in originals}
        for record in analyze_conflicts(originals, distance_threshold_km, guard_band_mhz):
            if record.is_conflict:
                degrees[record.left.link_id] += 1
                degrees[record.right.link_id] += 1
        ordered = sorted(enumerate(originals), key=lambda item: (-degrees[item[1].link_id], item[0]))
        assigned: list[Link] = []
        for _, link in ordered:
            scored = []
            for frequency in self.candidate_frequencies:
                candidate = replace(link, frequency_ghz=frequency)
                new_conflicts = sum(
                    detect_conflict(candidate, other, distance_threshold_km, guard_band_mhz).is_conflict
                    for other in assigned
                )
                scored.append((new_conflicts, abs(frequency - link.frequency_ghz), frequency, candidate))
            assigned.append(min(scored, key=lambda item: item[:3])[3])
        by_id = {link.link_id: link for link in assigned}
        optimized = [by_id[link.link_id] for link in originals]
        after = calculate_metrics(optimized, distance_threshold_km, guard_band_mhz)
        if after.conflict_count > before.conflict_count:
            optimized, after = originals, before
        return SolverResult(
            self.algorithm_name,
            optimized,
            before,
            after,
            perf_counter() - started,
            False,
        )
