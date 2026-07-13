import pytest

from core.models import ScenarioParameters
from core.validation import validate_scenario


def make_params(**changes):
    values = dict(
        channel_occupancy_pct=50,
        link_count=1,
        device_count=2,
        interference_count=0,
        remaining_interference_count=0,
        actual_span_ghz=4,
        span_ratio_pct=50,
    )
    values.update(changes)
    return ScenarioParameters(**values)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("channel_occupancy_pct", 0),
        ("channel_occupancy_pct", 100),
        ("span_ratio_pct", 0),
        ("span_ratio_pct", 100),
        ("actual_span_ghz", 0),
        ("actual_span_ghz", 8),
    ],
)
def test_validate_scenario_accepts_inclusive_boundaries(field, value):
    validate_scenario(make_params(**{field: value}))


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("channel_occupancy_pct", -0.1),
        ("channel_occupancy_pct", 100.1),
        ("span_ratio_pct", -1),
        ("span_ratio_pct", 101),
        ("link_count", 0),
        ("device_count", 1),
        ("interference_count", -1),
        ("remaining_interference_count", -1),
        ("actual_span_ghz", -0.1),
        ("actual_span_ghz", 8.1),
    ],
)
def test_validate_scenario_rejects_invalid_field_with_chinese_message(field, value):
    with pytest.raises(ValueError, match=field):
        validate_scenario(make_params(**{field: value}))


def test_remaining_interference_cannot_exceed_total():
    with pytest.raises(ValueError, match="remaining_interference_count"):
        validate_scenario(
            make_params(interference_count=2, remaining_interference_count=3)
        )
