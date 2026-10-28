import pytest

from solution import gga_to_latlon


def test_boston_fix():
    """a fix in Boston converts to about (42.359550, -71.094333)"""
    lat, lon = gga_to_latlon("$GPGGA,153012.00,4221.5730,N,07105.6600,W,1,09,0.9,10.2,M,-33.1,M,,*62")
    assert lat == pytest.approx(42.35955, abs=1e-6)
    assert lon == pytest.approx(-71.0943333, abs=1e-6)


def test_southern_eastern_fix():
    """a fix in Sydney converts to about (-33.856783, 151.213733)"""
    lat, lon = gga_to_latlon("$GNGGA,083000.00,3351.4070,S,15112.8240,E,1,08,1.0,25.0,M,22.1,M,,*54\r\n")
    assert lat == pytest.approx(-33.8567833, abs=1e-6)
    assert lon == pytest.approx(151.2137333, abs=1e-6)


def test_half_degree():
    """30 minutes is exactly half a degree: '0030.0000' N → 0.5 (edge case)"""
    lat, lon = gga_to_latlon("$GPGGA,000001.00,0030.0000,N,00000.0000,E,1,05,2.0,0.0,M,0.0,M,,*59")
    assert lat == pytest.approx(0.5, abs=1e-9)
    assert lon == pytest.approx(0.0, abs=1e-9)
