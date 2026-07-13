from pathlib import Path

import streamlit as st


DEFAULTS = {
    "active_page": "parameters",
    "task_id": "ZS-2026-001",
    "scenario": None,
    "links": [],
    "source_frame": None,
    "analysis_records": [],
    "optimized_links": [],
    "solver_result": None,
    "distance_threshold": 10.0,
    "guard_band": 20.0,
}


def initialize_state() -> None:
    for key, value in DEFAULTS.items():
        if key not in st.session_state:
            st.session_state[key] = value.copy() if isinstance(value, list) else value


def load_theme() -> None:
    theme_path = Path(__file__).resolve().parents[1] / "assets" / "theme.css"
    st.markdown(f"<style>{theme_path.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)


def render_header() -> None:
    st.markdown(
        f"""
        <header class="system-header">
          <div class="brand-mark">ZS</div>
          <div><div class="eyebrow">频谱资源规划与冲突分析</div>
          <div class="system-title">战场频谱智能指配演示系统</div></div>
          <div class="header-spacer"></div>
          <div class="ready-chip"><span></span> 系统就绪</div>
        </header>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar() -> None:
    links = st.session_state.links
    devices = {
        device.device_id
        for link in links
        for device in (link.transmitter, link.receiver)
    }
    algorithm = getattr(st.session_state.solver_result, "algorithm_name", "未执行")
    with st.sidebar:
        st.markdown('<div class="side-heading">任务态势摘要</div>', unsafe_allow_html=True)
        st.metric("用频设备", len(devices))
        st.metric("通信链路", len(links))
        st.caption("当前算法")
        st.markdown(f'<div class="algorithm-pill">{algorithm}</div>', unsafe_allow_html=True)
        st.markdown('<div class="side-foot">● 本地计算模式<br>数据仅在当前会话处理</div>', unsafe_allow_html=True)
