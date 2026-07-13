from core.conflicts import (
    ConflictType,
    analyze_conflicts,
    cross_link_distance_km,
    detect_conflict,
    enumerate_link_pairs,
)


def test_enumerate_link_pairs_returns_each_pair_once(link_factory):
    links = [link_factory(str(index), 1.0) for index in range(4)]
    pairs = list(enumerate_link_pairs(links))
    assert len(pairs) == 6
    assert {frozenset((left.link_id, right.link_id)) for left, right in pairs} == {
        frozenset((str(left), str(right))) for left in range(4) for right in range(left + 1, 4)
    }


def test_cross_link_distance_uses_shorter_cross_path(link_factory):
    left = link_factory("a", 1.0, tx=(0, 0), rx=(100, 0))
    right = link_factory("b", 1.0, tx=(101, 0), rx=(3, 4))
    assert cross_link_distance_km(left, right) == 1.0


def test_detects_cochannel_overlap(link_factory):
    left = link_factory("a", 2.0)
    right = link_factory("b", 2.01)
    assert detect_conflict(left, right, distance_threshold_km=10).conflict_type is ConflictType.COCHANNEL


def test_detects_adjacent_gap_inside_guard_band(link_factory):
    left = link_factory("a", 2.0)
    right = link_factory("b", 2.04)
    assert detect_conflict(left, right, 10, guard_band_mhz=25).conflict_type is ConflictType.ADJACENT


def test_distance_over_threshold_suppresses_frequency_conflict(link_factory):
    left = link_factory("a", 2.0, tx=(0, 0), rx=(0, 0))
    right = link_factory("b", 2.0, tx=(20, 0), rx=(20, 0))
    record = detect_conflict(left, right, distance_threshold_km=10)
    assert record.conflict_type is ConflictType.NONE
    assert not record.is_conflict
    assert len(analyze_conflicts([left, right], 10)) == 1
