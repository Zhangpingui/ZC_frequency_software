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
    for index in range(15):
        tx_number = index * 2 + 1
        rx_number = tx_number + 1
        rows.append(
            {
                "link_id": f"L{index + 1:02d}",
                "tx_id": f"D{tx_number:02d}",
                "tx_x_km": round(index * 100 / 14, 2),
                "tx_y_km": round((index * 37) % 101, 2),
                "rx_id": f"D{rx_number:02d}",
                "rx_x_km": round((index * 53 + 7) % 101, 2),
                "rx_y_km": round((index * 29 + 13) % 101, 2),
                "frequency_ghz": round(2.4 + (index % 3) * 0.01, 3),
                "bandwidth_mhz": 20.0,
                "tx_power_dbm": 30.0,
            }
        )
    return pd.DataFrame(rows)


def template_xlsx_bytes() -> bytes:
    buffer = BytesIO()
    example_dataframe().to_excel(buffer, index=False)
    return buffer.getvalue()
