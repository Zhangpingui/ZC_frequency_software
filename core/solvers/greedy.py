from dataclasses import replace
from itertools import combinations
from time import perf_counter
from typing import Sequence

from core.conflicts import analyze_conflicts, cross_link_distance_km, detect_conflict
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

        frozen_ids = self._find_frozen_pairs(originals, distance_threshold_km)

        degrees = {link.link_id: 0 for link in originals}
        for record in analyze_conflicts(originals, distance_threshold_km, guard_band_mhz):
            if record.is_conflict:
                degrees[record.left.link_id] += 1
                degrees[record.right.link_id] += 1
        ordered = sorted(enumerate(originals), key=lambda item: (-degrees[item[1].link_id], item[0]))
        assigned: list[Link] = []
        for _, link in ordered:
            if link.link_id in frozen_ids:
                assigned.append(link)
                continue
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

    def _find_frozen_pairs(
        self, links: Sequence[Link], distance_threshold_km: float
    ) -> set[str]:
        """Find the tightest same-frequency pair per frequency band to freeze."""
        close_pairs: list[tuple[str, str, float, float]] = []
        for a, b in combinations(links, 2):
            dist = cross_link_distance_km(a, b)
            if dist <= distance_threshold_km and a.frequency_ghz == b.frequency_ghz:
                close_pairs.append((a.link_id, b.link_id, dist, a.frequency_ghz))
        close_pairs.sort(key=lambda x: x[2])
        frozen = set()
        frozen_freqs = set()
        for lid_a, lid_b, _, freq in close_pairs:
            if freq in frozen_freqs:
                continue
            if lid_a in frozen or lid_b in frozen:
                continue
            frozen.add(lid_a)
            frozen.add(lid_b)
            frozen_freqs.add(freq)
        return frozen
