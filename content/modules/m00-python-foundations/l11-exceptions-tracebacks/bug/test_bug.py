import pytest

from solution import mean_satellites

G1 = "$GPGGA,153012.00,4220.0101,N,07105.6600,W,1,09,0.9,10.2,M,-33.1,M,,*62"
G3 = "$GPGGA,153014.00,4220.0110,N,07105.6584,W,1,10,0.8,10.5,M,-33.1,M,,*65"
EMPTY_SATS = "$GPGGA,,,,,,0,,,,,,,,*66"


def test_all_good_lines():
    """two fixes with 9 and 10 satellites give a mean of 9.5"""
    assert mean_satellites([G1, G3]) == pytest.approx(9.5)


def test_junk_line_ignored():
    """a non-NMEA junk line is ignored completely, so the mean is still 9.5"""
    assert mean_satellites([G1, "u-blox NEO-M8N ROM 2.01", G3]) == pytest.approx(9.5)


def test_empty_field_ignored():
    """a sentence with an empty satellites field is ignored, so the mean is 9.0"""
    assert mean_satellites([EMPTY_SATS, G1, EMPTY_SATS]) == pytest.approx(9.0)


def test_nothing_usable():
    """a log with no usable lines gives 0.0 (edge case)"""
    assert mean_satellites(["", "junk"]) == 0.0
