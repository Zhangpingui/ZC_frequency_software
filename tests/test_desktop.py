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


def test_desktop_ui_contains_web_feature_controls():
    source = __import__("pathlib").Path("desktop/main_window.py").read_text(encoding="utf-8")
    for label in ("只看冲突", "搜索链路 ID", "每页", "下载当前结果 CSV", "覆盖区域", "上一步", "下一步"):
        assert label in source
    assert "resize(1500, 920)" not in source


def test_desktop_charts_use_compact_and_collision_aware_labels():
    source = __import__("pathlib").Path("desktop/charts.py").read_text(encoding="utf-8")
    assert "_device_groups" in source
    assert "label = f\"{link.transmitter.device_id}–{link.receiver.device_id} · {link.frequency_ghz:.2f}G\"" in source


def test_desktop_supports_fullscreen_button_and_shortcuts():
    source = __import__("pathlib").Path("desktop/main_window.py").read_text(encoding="utf-8")
    assert "全屏显示" in source
    assert 'QKeySequence("F11")' in source
    assert 'QKeySequence("Escape")' in source


def test_desktop_conflict_canvas_supports_filtering_and_pagination():
    source = __import__("pathlib").Path("desktop/charts.py").read_text(encoding="utf-8")
    assert "only_conflicts" in source
    assert "page_size" in source
    assert "total_pages" in source
    assert "max(32" not in source
