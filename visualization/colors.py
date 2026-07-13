FREQUENCY_STOPS = (
    "#e0f2fe",
    "#38bdf8",
    "#06b6d4",
    "#22c55e",
    "#eab308",
    "#f97316",
    "#ef4444",
    "#a855f7",
    "#312e81",
)


def frequency_to_hex(frequency_ghz: float) -> str:
    frequency = min(9.0, max(1.0, float(frequency_ghz)))
    lower_index = min(int(frequency) - 1, len(FREQUENCY_STOPS) - 1)
    if lower_index == len(FREQUENCY_STOPS) - 1:
        return FREQUENCY_STOPS[-1]
    fraction = frequency - (lower_index + 1)
    lower = _hex_to_rgb(FREQUENCY_STOPS[lower_index])
    upper = _hex_to_rgb(FREQUENCY_STOPS[lower_index + 1])
    interpolated = tuple(round(start + (end - start) * fraction) for start, end in zip(lower, upper))
    return "#" + "".join(f"{channel:02x}" for channel in interpolated)


def plotly_frequency_colorscale() -> list[list[float | str]]:
    last_index = len(FREQUENCY_STOPS) - 1
    return [[index / last_index, color] for index, color in enumerate(FREQUENCY_STOPS)]


def _hex_to_rgb(color: str) -> tuple[int, int, int]:
    return tuple(int(color[index:index + 2], 16) for index in (1, 3, 5))
