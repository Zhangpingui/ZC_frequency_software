import pytest

from core.protection_rules import parse_protection_upload


def test_parses_mixed_unit_ranges_and_tolerance():
    rules = parse_protection_upload(
        (
            "频率 | 用途 | 保护要求\n"
            "2523-2654MHz, 1.2-1.321GHz | 航空通信 | 禁止占用\n"
            "13525±10kHz | 信标 | 严格保护\n"
        ).encode(),
        "rules.txt",
    )

    assert rules.valid_count == 3
    assert rules.rules[0].lower_mhz == 2523
    assert rules.rules[1].upper_mhz == 1321
    assert rules.rules[2].lower_mhz == pytest.approx(13.515)
    assert rules.rules[2].upper_mhz == pytest.approx(13.535)


def test_parses_json_and_reports_invalid_entries():
    rules = parse_protection_upload(
        b'[{"frequency":"406-406.1MHz"},{"frequency":"bad"}]',
        "rules.json",
    )

    assert rules.valid_count == 1
    assert rules.invalid_count == 1
    assert "bad" in rules.warnings[0]
