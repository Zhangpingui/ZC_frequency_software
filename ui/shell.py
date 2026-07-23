from pathlib import Path

import streamlit as st


DEFAULTS = {
    "scenario": None,
    "demand_dataset": None,
    "demand_source_name": "未导入",
    "protection_rules": None,
    "protection_source_name": "未导入",
    "protection_warnings": (),
    "demand_result": None,
    "conflict_page": 1,
}


def initialize_state() -> None:
    for key, value in DEFAULTS.items():
        if key not in st.session_state:
            st.session_state[key] = value


def load_theme() -> None:
    theme_path = Path(__file__).resolve().parents[1] / "assets" / "theme.css"
    input_theme = (
        ".stTextInput input{background:#0a2947!important;"
        "border:1px solid #33739b!important;border-radius:5px!important;"
        "color:#e5f4ff!important;-webkit-text-fill-color:#e5f4ff!important}"
        ".stTextInput input::placeholder{color:#86abc5!important;"
        "-webkit-text-fill-color:#86abc5!important;opacity:1}"
    )
    st.markdown(
        f"<style>{theme_path.read_text(encoding='utf-8')}{input_theme}</style>",
        unsafe_allow_html=True,
    )


def render_header() -> None:
    st.markdown(
        """<header class="system-header"><div class="brand-mark">FM</div><div class="header-title-block"><div class="eyebrow">频谱资源规划 · 冲突分析</div><div class="system-title">战场频谱智能指配系统</div></div><div class="header-spacer"></div><div class="ready-chip"><span></span> 本地运行</div></header>""",
        unsafe_allow_html=True,
    )
