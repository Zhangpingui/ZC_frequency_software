import streamlit as st

st.set_page_config(
    page_title="战场频谱智能指配演示系统",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded",
)

from pages import analysis, parameters, topology
from ui import initialize_state, render_bottom_navigation, render_header, render_sidebar
from ui.shell import load_theme


def main() -> None:
    initialize_state()
    load_theme()
    render_header()
    routes = {"parameters": parameters.render, "topology": topology.render, "analysis": analysis.render}
    routes.get(st.session_state.active_page, parameters.render)()
    render_sidebar()
    render_bottom_navigation()


if __name__ == "__main__":
    main()
