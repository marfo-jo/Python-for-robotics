"""Hidden tests for the Module 0 No Hands checkpoint: parse_rmc."""
import pytest

from solution import parse_rmc

BOSTON = "$GNRMC,140000.00,A,4220.38800,N,07105.35200,W,1.200,45.10,281026,,,A*5B"
SYDNEY = "$GPRMC,081836,A,3751.65,S,14507.36,E,000.0,360.0,130998,011.3,E*62"
PARKED = "$GNRMC,135959.00,A,4220.38512,N,07105.35077,W,0.012,,281026,,,A*7E"
VOID = "$GNRMC,135959.00,V,4220.38512,N,07105.35077,W,0.000,,281026,,,N*65"


def test_basic_fields():
    """parses time, date, speed, and course from a clean active RMC"""
    r = parse_rmc(BOSTON)
    assert r["utc"] == "140000.00"
    assert r["date"] == "281026"
    assert r["speed_knots"] == pytest.approx(1.2)
    assert r["course_deg"] == pytest.approx(45.1)


def test_decimal_degrees_north_west():
    """converts ddmm.mmmm / dddmm.mmmm to decimal degrees; W longitude is negative"""
    r = parse_rmc(BOSTON)
    assert r["lat"] == pytest.approx(42.3398, abs=1e-6)
    assert r["lon"] == pytest.approx(-71.0892, abs=1e-6)


def test_south_and_east_hemispheres():
    """S latitude is negative and E longitude is positive"""
    r = parse_rmc(SYDNEY)
    assert r["lat"] == pytest.approx(-37.860833, abs=1e-5)
    assert r["lon"] == pytest.approx(145.122667, abs=1e-5)


def test_empty_course_is_none():
    """a parked receiver leaves the course field empty: course_deg is None, no crash (edge case)"""
    r = parse_rmc(PARKED)
    assert r["course_deg"] is None
    assert r["speed_knots"] == pytest.approx(0.012)


def test_void_status_returns_none():
    """status 'V' (void, no valid fix) returns None, even when position fields are filled"""
    assert parse_rmc(VOID) is None
    assert parse_rmc("$GNRMC,135957.00,V,,,,,,,281026,,,N*60") is None


def test_bad_checksum_returns_none():
    """a sentence corrupted in transit (checksum mismatch) returns None"""
    assert parse_rmc(BOSTON.replace("1.200", "9.200")) is None


def test_serial_line_and_lowercase_hex():
    """handles a trailing \r\n and lowercase checksum hex (edge case)"""
    line = "$GNRMC,220516,A,4221.123,N,07105.456,W,0.13,309.62,281026,,,A*7c\r\n"
    r = parse_rmc(line)
    assert r is not None
    assert r["utc"] == "220516"
    assert r["lat"] == pytest.approx(42 + 21.123 / 60, abs=1e-6)


def test_malformed_and_other_types_return_none():
    """truncated lines, junk, and non-RMC sentences (like GGA) return None"""
    assert parse_rmc("$GNRMC,140026.00,A,4220.4951") is None
    assert parse_rmc("") is None
    assert parse_rmc("9.0,M,-33.1,M,,*5B") is None
    assert parse_rmc("$GPGGA,123519,4807.038,N,01131.000,E,1,08,0.9,545.4,M,46.9,M,,*47") is None


def test_small_degrees_keep_leading_zeros():
    """a position near 0 degrees keeps its leading zeros: 0012.0 N is 0.2, 00030.0 W is -0.5"""
    r = parse_rmc("$GNRMC,120000.00,A,0012.00000,N,00030.00000,W,5.000,270.00,281026,,,A*6E")
    assert r["lat"] == pytest.approx(0.2, abs=1e-9)
    assert r["lon"] == pytest.approx(-0.5, abs=1e-9)
