import plotly.graph_objects as go


def build_topology_figure(links) -> go.Figure:
    links = list(links)
    devices = {}
    for link in links:
        devices[link.transmitter.device_id] = link.transmitter
        devices[link.receiver.device_id] = link.receiver

    figure = go.Figure()
    for link in links:
        figure.add_trace(go.Scatter(
            x=[link.transmitter.x_km, link.receiver.x_km],
            y=[link.transmitter.y_km, link.receiver.y_km],
            mode="lines",
            name="通信链路",
            legendgroup="links",
            showlegend=not any(trace.legendgroup == "links" for trace in figure.data),
            line={"color": "rgba(56, 189, 248, 0.45)", "width": 3},
            hovertemplate=f"链路 {link.link_id}<extra></extra>",
        ))

    ordered_devices = list(devices.values())
    figure.add_trace(go.Scatter(
        x=[device.x_km for device in ordered_devices],
        y=[device.y_km for device in ordered_devices],
        mode="markers+text",
        name="设备",
        marker={"size": 12, "color": "#e2e8f0", "line": {"color": "#38bdf8", "width": 2}},
        text=[f"{device.device_id} ({device.x_km:.1f}, {device.y_km:.1f})" for device in ordered_devices],
        textposition="top center",
        textfont={"size": 10, "color": "#cbd5e1"},
        cliponaxis=False,
        customdata=[[device.device_id, device.x_km, device.y_km] for device in ordered_devices],
        hovertemplate="设备 %{customdata[0]}<br>x=%{customdata[1]:.2f} km<br>y=%{customdata[2]:.2f} km<extra></extra>",
    ))

    x_values = [device.x_km for device in ordered_devices] or [0, 100]
    y_values = [device.y_km for device in ordered_devices] or [0, 100]
    x_range = _axis_range(x_values)
    y_range = _axis_range(y_values)
    figure.update_layout(
        template="plotly_dark",
        paper_bgcolor="#0b1220",
        plot_bgcolor="#111827",
        title="通信拓扑",
        legend={"title": {"text": "图例"}},
        xaxis={"title": "X 坐标 (km)", "range": x_range, "scaleanchor": "y", "scaleratio": 1},
        yaxis={"title": "Y 坐标 (km)", "range": y_range},
        margin={"l": 60, "r": 30, "t": 60, "b": 60},
    )
    return figure


def _axis_range(values):
    lower = min(0.0, min(values))
    upper = max(100.0, max(values))
    padding = max(5.0, (upper - lower) * 0.05)
    return [lower - padding, upper + padding]
