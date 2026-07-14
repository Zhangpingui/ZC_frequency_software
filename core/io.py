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
    # Realistic battlefield comm network: command posts, relay stations,
    # forward units, artillery, recon, EW, logistics across 100x100km AO.
    links_data = [
        # --- Alpha sector (command cluster, NW) ---
        ("L01", "CMD-A", 8, 72, "REL-1", 18, 80, 2.0, 20, 37),
        ("L02", "CMD-A", 8, 72, "FWD-1", 22, 65, 2.0, 20, 40),
        ("L03", "REL-1", 18, 80, "FWD-2", 30, 88, 2.0, 20, 33),
        ("L04", "FWD-2", 30, 88, "ART-1", 25, 70, 2.0, 20, 35),
        # --- Bravo sector (central relay hub) ---
        ("L05", "REL-2", 45, 55, "CMD-B", 50, 62, 5.5, 20, 38),
        ("L06", "REL-2", 45, 55, "FWD-3", 52, 48, 5.5, 20, 36),
        ("L07", "CMD-B", 50, 62, "ART-2", 55, 70, 5.5, 20, 40),
        ("L08", "FWD-3", 52, 48, "EW-1", 40, 48, 4.8, 20, 34),
        ("L09", "EW-1", 40, 48, "RCN-1", 60, 42, 4.8, 20, 30),
        # --- Charlie sector (eastern forward, SE) ---
        ("L10", "CMD-C", 78, 25, "REL-3", 85, 18, 7.5, 20, 38),
        ("L11", "CMD-C", 78, 25, "FWD-4", 72, 18, 7.5, 20, 36),
        ("L12", "REL-3", 85, 18, "ART-3", 90, 28, 7.2, 20, 35),
        ("L13", "FWD-4", 72, 18, "RCN-2", 92, 12, 7.5, 20, 30),
        # --- Cross-sector backbone links ---
        ("L14", "REL-1", 18, 80, "REL-2", 45, 55, 3.5, 40, 43),
        ("L15", "REL-2", 45, 55, "CMD-C", 78, 25, 6.2, 40, 43),
        ("L16", "CMD-A", 8, 72, "CMD-B", 50, 62, 1.8, 40, 45),
        # --- Support / logistics links ---
        ("L17", "LOG-1", 15, 40, "LOG-2", 30, 35, 4.5, 20, 30),
        ("L18", "LOG-2", 30, 35, "FWD-1", 22, 65, 4.2, 20, 30),
        ("L19", "EW-2", 65, 80, "CMD-B", 50, 62, 6.8, 20, 34),
        ("L20", "RCN-3", 35, 15, "LOG-2", 30, 35, 3.53, 20, 30),
        # --- Additional tactical links ---
        ("L21", "ART-1", 25, 70, "FWD-2", 30, 88, 2.4, 20, 33),
        ("L22", "RCN-1", 60, 42, "FWD-3", 52, 48, 4.8, 20, 32),
        ("L23", "FWD-4", 72, 18, "ART-3", 90, 28, 8.2, 20, 35),
        ("L24", "LOG-1", 15, 40, "CMD-A", 8, 72, 1.5, 20, 36),
        ("L25", "RCN-2", 92, 12, "ART-3", 90, 28, 8.8, 20, 30),
    ]
    for (link_id, tx_id, tx_x, tx_y, rx_id, rx_x, rx_y,
         freq, bw, power) in links_data:
        rows.append({
            "link_id": link_id,
            "tx_id": tx_id,
            "tx_x_km": tx_x,
            "tx_y_km": tx_y,
            "rx_id": rx_id,
            "rx_x_km": rx_x,
            "rx_y_km": rx_y,
            "frequency_ghz": freq,
            "bandwidth_mhz": float(bw),
            "tx_power_dbm": float(power),
        })
    return pd.DataFrame(rows)


def template_xlsx_bytes() -> bytes:
    buffer = BytesIO()
    example_dataframe().to_excel(buffer, index=False)
    return buffer.getvalue()
