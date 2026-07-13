import pytest

from core.models import Device, Link


@pytest.fixture
def link_factory():
    def make(link_id, frequency_ghz, tx=(0.0, 0.0), rx=(1.0, 0.0), bandwidth_mhz=20.0):
        return Link(
            link_id,
            Device(f"{link_id}-tx", *tx),
            Device(f"{link_id}-rx", *rx),
            frequency_ghz,
            bandwidth_mhz,
        )

    return make
