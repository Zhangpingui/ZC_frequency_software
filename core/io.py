from io import BytesIO
from pathlib import Path

import pandas as pd

from core.models import Device, Link


COLUMN_ALIASES = {
    "链路ID": "link_id",
    "发射机ID": "tx_id",
    "发射机X": "tx_x_km",
    "发射机Y": "tx_y_km",
    "接收机ID": "rx_id",
    "接收机X": "rx_x_km",
    "接收机Y": "rx_y_km",
    "使用频率GHz": "frequency_ghz",
    "带宽MHz": "bandwidth_mhz",
    "发射功率dBm": "tx_power_dbm",
}

REQUIRED_COLUMNS = (
    "link_id",
    "tx_id",
    "tx_x_km",
    "tx_y_km",
    "rx_id",
    "rx_x_km",
    "rx_y_km",
    "frequency_ghz",
)


def _normalized_dataframe(frame: pd.DataFrame) -> pd.DataFrame:
    renamed = frame.rename(columns=COLUMN_ALIASES)
    missing = [column for column in REQUIRED_COLUMNS if column not in renamed.columns]
    if missing:
        raise ValueError(f"缺少必填列：{', '.join(missing)}")
    return renamed


def _required_text(value, field: str, row_number: int) -> str:
    if pd.isna(value) or not str(value).strip():
        raise ValueError(f"第{row_number}行字段 {field} 不能为空")
    return str(value).strip()


def _number(value, field: str, row_number: int) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        raise ValueError(f"第{row_number}行字段 {field} 必须是数字") from None
    if pd.isna(number):
        raise ValueError(f"第{row_number}行字段 {field} 不能为空")
    return number


def dataframe_to_links(frame: pd.DataFrame) -> list[Link]:
    frame = _normalized_dataframe(frame)
    links = []
    for index, row in frame.iterrows():
        row_number = index + 2 if isinstance(index, int) else len(links) + 2
        frequency = _number(row["frequency_ghz"], "frequency_ghz", row_number)
        if not 1 <= frequency <= 9:
            raise ValueError(
                f"第{row_number}行字段 frequency_ghz 必须在 1 到 9 GHz 之间"
            )

        bandwidth_value = row.get("bandwidth_mhz", 20)
        power_value = row.get("tx_power_dbm", 30)
        bandwidth = 20.0 if pd.isna(bandwidth_value) else _number(
            bandwidth_value, "bandwidth_mhz", row_number
        )
        power = 30.0 if pd.isna(power_value) else _number(
            power_value, "tx_power_dbm", row_number
        )
        links.append(
            Link(
                link_id=_required_text(row["link_id"], "link_id", row_number),
                transmitter=Device(
                    _required_text(row["tx_id"], "tx_id", row_number),
                    _number(row["tx_x_km"], "tx_x_km", row_number),
                    _number(row["tx_y_km"], "tx_y_km", row_number),
                ),
                receiver=Device(
                    _required_text(row["rx_id"], "rx_id", row_number),
                    _number(row["rx_x_km"], "rx_x_km", row_number),
                    _number(row["rx_y_km"], "rx_y_km", row_number),
                ),
                frequency_ghz=frequency,
                bandwidth_mhz=bandwidth,
                tx_power_dbm=power,
            )
        )
    return links


def parse_uploaded_data(data: bytes, filename: str) -> pd.DataFrame:
    suffix = Path(filename).suffix.lower()
    try:
        if suffix == ".xlsx":
            return pd.read_excel(BytesIO(data))
        if suffix == ".csv":
            return pd.read_csv(BytesIO(data))
        if suffix == ".json":
            return pd.read_json(BytesIO(data))
    except Exception as error:
        raise ValueError(f"文件 {filename} 解析失败：{error}") from error
    raise ValueError(f"不支持的文件格式：{suffix or '无扩展名'}")


def example_dataframe() -> pd.DataFrame:
    rows = []
    positions = (
        ((10, 10), (12, 12)), ((11, 11), (13, 13)), ((12, 10), (14, 12)),
        ((13, 11), (15, 13)), ((14, 10), (16, 12)), ((0, 0), (4, 2)),
        ((30, 10), (34, 12)), ((50, 10), (54, 12)), ((70, 10), (74, 12)),
        ((90, 10), (94, 12)), ((10, 40), (14, 42)), ((35, 40), (39, 42)),
        ((60, 40), (64, 42)), ((20, 75), (24, 77)), ((80, 95), (100, 100)),
    )
    frequencies = (1.5, 1.5, 1.5, 1.5, 1.5, 2.5, 3.2, 4.0, 4.8, 5.6, 6.4, 7.2, 8.0, 8.6, 9.0)
    for index in range(15):
        tx_number = index * 2 + 1
        rx_number = tx_number + 1
        (tx_x, tx_y), (rx_x, rx_y) = positions[index]
        rows.append(
            {
                "link_id": f"L{index + 1:02d}",
                "tx_id": _device_name(tx_number),
                "tx_x_km": tx_x,
                "tx_y_km": tx_y,
                "rx_id": _device_name(rx_number),
                "rx_x_km": rx_x,
                "rx_y_km": rx_y,
                "frequency_ghz": frequencies[index],
                "bandwidth_mhz": 20.0,
                "tx_power_dbm": 30.0,
            }
        )
    return pd.DataFrame(rows)


def _device_name(number: int) -> str:
    name = ""
    while number:
        number, remainder = divmod(number - 1, 26)
        name = chr(65 + remainder) + name
    return name


def template_xlsx_bytes() -> bytes:
    buffer = BytesIO()
    example_dataframe().to_excel(buffer, index=False)
    return buffer.getvalue()


def links_to_csv_bytes(links: list[Link]) -> bytes:
    rows = [{
        "link_id": link.link_id,
        "tx_id": link.transmitter.device_id,
        "tx_x_km": link.transmitter.x_km,
        "tx_y_km": link.transmitter.y_km,
        "rx_id": link.receiver.device_id,
        "rx_x_km": link.receiver.x_km,
        "rx_y_km": link.receiver.y_km,
        "frequency_ghz": link.frequency_ghz,
        "bandwidth_mhz": link.bandwidth_mhz,
        "tx_power_dbm": link.tx_power_dbm,
    } for link in links]
    return pd.DataFrame(rows).to_csv(index=False).encode("utf-8-sig")
