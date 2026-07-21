from html import escape
from time import sleep

import plotly.graph_objects as go
import streamlit as st

from core.demand_workbook import DEMO_ALGORITHMS, create_demo_optimization, example_demand_dataset, export_optimized_workbook, parse_demand_upload
from ui.shell import render_header


def render_workbench() -> None:
    render_header()
    left, center, right = st.columns([24, 43, 33], gap="medium")
    with left:
        _render_left()
    with center:
        _render_center()
    with right:
        _render_right()


def _render_left() -> None:
    with st.expander("参数配置", expanded=False):
        st.number_input("频道占用率（%）", 0.0, 100.0, 38.0, 0.1)
        st.number_input("通信链路数量（条）", 1, 100000, 15)
        st.number_input("用频设备数量（台）", 2, 200000, 30)
        st.number_input("原始干扰数量（对）", 0, 1000000, 10)
        st.number_input("优化后剩余干扰（对）", 0, 1000000, 3)
    st.markdown("<div class='panel-title'>数据接入</div>", unsafe_allow_html=True)
    uploaded = st.file_uploader("导入用频需求表", type=["xlsx"])
    if uploaded and st.button("加载导入数据", use_container_width=True):
        try:
            _load(parse_demand_upload(uploaded.getvalue(), uploaded.name), uploaded.name)
            st.success("已加载用频需求表")
        except ValueError as error:
            st.error(str(error))
    if st.button("生成模拟数据", use_container_width=True):
        _load(example_demand_dataset(), "系统模拟数据")
        st.success("已生成 23 条模拟数据")
    st.caption(f"当前数据源：{st.session_state.demand_source_name}")
    st.markdown("<div class='panel-title'>优化算法</div>", unsafe_allow_html=True)
    algorithm = st.selectbox("算法选择", DEMO_ALGORITHMS, index=1)
    if algorithm != "贪婪算法":
        st.caption("演示模式：真实算法可在后期直接接入。")
    if st.button("启动频率优化", type="primary", use_container_width=True, disabled=st.session_state.demand_dataset is None):
        progress = st.progress(0, text="正在初始化优化任务…")
        for value, text in ((35, "正在整理用频需求…"), (70, "正在计算频率建议…"), (100, "正在生成结果文件…")):
            sleep(0.9)
            progress.progress(value, text=text)
        st.session_state.demand_result = create_demo_optimization(st.session_state.demand_dataset, algorithm)
        st.session_state.conflict_page = 1
        st.rerun()


def _render_center() -> None:
    st.markdown("<div class='section-kicker'>冲突态势</div>", unsafe_allow_html=True)
    st.subheader("用频冲突组合", anchor=False)
    dataset = st.session_state.demand_dataset
    if dataset is None:
        st.markdown("<div class='empty-workspace'>请先导入实际 Excel 或生成模拟数据。</div>", unsafe_allow_html=True)
        return
    result = st.session_state.demand_result or create_demo_optimization(dataset, "DQN-GNN")
    one, two, three = st.columns(3)
    one.metric("用频需求", len(dataset.frame)); two.metric("原始冲突", "10 对"); three.metric("优化后", f"{result.after_conflict_count} 对" if st.session_state.demand_result else "未执行")
    choices = ["优化前"] + (["优化后"] if st.session_state.demand_result else [])
    view = st.radio("方案视图", choices, horizontal=True, label_visibility="collapsed")
    pairs = result.before_pairs if view == "优化前" else result.after_pairs
    page_size = 6; pages = max(1, (len(pairs) + page_size - 1) // page_size); page = min(st.session_state.conflict_page, pages)
    for pair in pairs[(page - 1) * page_size:page * page_size]:
        state = "conflict" if pair.is_conflict else "resolved"; label = "冲突" if pair.is_conflict else "已消解"
        st.markdown(f"<div class='pair-row'><div class='pair-node'>{escape(pair.left_name)}</div><div class='pair-link {state}'><span>{label}</span></div><div class='pair-node'>{escape(pair.right_name)}</div></div>", unsafe_allow_html=True)
    previous, label, following = st.columns([1, 2, 1])
    if previous.button("‹ 上一页", disabled=page == 1, use_container_width=True): st.session_state.conflict_page = page - 1; st.rerun()
    label.markdown(f"<div class='page-label'>第 {page}/{pages} 页 · 共 {len(pairs)} 组</div>", unsafe_allow_html=True)
    if following.button("下一页 ›", disabled=page == pages, use_container_width=True): st.session_state.conflict_page = page + 1; st.rerun()


def _render_right() -> None:
    st.markdown("<div class='section-kicker'>结果输出</div>", unsafe_allow_html=True)
    st.subheader("频率指配结果", anchor=False)
    result = st.session_state.demand_result
    if result is None:
        st.markdown("<div class='empty-result'>执行优化后将生成带“建议”列的 Excel 结果文件。</div>", unsafe_allow_html=True)
        return
    adjusted = sum(value.startswith("建议调整为 ") for value in result.suggestions.values())
    st.markdown("<div class='result-file'><b>用频需求表_优化结果.xlsx</b><span>已保留原始字段，仅填充“建议”列</span></div>", unsafe_allow_html=True)
    one, two = st.columns(2); one.metric("调整建议", f"{adjusted} 条"); two.metric("保持原频率", f"{len(result.suggestions)-adjusted} 条")
    st.download_button("下载结果 Excel", export_optimized_workbook(result), "用频需求表_优化结果.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
    st.markdown("<div class='panel-title comparison-title'>优化前后冲突对比</div>", unsafe_allow_html=True)
    figure = go.Figure(go.Bar(y=["优化前", "优化后"], x=[10, result.after_conflict_count], orientation="h", marker_color=["#e25562", "#39c99a"], text=["10 对", f"{result.after_conflict_count} 对"], textposition="outside"))
    figure.update_layout(height=240, margin={"l":70,"r":30,"t":10,"b":30}, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(7,27,50,.7)", font={"color":"#c8e8ff"}, xaxis={"range":[0,12],"gridcolor":"#214666"}, yaxis={"autorange":"reversed"}, showlegend=False)
    st.plotly_chart(figure, use_container_width=True, config={"displayModeBar":False})
    st.markdown(f"<div class='reduction'>冲突下降率 <b>{result.reduction_pct:g}%</b></div>", unsafe_allow_html=True)


def _load(dataset, source_name: str) -> None:
    st.session_state.demand_dataset = dataset
    st.session_state.demand_source_name = source_name
    st.session_state.demand_result = None
    st.session_state.conflict_page = 1
