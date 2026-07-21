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
