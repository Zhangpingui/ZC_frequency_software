from visualization.colors import frequency_to_hex, plotly_frequency_colorscale


def test_frequency_endpoints_and_clamping():
    assert frequency_to_hex(1) == "#e0f2fe"
    assert frequency_to_hex(9) == "#312e81"
    assert frequency_to_hex(-10) == "#e0f2fe"
    assert frequency_to_hex(20) == "#312e81"


def test_frequency_midpoint_interpolates_rgb_channels():
    assert frequency_to_hex(1.5) == "#8cd8fb"


def test_plotly_colorscale_has_normalized_frequency_stops():
    scale = plotly_frequency_colorscale()
    assert scale[0] == [0.0, "#e0f2fe"]
    assert scale[-1] == [1.0, "#312e81"]
    assert len(scale) == 9
