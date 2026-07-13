from core.models import ScenarioParameters


def validate_scenario(params: ScenarioParameters) -> None:
    ranges = {
        "channel_occupancy_pct": (0, 100),
        "span_ratio_pct": (0, 100),
        "actual_span_ghz": (0, 8),
    }
    for field, (minimum, maximum) in ranges.items():
        value = getattr(params, field)
        if not minimum <= value <= maximum:
            raise ValueError(f"字段 {field} 必须在 {minimum} 到 {maximum} 之间")

    minimums = {
        "link_count": 1,
        "device_count": 2,
        "interference_count": 0,
        "remaining_interference_count": 0,
    }
    for field, minimum in minimums.items():
        if getattr(params, field) < minimum:
            raise ValueError(f"字段 {field} 不能小于 {minimum}")

    if params.remaining_interference_count > params.interference_count:
        raise ValueError(
            "字段 remaining_interference_count 不能大于 interference_count"
        )
