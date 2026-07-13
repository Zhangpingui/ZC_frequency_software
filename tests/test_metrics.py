import pytest

from core.metrics import calculate_metrics


def test_calculate_metrics_counts_conflicts_and_rounded_frequencies(link_factory):
    links = [
        link_factory("a", 1.0000000001),
        link_factory("b", 1.0),
        link_factory("c", 9.0, tx=(100, 0), rx=(100, 0)),
    ]
    metrics = calculate_metrics(links, distance_threshold_km=10)
    assert metrics.conflict_count == 1
    assert metrics.unique_frequency_count == 2
    assert metrics.channel_occupancy_pct == pytest.approx(2 / 81 * 100)
    assert metrics.span_ghz == pytest.approx(8.0)
    assert metrics.span_ratio_pct == pytest.approx(100.0)


def test_empty_assignment_has_zero_metrics():
    assert calculate_metrics([]).span_ratio_pct == 0
