import pytest

from core.demand_workbook import example_demand_dataset, example_protection_rules
from desktop.state import DesktopState


def test_desktop_state_requires_both_data_sources():
    state = DesktopState()
    state.load_dataset(example_demand_dataset(), "需求.xlsx")

    assert not state.is_ready
    with pytest.raises(ValueError, match="禁用保护"):
        state.optimize()
    state.load_protection_rules(example_protection_rules(), "规则.docx")
    result = state.optimize()

    assert state.is_ready
    assert result.before_conflict_count == 10
    assert result.after_conflict_count == 3
    assert result.protection_rule_count == 3
    assert state.source_name == "需求.xlsx"


def test_desktop_entrypoint_is_import_safe():
    import desktop_app

    assert callable(desktop_app.main)


def test_desktop_workbench_contains_the_web_result_and_comparison_structure():
    source = __import__("pathlib").Path("desktop/main_window.py").read_text(encoding="utf-8")

    for label in ("调整建议", "保持原频率", "优化前后冲突对比", "导入禁用保护/规则数据"):
        assert label in source
    assert "DEMO_ALGORITHMS" not in source
    assert "算法选择" not in source
    assert "模拟" not in source


def test_desktop_theme_colors_the_scroll_area_and_input_controls():
    source = __import__("pathlib").Path("desktop/theme.py").read_text(encoding="utf-8")

    for selector in ("QScrollArea", "QScrollArea > QWidget > QWidget", "QAbstractSpinBox"):
        assert selector in source
    assert "#06182f" in source
