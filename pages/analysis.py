import math

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from core.conflicts import analyze_conflicts
from core.io import dataframe_to_links, example_dataframe
from core.metrics import calculate_metrics
from core.solvers import get_solver
from visualization import build_conflict_pair_figure, build_frequency_legend


def _load_demo() -> None:
    frame = example_dataframe()
    st.session_state.source_frame = frame
    st.session_state.links = dataframe_to_links(frame)


def _csv_bytes(links) -> bytes:
    rows = [{
        "link_id": link.link_id, "tx_id": link.transmitter.device_id,
        "tx_x_km": link.transmitter.x_km, "tx_y_km": link.transmitter.y_km,
        "rx_id": link.receiver.device_id, "rx_x_km": link.receiver.x_km,
        "rx_y_km": link.receiver.y_km, "frequency_ghz": link.frequency_ghz,
        "bandwidth_mhz": link.bandwidth_mhz, "tx_power_dbm": link.tx_power_dbm,
    } for link in links]
    return pd.DataFrame(rows).to_csv(index=False).encode("utf-8-sig")


def _metric_cards(links, threshold, guard):
    current = calculate_metrics(links, threshold, guard)
    result = st.session_state.solver_result
    before_count = result.before_metrics.conflict_count if result else current.conflict_count
    decrease = (before_count - current.conflict_count) / before_count * 100 if before_count else 0
    labels = (("冲突", current.conflict_count, "对"), ("下降率", decrease, "%"),
              ("频点数", current.unique_frequency_count, "个"), ("占用率", current.channel_occupancy_pct, "%"),
              ("频谱跨度", current.span_ghz, "GHz"))
    for column, (label, value, unit) in zip(st.columns(5), labels):
        display = f"{value:.1f}" if isinstance(value, float) else str(value)
        column.metric(label, f"{display} {unit}")


def render() -> None:
    st.markdown('<div class="page-kicker">03 · 冲突检测与频率优化</div>', unsafe_allow_html=True)
    st.title("冲突计算")
    st.caption("检测当前方案的同频/邻频冲突，并在同一画布切换查看优化前后链路对。")
    if not st.session_state.links:
        st.warning("当前没有可分析的链路数据。请先进入“物理拓扑”，或直接加载演示数据。")
        if st.button("加载演示数据并开始", type="primary"):
            _load_demo()
            st.rerun()
        return
    left, right = st.columns([2.25, 1], gap="large")
    with right:
        with st.container(border=True):
            st.subheader("计算控制台")
            threshold = st.number_input("空间干扰阈值（km）", min_value=0.0, max_value=500.0,
                                        value=float(st.session_state.distance_threshold), step=1.0,
                                        help="跨链路最短收发距离不超过该值时进入频率冲突判定。")
            guard = st.number_input("保护频差（MHz）", min_value=0.0, max_value=1000.0,
                                    value=float(st.session_state.guard_band), step=5.0,
                                    help="频率间隔小于该保护带宽时判定为邻频冲突。")
            st.session_state.distance_threshold = threshold
            st.session_state.guard_band = guard
            if st.button("① 检测当前方案冲突", type="primary", use_container_width=True):
                st.session_state.analysis_records = analyze_conflicts(st.session_state.links, threshold, guard)
                st.toast("冲突检测完成", icon="✅")
            algorithm = st.selectbox("优化算法", ["贪婪算法", "DQN-GNN", "遗传算法", "禁忌搜索"])
            if algorithm != "贪婪算法":
                st.caption("⚠ 演示模式：当前使用贪婪内核模拟该算法输出。")
            if st.button("② 选择算法并优化频率", use_container_width=True):
                result = get_solver(algorithm).solve(st.session_state.links, threshold, guard)
                st.session_state.solver_result = result
                st.session_state.optimized_links = result.links
                st.session_state.analysis_records = analyze_conflicts(st.session_state.links, threshold, guard)
                st.success(f"{algorithm} 完成 · {result.elapsed_seconds:.3f}s" + (" · 演示模式" if result.is_demo else ""))
            result_links = st.session_state.optimized_links or st.session_state.links
            st.download_button("下载当前结果 CSV", data=_csv_bytes(result_links), file_name="频谱指配结果.csv",
                               mime="text/csv", use_container_width=True)
    with left:
        view = st.radio("方案视图", ["优化前", "优化后"], horizontal=True,
                        disabled=not bool(st.session_state.optimized_links), key="analysis_view")
        shown_links = st.session_state.optimized_links if view == "优化后" and st.session_state.optimized_links else st.session_state.links
        records = analyze_conflicts(shown_links, threshold, guard)
        _metric_cards(shown_links, threshold, guard)
        control_a, control_b, control_c = st.columns([1, 1.5, 1])
        only_conflicts = control_a.toggle("只看冲突", value=True)
        search = control_b.text_input("搜索链路 ID", placeholder="例如 L03", label_visibility="collapsed").strip().lower()
        page_size = control_c.selectbox("每页", [10, 20, 50], index=1, label_visibility="collapsed")
        if search:
            records = [record for record in records if search in record.left.link_id.lower() or search in record.right.link_id.lower()]
        if only_conflicts:
            records = [record for record in records if record.is_conflict]
        total_pages = max(1, math.ceil(len(records) / page_size))
        page = st.number_input("页码", min_value=1, max_value=total_pages, value=1, step=1, label_visibility="collapsed")
        legend = go.Figure(data=[build_frequency_legend()])
        legend.update_layout(
            template="plotly_dark", height=100, paper_bgcolor="#0b1220", plot_bgcolor="#0b1220",
            margin={"l": 20, "r": 20, "t": 0, "b": 50},
            xaxis={"visible": False}, yaxis={"visible": False},
        )
        st.plotly_chart(legend, use_container_width=True, config={"displayModeBar": False})
        with st.container(border=True):
            figure = build_conflict_pair_figure(records, page=page, page_size=page_size)
            figure.update_layout(height=570, title=f"{view} · 链路冲突对", margin={"l": 40, "r": 25, "t": 55, "b": 115})
            st.plotly_chart(figure, use_container_width=True, config={"displaylogo": False})
        st.caption(f"共 {len(records)} 条记录 · 第 {page}/{total_pages} 页 · 红色连线表示固定高亮冲突")
