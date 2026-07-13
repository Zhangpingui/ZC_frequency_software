import streamlit as st

from core.io import dataframe_to_links, example_dataframe, parse_uploaded_data, template_xlsx_bytes
from visualization import build_topology_figure


def _accept_frame(frame, source: str) -> None:
    links = dataframe_to_links(frame)
    st.session_state.source_frame = frame
    st.session_state.links = links
    st.session_state.analysis_records = []
    st.session_state.optimized_links = []
    st.session_state.solver_result = None
    st.session_state.data_source = source


def _accept_and_refresh(frame, source: str) -> None:
    _accept_frame(frame, source)
    st.rerun()


def _summary(links) -> tuple[int, int, str, float]:
    devices = {device.device_id: device for link in links for device in (link.transmitter, link.receiver)}
    if not links:
        return 0, 0, "—", 0.0
    xs = [device.x_km for device in devices.values()]
    ys = [device.y_km for device in devices.values()]
    area = f"{max(xs)-min(xs):.1f} × {max(ys)-min(ys):.1f} km"
    complete = sum(bool(link.link_id and link.transmitter.device_id and link.receiver.device_id) for link in links) / len(links) * 100
    return len(devices), len(links), area, complete


def render() -> None:
    st.markdown('<div class="page-kicker">02 · 原始数据建模</div>', unsafe_allow_html=True)
    st.title("数据建模")
    st.caption("导入链路数据并验证空间拓扑。画布默认覆盖 100 × 100 km 作战区域。")
    left, right = st.columns([2.2, 1], gap="large")
    with right:
        with st.container(border=True):
            st.subheader("数据接入")
            uploaded = st.file_uploader("上传链路数据", type=["xlsx", "csv", "json"], help="支持 .xlsx、.csv、.json")
            if uploaded is not None and st.button("解析并加载文件", type="primary", use_container_width=True):
                try:
                    _accept_and_refresh(parse_uploaded_data(uploaded.getvalue(), uploaded.name), uploaded.name)
                except ValueError as error:
                    st.error(str(error))
            if st.button("生成并加载模拟数据", use_container_width=True):
                try:
                    _accept_and_refresh(example_dataframe(), "系统演示数据")
                except ValueError as error:
                    st.error(str(error))
            st.download_button("下载模拟 Excel 数据", data=template_xlsx_bytes(), file_name="模拟频谱链路数据.xlsx",
                               mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
        device_count, link_count, area, completeness = _summary(st.session_state.links)
        st.markdown('<div class="summary-label">数据质量概览</div>', unsafe_allow_html=True)
        first, second = st.columns(2)
        first.metric("设备数", device_count)
        second.metric("链路数", link_count)
        st.metric("覆盖区域", area)
        st.progress(completeness / 100 if completeness else 0, text=f"字段完整率 {completeness:.0f}%")
    with left:
        with st.container(border=True):
            st.markdown('<div class="canvas-title">全域通信拓扑 <span>当前数据</span></div>', unsafe_allow_html=True)
            if st.session_state.links:
                figure = build_topology_figure(st.session_state.links)
                figure.update_layout(height=650)
                st.plotly_chart(figure, use_container_width=True, config={"displaylogo": False})
            else:
                st.markdown('<div class="empty-state"><div class="empty-icon">⌁</div><h3>尚未建立通信拓扑</h3><p>请从右侧上传任务数据，或加载内置演示数据。</p></div>', unsafe_allow_html=True)
