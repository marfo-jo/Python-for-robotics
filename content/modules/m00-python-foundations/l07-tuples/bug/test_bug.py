import pytest

from solution import inside_fence, position

TEST_AREA = (42.3350, 42.3360, -71.0935, -71.0920)
PARKED = "$GPGGA,152305.00,4220.1234,N,07105.5678,W,1,09,1.1,12.3,M,-33.1,M,,*64"
ALSO_INSIDE = "$GPGGA,152322.00,4220.1500,N,07105.5300,W,1,08,1.0,12.6,M,-33.1,M,,*6E"
TOO_FAR_NORTH = "$GPGGA,152320.00,4220.2000,N,07105.5678,W,1,09,1.1,12.3,M,-33.1,M,,*65"
TOO_FAR_WEST = "$GPGGA,152321.00,4220.1234,N,07105.7000,W,1,09,1.1,12.3,M,-33.1,M,,*69"


def test_position_order():
    """position() still returns (lat, lon), latitude first"""
    lat, lon = position(PARKED)
    assert lat == pytest.approx(42.33539, abs=1e-6)
    assert lon == pytest.approx(-71.092797, abs=1e-6)


def test_parked_inside():
    """a robot parked in the middle of the test area is inside"""
    assert inside_fence(PARKED, TEST_AREA) is True


def test_second_point_inside():
    """another point in the test area is inside"""
    assert inside_fence(ALSO_INSIDE, TEST_AREA) is True


def test_outside_north():
    """a fix north of the area is outside"""
    assert inside_fence(TOO_FAR_NORTH, TEST_AREA) is False


def test_outside_west():
    """a fix west of the area is outside"""
    assert inside_fence(TOO_FAR_WEST, TEST_AREA) is False
