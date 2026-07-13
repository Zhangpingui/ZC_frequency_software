from io import BytesIO

import pandas as pd
import pytest

from core.io import (
    dataframe_to_links,
    example_dataframe,
    parse_uploaded_data,
    template_xlsx_bytes,
)
from core.metrics import calculate_metrics
from core.solvers.greedy import GreedySolver


def standard_row(**changes):
    row = {
        "link_id": "L1",
        "tx_id": "D1",
        "tx_x_km": 1,
        "tx_y_km": 2,
        "rx_id": "D2",
        "rx_x_km": 3,
        "rx_y_km": 4,
        "frequency_ghz": 5,
    }
    row.update(changes)
    return row


def test_dataframe_to_links_supports_chinese_aliases_and_defaults():
    frame = pd.DataFrame(
        [
            {
                "链路ID": "链路1",
                "发射机ID": "设备1",
                "发射机X": 1,
                "发射机Y": 2,
                "接收机ID": "设备2",
                "接收机X": 3,
                "接收机Y": 4,
                "使用频率GHz": 5.5,
            }
        ]
    )
    link = dataframe_to_links(frame)[0]
    assert link.link_id == "链路1"
    assert link.transmitter.device_id == "设备1"
    assert link.receiver.x_km == 3
    assert link.frequency_ghz == 5.5
    assert link.bandwidth_mhz == 20
    assert link.tx_power_dbm == 30


def test_dataframe_to_links_reads_optional_chinese_columns():
    row = standard_row()
    row.update({"带宽MHz": 40, "发射功率dBm": 26})
    link = dataframe_to_links(pd.DataFrame([row]))[0]
    assert (link.bandwidth_mhz, link.tx_power_dbm) == (40, 26)


def test_dataframe_to_links_reports_missing_columns():
    frame = pd.DataFrame([standard_row()]).drop(columns=["rx_id"])
    with pytest.raises(ValueError, match="缺少必填列.*rx_id"):
        dataframe_to_links(frame)


@pytest.mark.parametrize("frequency", [0.99, 9.01, "坏数据"])
def test_dataframe_to_links_reports_bad_row(frequency):
    with pytest.raises(ValueError, match="第2行.*frequency_ghz"):
        dataframe_to_links(pd.DataFrame([standard_row(frequency_ghz=frequency)]))


@pytest.mark.parametrize("suffix", ["csv", "json", "xlsx"])
def test_parse_uploaded_data_supports_three_formats(suffix):
    frame = pd.DataFrame([standard_row()])
    buffer = BytesIO()
    if suffix == "csv":
        data = frame.to_csv(index=False).encode("utf-8-sig")
    elif suffix == "json":
        data = frame.to_json(orient="records", force_ascii=False).encode()
    else:
        frame.to_excel(buffer, index=False)
        data = buffer.getvalue()
    parsed = parse_uploaded_data(data, f"links.{suffix}")
    assert parsed.loc[0, "link_id"] == "L1"


def test_parse_uploaded_data_rejects_unknown_format():
    with pytest.raises(ValueError, match="不支持"):
        parse_uploaded_data(b"x", "links.txt")


def test_example_and_template_have_expected_scale():
    frame = example_dataframe()
    assert len(frame) == 15
    assert len(set(frame["tx_id"]) | set(frame["rx_id"])) == 30
    assert (frame.loc[0, "tx_id"], frame.loc[0, "rx_id"]) == ("A", "B")
    assert frame.loc[14, "rx_id"] == "AD"
    assert frame[["tx_x_km", "tx_y_km", "rx_x_km", "rx_y_km"]].min().min() >= 0
    assert frame[["tx_x_km", "tx_y_km", "rx_x_km", "rx_y_km"]].max().max() <= 100
    assert frame["frequency_ghz"].between(1, 9).all()
    assert frame["frequency_ghz"].min() <= 1.5
    assert frame["frequency_ghz"].max() >= 8.5
    downloaded = pd.read_excel(BytesIO(template_xlsx_bytes()))
    assert len(downloaded) == 15


def test_example_data_demonstrates_conflict_reduction():
    links = dataframe_to_links(example_dataframe())
    before = calculate_metrics(links, 10.0, 20.0)
    result = GreedySolver().solve(links, 10.0, 20.0)
    assert before.conflict_count > 0
    assert result.after_metrics.conflict_count < before.conflict_count


def test_example_conflicts_span_multiple_frequency_colors():
    from core.conflicts import analyze_conflicts

    links = dataframe_to_links(example_dataframe())
    conflicts = [record for record in analyze_conflicts(links, 10.0, 20.0) if record.is_conflict]
    frequencies = {record.left.frequency_ghz for record in conflicts} | {record.right.frequency_ghz for record in conflicts}
    assert len(conflicts) == 10
    assert len(frequencies) >= 3
