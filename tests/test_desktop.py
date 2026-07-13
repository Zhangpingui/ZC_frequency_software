from desktop.state import DesktopState
from core.io import dataframe_to_links, example_dataframe


def test_desktop_state_loads_mock_data_and_clears_results():
    state = DesktopState()
    state.optimized_links = [object()]
    state.load_frame(example_dataframe(), "模拟数据")
    assert len(state.links) == 15
    assert state.source_name == "模拟数据"
    assert state.optimized_links == []


def test_desktop_state_detects_and_optimizes_conflicts():
    state = DesktopState(links=dataframe_to_links(example_dataframe()))
    records = state.detect_conflicts()
    result = state.optimize("贪婪算法")
    assert sum(record.is_conflict for record in records) > 0
    assert result.after_metrics.conflict_count < result.before_metrics.conflict_count
    assert state.optimized_links == result.links


def test_desktop_entrypoint_is_import_safe():
    import desktop_app

    assert callable(desktop_app.main)
