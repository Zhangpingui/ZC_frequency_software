import math

import plotly.graph_objects as go

from .colors import frequency_to_hex, plotly_frequency_colorscale


def build_frequency_legend() -> go.Heatmap:
    return go.Heatmap(
        z=[[1, 9]],
        x=[1, 9],
        y=[0, 0],
        zmin=1,
        zmax=9,
        colorscale=plotly_frequency_colorscale(),
        showscale=True,
        opacity=0,
        hoverinfo="skip",
        colorbar={
            "title": {"text": "频率 (GHz)", "side": "top"},
            "orientation": "h",
            "x": 0.5,
            "xanchor": "center",
            "y": -0.12,
            "tickmode": "array",
            "tickvals": list(range(1, 10)),
            "ticktext": [f"{value}G" for value in range(1, 10)],
            "len": 0.8,
        },
    )


def build_conflict_pair_figure(records, page=1, page_size=20, only_conflicts=False) -> go.Figure:
    if page_size <= 0:
        raise ValueError("page_size must be positive")
    records = list(records)
    if only_conflicts:
        records = [record for record in records if _is_conflict(record)]
    total_records = len(records)
    total_pages = max(1, math.ceil(total_records / page_size))
    page = min(max(1, int(page)), total_pages)
    visible = records[(page - 1) * page_size:page * page_size]

    figure = go.Figure()
    if not visible:
        figure.add_annotation(text="暂无数据", x=0.5, y=0.5, xref="paper", yref="paper", showarrow=False)
    else:
        spacing = 1.5
        for row, record in enumerate(visible):
            y_position = (len(visible) - row) * spacing
            for x_position, link, side in ((0, record.left, "链路一"), (1, record.right, "链路二")):
                figure.add_trace(go.Scatter(
                    x=[x_position],
                    y=[y_position],
                    mode="markers+text",
                    name=side,
                    legendgroup=side,
                    showlegend=row == 0,
                    marker={"size": 28, "color": frequency_to_hex(link.frequency_ghz), "line": {"color": "#e2e8f0", "width": 1}},
                    text=[link.link_id],
                    textposition="middle left" if x_position == 0 else "middle right",
                    textfont={"size": 11, "color": "#e2e8f0"},
                    customdata=[[link.frequency_ghz]],
                    hovertemplate="%{text}<br>%{customdata[0]:.3f} GHz<extra></extra>",
                ))
            if _is_conflict(record):
                figure.add_trace(go.Scatter(
                    x=[0, 1], y=[y_position, y_position], mode="lines",
                    name="冲突连接", showlegend=False,
                    line={"color": "#ff3344", "width": 3, "dash": "solid"},
                    hoverinfo="skip",
                ))
        figure.add_trace(build_frequency_legend())

    max_y = len(visible) * spacing if visible else 1.6
    figure.update_layout(
        template="plotly_dark",
        paper_bgcolor="#0b1220",
        plot_bgcolor="#111827",
        title=f"冲突链路对（第 {page}/{total_pages} 页）",
        xaxis={"tickmode": "array", "tickvals": [0, 1], "ticktext": ["链路一", "链路二"], "range": [-0.4, 1.4]},
        yaxis={"title": "记录", "showticklabels": False, "range": [0, max_y + spacing]},
        legend={"title": {"text": "图例"}},
        margin={"l": 50, "r": 30, "t": 60, "b": 110},
        meta={
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
            "total_records": total_records,
            "visible_records": len(visible),
        },
    )
    return figure


def _is_conflict(record) -> bool:
    conflict_type = getattr(record, "conflict_type", None)
    return conflict_type is not None and str(conflict_type).lower() not in {"", "none", "no_conflict", "无冲突"}
