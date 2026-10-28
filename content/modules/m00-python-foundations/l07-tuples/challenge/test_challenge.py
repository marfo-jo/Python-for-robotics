import pytest

from solution import bounding_box, fix_record

BOSTON_1 = "$GPGGA,152305.00,4220.1234,N,07105.5678,W,1,09,1.1,12.3,M,-33.1,M,,*64"
BOSTON_2 = "$GPGGA,152309.00,4220.1270,N,07105.5725,W,1,10,0.7,13.1,M,-33.1,M,,*6D"
MUNICH = "$GPGGA,123519,4807.038,N,01131.000,E,1,08,0.9,545.4,M,46.9,M,,*47"
SYDNEY = "$GPGGA,084512.00,3351.5210,S,15112.7340,E,1,10,0.8,38.6,M,22.1,M,,*4A"
GNGGA = "$GNGGA,201530.00,4220.0101,N,07105.6600,W,4,12,0.6,10.2,M,-33.1,M,1.0,0000*52"
RMC = "$GPRMC,152305.00,A,4220.1234,N,07105.5678,W,0.05,87.30,281026,,,A*75"
NO_FIX = "$GPGGA,,,,,,0,00,,,M,,M,,*66"
CUT_OFF = "$GPGGA,152310.00,4220.12"


def test_fix_record_is_a_tuple():
    """fix_record returns a tuple with exactly 3 items (not a list)"""
    record = fix_record(BOSTON_1)
    assert isinstance(record, tuple)
    assert len(record) == 3


def test_fix_record_values():
    """fix_record gives (time, lat, lon) with west longitude negative"""
    time, lat, lon = fix_record(BOSTON_1)
    assert time == "152305.00"
    assert lat == pytest.approx(42.33539, abs=1e-6)
    assert lon == pytest.approx(-71.092797, abs=1e-6)


def test_fix_record_lat_before_lon():
    """latitude comes BEFORE longitude in the tuple (Munich: 48.1 N, 11.5 E)"""
    record = fix_record(MUNICH)
    assert record[1] == pytest.approx(48.1173, abs=1e-6)
    assert record[2] == pytest.approx(11.516667, abs=1e-6)


def test_fix_record_southern_eastern():
    """southern latitude is negative and eastern longitude positive (Sydney)"""
    time, lat, lon = fix_record(SYDNEY)
    assert lat == pytest.approx(-33.858683, abs=1e-6)
    assert lon == pytest.approx(151.212233, abs=1e-6)


def test_fix_record_other_talker_whitespace():
    """fix_record handles $GNGGA with stray spaces and \\r\\n (edge case)"""
    time, lat, lon = fix_record("  " + GNGGA + "\r\n")
    assert time == "201530.00"
    assert lat == pytest.approx(42.333502, abs=1e-6)


def test_fix_record_not_gga():
    """fix_record returns None for an RMC sentence"""
    assert fix_record(RMC) is None


def test_fix_record_no_position():
    """fix_record returns None when the lat/lon fields are empty, without crashing (edge case)"""
    assert fix_record(NO_FIX) is None


def test_fix_record_cut_off():
    """fix_record returns None for a cut-off line instead of raising IndexError (bad input)"""
    assert fix_record(CUT_OFF) is None


def test_bounding_box_basic():
    """bounding_box returns ((min_lat, min_lon), (max_lat, max_lon)) as tuples"""
    records = [("1", 48.2, 11.6), ("2", 48.1, 11.7), ("3", 48.3, 11.5)]
    box = bounding_box(records)
    assert box == ((48.1, 11.5), (48.3, 11.7))
    assert isinstance(box, tuple) and isinstance(box[0], tuple) and isinstance(box[1], tuple)


def test_bounding_box_negative_coordinates():
    """bounding_box works when every longitude is negative (Boston, west of Greenwich)"""
    records = [fix_record(BOSTON_1), fix_record(BOSTON_2)]
    (min_lat, min_lon), (max_lat, max_lon) = bounding_box(records)
    assert min_lat == pytest.approx(42.33539, abs=1e-6)
    assert max_lat == pytest.approx(42.33545, abs=1e-6)
    assert min_lon == pytest.approx(-71.092875, abs=1e-6)
    assert max_lon == pytest.approx(-71.092797, abs=1e-6)


def test_bounding_box_single_record():
    """with one record, both corners are that point (edge case)"""
    assert bounding_box([("1", -33.9, 151.2)]) == ((-33.9, 151.2), (-33.9, 151.2))


def test_bounding_box_empty():
    """an empty list of records gives None (edge case)"""
    assert bounding_box([]) is None
