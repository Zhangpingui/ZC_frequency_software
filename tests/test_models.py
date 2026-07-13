from core.models import Device, Link, ScenarioParameters


def test_scenario_parameters_accept_confirmed_fields():
    params = ScenarioParameters(65, 12, 24, 18, 2, 6.4, 80)
    assert params.channel_occupancy_pct == 65
    assert params.link_count == 12
    assert params.device_count == 24


def test_link_exposes_frequency_interval():
    tx = Device("D-01", 0.0, 0.0)
    rx = Device("D-02", 10.0, 0.0)
    link = Link("L-01", tx, rx, 2.4, 20.0, 30.0)
    assert link.frequency_interval_ghz == (2.39, 2.41)
