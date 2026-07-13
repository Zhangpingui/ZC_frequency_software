import ast
from pathlib import Path


def test_app_configures_streamlit_before_other_calls():
    source = Path("app.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    calls = [node for node in tree.body if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call)]
    first = calls[0].value
    assert isinstance(first.func, ast.Attribute)
    assert first.func.attr == "set_page_config"


def test_all_page_renderers_are_importable():
    from pages import analysis, parameters, topology

    assert all(callable(module.render) for module in (analysis, parameters, topology))


def test_streamlit_builtin_page_navigation_is_disabled():
    config = Path(".streamlit/config.toml").read_text(encoding="utf-8")
    assert "showSidebarNavigation = false" in config


def test_topology_page_preserves_plot_title_and_reruns_after_load():
    source = Path("pages/topology.py").read_text(encoding="utf-8")
    assert "title=None" not in source
    assert "st.rerun()" in source


def test_analysis_toast_uses_valid_emoji():
    source = Path("pages/analysis.py").read_text(encoding="utf-8")
    assert 'icon="✓"' not in source


def test_sidebar_renders_after_active_page_updates_state():
    source = Path("app.py").read_text(encoding="utf-8")
    assert source.index("routes.get") < source.index("render_sidebar()")
