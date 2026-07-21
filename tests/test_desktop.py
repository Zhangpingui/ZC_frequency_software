from core.demand_workbook import example_demand_dataset
from desktop.state import DesktopState


def test_desktop_state_uses_shared_demo_result():
    state = DesktopState()
    state.load_dataset(example_demand_dataset(), "系统模拟数据")
    result = state.optimize("DQN-GNN")

    assert result.before_conflict_count == 10
    assert result.after_conflict_count == 3
    assert state.source_name == "系统模拟数据"


def test_desktop_entrypoint_is_import_safe():
    import desktop_app

    assert callable(desktop_app.main)


def test_desktop_workbench_contains_the_web_result_and_comparison_structure():
    source = __import__("pathlib").Path("desktop/main_window.py").read_text(encoding="utf-8")

    for label in ("调整建议", "保持原频率", "优化前后冲突对比", "频道占用率（%）"):
        assert label in source


def test_desktop_theme_colors_the_scroll_area_and_input_controls():
    source = __import__("pathlib").Path("desktop/theme.py").read_text(encoding="utf-8")

    for selector in ("QScrollArea", "QScrollArea > QWidget > QWidget", "QAbstractSpinBox"):
        assert selector in source
    assert "#06182f" in source
