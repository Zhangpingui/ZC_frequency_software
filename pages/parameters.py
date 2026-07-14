import streamlit as st

from core.models import ScenarioParameters
from core.validation import validate_scenario


FIELDS = (
    ("channel_occupancy_pct", "频道占用率", 38.0, "%", "示例：38%，反映当前频点资源占用水平。", 0.0, 100.0, 0.1),
    ("link_count", "通信链路数量", 15, "条", "示例：15 条待指配通信链路。", 1, 100000, 1),
    ("device_count", "用频设备数量", 30, "台", "示例：30 台收发设备。", 2, 200000, 1),
    ("interference_count", "链路间干扰数量", 12, "对", "示例：检测到 12 对潜在干扰。", 0, 1000000, 1),
    ("remaining_interference_count", "最优化后剩余干扰数", 2, "对", "示例：优化目标为剩余 2 对。", 0, 1000000, 1),
    ("actual_span_ghz", "频谱指配实际跨度", 4.8, "GHz", "最高与最低工作频率之差，范围 0–8 GHz。", 0.0, 8.0, 0.1),
    ("span_ratio_pct", "频谱指配跨度比例", 60.0, "%", "实际跨度相对于 1–9 GHz 可用频段的比例。", 0.0, 100.0, 0.1),
)


def render() -> None:
    st.markdown('<div class="page-kicker">01 · 任务场景定义</div>', unsafe_allow_html=True)
    st.title("参数配置")
    st.caption("定义本次频谱指配任务的规模、现状与优化目标。")
    saved = st.session_state.scenario
    with st.form("scenario_form", border=True):
        columns = st.columns(2, gap="large")
        values = {}
        for index, (field, label, default, unit, help_text, minimum, maximum, step) in enumerate(FIELDS):
            value = getattr(saved, field) if saved else default
            with columns[index % 2]:
                values[field] = st.number_input(
                    f"{label}（{unit}）", min_value=minimum, max_value=maximum,
                    value=value, step=step, help=help_text, key=f"param_{field}",
                )
        submitted = st.form_submit_button("✓ 校验并保存任务场景", type="primary", use_container_width=True)
    if submitted:
        try:
            params = ScenarioParameters(
                channel_occupancy_pct=float(values["channel_occupancy_pct"]),
                link_count=int(values["link_count"]), device_count=int(values["device_count"]),
                interference_count=int(values["interference_count"]),
                remaining_interference_count=int(values["remaining_interference_count"]),
                actual_span_ghz=float(values["actual_span_ghz"]), span_ratio_pct=float(values["span_ratio_pct"]),
            )
            validate_scenario(params)
            st.session_state.scenario = params
            st.success("任务场景已通过校验并保存。可进入「物理拓扑」导入链路数据。")
        except ValueError as error:
            st.error(f"参数校验失败：{error}")
