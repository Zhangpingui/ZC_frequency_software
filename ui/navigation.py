import streamlit as st


STEPS = (
    ("parameters", "01", "参数配置"),
    ("topology", "02", "数据建模"),
    ("analysis", "03", "冲突计算"),
)


def _navigate(page: str) -> None:
    st.session_state.active_page = page


def render_bottom_navigation() -> None:
    current = st.session_state.active_page
    current_index = next(index for index, step in enumerate(STEPS) if step[0] == current)
    st.markdown('<div class="nav-spacer"></div>', unsafe_allow_html=True)
    columns = st.columns([0.9, 1.25, 1.25, 1.25, 0.9], gap="small")
    with columns[0]:
        st.button("‹ 上一步", disabled=current_index == 0, use_container_width=True,
                  on_click=_navigate, args=(STEPS[max(0, current_index - 1)][0],), key="nav_prev")
    for column, (page, number, label) in zip(columns[1:4], STEPS):
        with column:
            marker = "●" if page == current else "○"
            st.button(f"{marker}  {number}  {label}", use_container_width=True,
                      on_click=_navigate, args=(page,), key=f"nav_{page}", type="primary" if page == current else "secondary")
    with columns[4]:
        st.button("下一步 ›", disabled=current_index == len(STEPS) - 1, use_container_width=True,
                  on_click=_navigate, args=(STEPS[min(len(STEPS) - 1, current_index + 1)][0],), key="nav_next")
