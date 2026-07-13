from dataclasses import dataclass


@dataclass(frozen=True)
class Device:
    device_id: str
    x_km: float
    y_km: float


@dataclass(frozen=True)
class Link:
    link_id: str
    transmitter: Device
    receiver: Device
    frequency_ghz: float
    bandwidth_mhz: float = 20.0
    tx_power_dbm: float = 30.0

    @property
    def frequency_interval_ghz(self) -> tuple[float, float]:
        half_bandwidth_ghz = self.bandwidth_mhz / 2000
        return (
            round(self.frequency_ghz - half_bandwidth_ghz, 12),
            round(self.frequency_ghz + half_bandwidth_ghz, 12),
        )


@dataclass(frozen=True)
class ScenarioParameters:
    channel_occupancy_pct: float
    link_count: int
    device_count: int
    interference_count: int
    remaining_interference_count: int
    actual_span_ghz: float
    span_ratio_pct: float
