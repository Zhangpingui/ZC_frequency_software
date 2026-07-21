from pathlib import Path


def test_app_renders_the_single_workbench_without_page_routing():
    source = Path("app.py").read_text(encoding="utf-8")

    assert "render_workbench" in source
    assert "render_bottom_navigation" not in source
    assert "from pages import" not in source


def test_workbench_contains_data_algorithm_result_and_comparison_controls():
    source = Path("ui/workbench.py").read_text(encoding="utf-8")

    for label in (
        "导入用频需求表",
        "生成模拟数据",
        "启动频率优化",
        "下载结果 Excel",
        "优化前后冲突对比",
    ):
        assert label in source
