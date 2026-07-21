from pathlib import Path

import streamlit as st


DEFAULTS = {
    "scenario": None,
    "demand_dataset": None,
    "demand_source_name": "未导入",
    "demand_result": None,
    "selected_algorithm": "DQN-GNN",
    "conflict_page": 1,
}


def initialize_state() -> None:
    for key, value in DEFAULTS.items():
        if key not in st.session_state:
            st.session_state[key] = value


def load_theme() -> None:
    theme_path = Path(__file__).resolve().parents[1] / "assets" / "theme.css"
    st.markdown(f"<style>{theme_path.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)


def render_header() -> None:
    st.markdown(
        """<header class="system-header"><div class="brand-mark">FM</div><div><div class="eyebrow">频谱资源规划 · 冲突分析 · 结果导出</div><div class="system-title">战场频谱智能指配系统</div></div><div class="header-spacer"></div><div class="ready-chip"><span></span> 本地演示模式</div></header>""",
        unsafe_allow_html=True,
    )
