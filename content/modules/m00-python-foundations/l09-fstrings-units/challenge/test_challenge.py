import pytest

from solution import format_position, nmea_to_decimal


def test_latitude_north():
    """'4220.0101', 'N' → 42.333502 (42° plus 20.0101 minutes)"""
    assert nmea_to_decimal("4220.0101", "N") == pytest.approx(42.3335016667, abs=1e-7)


def test_longitude_west_is_negative():
    """'07105.6600', 'W' → -71.094333 (west of Greenwich is negative)"""
    assert nmea_to_decimal("07105.6600", "W") == pytest.approx(-71.0943333333, abs=1e-7)


def test_latitude_south_is_negative():
    """'3351.4070', 'S' → -33.856783 (south of the equator is negative)"""
    assert nmea_to_decimal("3351.4070", "S") == pytest.approx(-33.8567833333, abs=1e-7)


def test_longitude_three_degree_digits():
    """'15112.8240', 'E' → 151.213733 (three degree digits, more than 99°)"""
    assert nmea_to_decimal("15112.8240", "E") == pytest.approx(151.2137333333, abs=1e-7)


def test_fewer_decimal_places():
    """works with 3 decimal places of minutes: '4807.038' N and '01131.000' E"""
    assert nmea_to_decimal("4807.038", "N") == pytest.approx(48.1173, abs=1e-7)
    assert nmea_to_decimal("01131.000", "E") == pytest.approx(11.5166666667, abs=1e-7)


def test_zero_degrees():
    """near the equator and prime meridian: '0030.0000' N → 0.5, '00000.0000' E → 0.0 (edge case)"""
    assert nmea_to_decimal("0030.0000", "N") == pytest.approx(0.5, abs=1e-9)
    assert nmea_to_decimal("00000.0000", "E") == pytest.approx(0.0, abs=1e-9)


def test_empty_fields_return_none():
    """returns None when the value or the hemisphere is empty (no fix yet)"""
    assert nmea_to_decimal("", "") is None
    assert nmea_to_decimal("4220.0101", "") is None


def test_returns_a_float():
    """nmea_to_decimal returns a float, not a string"""
    assert isinstance(nmea_to_decimal("4220.0101", "N"), float)


def test_format_north_west():
    """format_position(42.3335017, -71.0943333) → '42.333502°N, 71.094333°W'"""
    assert format_position(42.3335017, -71.0943333) == "42.333502°N, 71.094333°W"


def test_format_south_east():
    """negative latitude prints as °S, positive longitude as °E, with no minus signs"""
    assert format_position(-33.8567833, 151.2137333) == "33.856783°S, 151.213733°E"


def test_format_always_six_decimals():
    """always exactly 6 decimal places, trailing zeros kept: '5.500000°N, 0.000000°E' (edge case)"""
    assert format_position(5.5, 0.0) == "5.500000°N, 0.000000°E"


def test_convert_then_format():
    """the two functions work together on the classic $GPGGA example"""
    lat = nmea_to_decimal("4807.038", "N")
    lon = nmea_to_decimal("01131.000", "E")
    assert format_position(lat, lon) == "48.117300°N, 11.516667°E"
