import streamlit as st

st.set_page_config(page_title="战场频谱智能指配系统", page_icon="📡", layout="wide", initial_sidebar_state="collapsed")

from ui import initialize_state
from ui.shell import load_theme
from ui.workbench import render_workbench


def main() -> None:
    initialize_state()
    load_theme()
    render_workbench()


if __name__ == "__main__":
    main()
