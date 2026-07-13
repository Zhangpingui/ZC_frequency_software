from types import SimpleNamespace

from core.models import Device, Link
from visualization.conflict_pairs import build_conflict_pair_figure
from visualization.topology import build_topology_figure


def make_links():
    first = Link("L1", Device("D1", 10, 20), Device("D2", 30, 40), 2)
    second = Link("L2", first.receiver, Device("D3", 120, 50), 6)
    return first, second


def record(left, right, conflict_type=None):
    return SimpleNamespace(
        left=left,
        right=right,
        conflict_type=conflict_type,
        distance_km=10.0,
    )


def test_topology_contains_links_and_unique_devices():
    figure = build_topology_figure(make_links())
    assert len(figure.data) >= 2
    device_trace = next(trace for trace in figure.data if trace.name == "设备")
    assert len(device_trace.x) == 3
    assert figure.layout.xaxis.scaleanchor == "y"
    assert figure.layout.xaxis.range[1] >= 120


def test_conflict_pairs_draw_one_red_connector_per_conflict():
    left, right = make_links()
    records = [record(left, right, "同频冲突"), record(right, left)]
    figure = build_conflict_pair_figure(records)
    red_lines = [
        trace for trace in figure.data
        if getattr(getattr(trace, "line", None), "color", None) == "#ff3344"
    ]
    assert len(red_lines) == 1


def test_non_conflict_pair_has_no_connector():
    left, right = make_links()
    figure = build_conflict_pair_figure([record(left, right)])
    assert not [trace for trace in figure.data if getattr(trace, "mode", None) == "lines"]


def test_conflict_pairs_pagination_and_filtering():
    left, right = make_links()
    records = [record(left, right, "冲突") if index % 2 else record(left, right) for index in range(5)]
    page = build_conflict_pair_figure(records, page=2, page_size=2)
    assert page.layout.meta["total_pages"] == 3
    assert page.layout.meta["visible_records"] == 2
    filtered = build_conflict_pair_figure(records, only_conflicts=True)
    assert filtered.layout.meta["total_records"] == 2


def test_conflict_pairs_empty_state():
    figure = build_conflict_pair_figure([])
    assert figure.layout.annotations[0].text == "暂无数据"
