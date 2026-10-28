"""Milestone 1.3 tests for YOUR module imu_convert.py (Sprint 1, IMU data pipeline).

Put this file next to your imu_convert.py and run:
    conda activate robotics-course
    python -m pytest test_imu_convert.py -q

The spec (function names, CSV line format, return values) is on the
milestone 1.3 page. These tests only use the standard library and numpy.
"""
import math

import numpy as np
import pytest

from imu_convert import (ACCEL_LSB_PER_G, GYRO_LSB_PER_DPS, combine_bytes, parse_csv_line,
                         raw_to_celsius, raw_to_dps, raw_to_g)

GOOD = "123456,16384,-120,-16300,-1520,131,-262,7"


def test_parse_good_line():
    """parses a normal 8-field line into a tuple of 8 ints"""
    assert parse_csv_line(GOOD) == (123456, 16384, -120, -16300, -1520, 131, -262, 7)


def test_parse_strips_line_ending_and_accepts_bytes():
    """accepts raw bytes from pyserial with a trailing \\r\\n"""
    assert parse_csv_line((GOOD + "\r\n").encode("ascii")) == parse_csv_line(GOOD)


def test_parse_ignores_blank_comment_and_header():
    """returns None for a blank line, a '#' comment, and the text header row"""
    assert parse_csv_line("") is None
    assert parse_csv_line("\r\n") is None
    assert parse_csv_line("# MPU-6050 stream v1") is None
    assert parse_csv_line("t_ms,ax,ay,az,temp,gx,gy,gz") is None


def test_parse_rejects_wrong_field_count():
    """returns None for a truncated line (the first line after opening the port often is)"""
    assert parse_csv_line("123456,16384,-120,-16300") is None
    assert parse_csv_line(GOOD + ",99") is None
    assert parse_csv_line("23456,16384,-120,-16300,-1520,131,-262,") is None


def test_parse_rejects_garbage_and_bad_bytes():
    """returns None (never raises) for non-numbers and undecodable bytes (wrong baud rate)"""
    assert parse_csv_line("123456,16384,-120,abc,-1520,131,-262,7") is None
    assert parse_csv_line(b"\xf0\x9f\xff\xfe,\x80\x81") is None
    assert parse_csv_line("1.5,1,2,3,4,5,6,7") is None


def test_parse_rejects_out_of_range_values():
    """returns None when a sensor field is outside int16 or the time is negative"""
    assert parse_csv_line("100,32768,0,0,0,0,0,0") is None
    assert parse_csv_line("100,0,0,0,0,0,0,-32769") is None
    assert parse_csv_line("-5,0,0,0,0,0,0,0") is None
    assert parse_csv_line("100,32767,-32768,0,0,0,0,0") == (100, 32767, -32768, 0, 0, 0, 0, 0)


def test_combine_bytes_positive_values():
    """combines a big-endian high byte and low byte (0x3B is high, 0x3C is low)"""
    assert combine_bytes(0x00, 0x01) == 1
    assert combine_bytes(0x40, 0x00) == 16384
    assert combine_bytes(0x7F, 0xFF) == 32767


def test_combine_bytes_is_signed():
    """treats the result as signed two's complement int16 (0xFFFF is -1, not 65535)"""
    assert combine_bytes(0xFF, 0xFF) == -1
    assert combine_bytes(0x80, 0x00) == -32768
    assert combine_bytes(0xC0, 0x00) == -16384
    assert combine_bytes(0xFF, 0x83) == -125


def test_combine_bytes_rejects_non_bytes():
    """raises ValueError for values that are not a byte (0..255)"""
    for hi, lo in [(256, 0), (0, -1), (1.5, 0)]:
        with pytest.raises(ValueError):
            combine_bytes(hi, lo)


def test_unit_constants_and_conversions():
    """uses 16384 LSB/g and 131 LSB/(deg/s) at the default full-scale ranges"""
    assert ACCEL_LSB_PER_G == 16384
    assert GYRO_LSB_PER_DPS == 131
    assert raw_to_g(16384) == pytest.approx(1.0)
    assert raw_to_g(-8192) == pytest.approx(-0.5)
    assert raw_to_dps(131) == pytest.approx(1.0)
    assert raw_to_dps(-32768) == pytest.approx(-250.137, abs=1e-3)
    assert isinstance(raw_to_g(1), float)


def test_conversions_with_other_ranges():
    """accepts the scale for other ranges (+-8 g is 4096 LSB/g, +-2000 deg/s is 16.4)"""
    assert raw_to_g(4096, lsb_per_g=4096) == pytest.approx(1.0)
    assert raw_to_dps(164, lsb_per_dps=16.4) == pytest.approx(10.0)


def test_conversions_work_on_numpy_arrays():
    """converts a whole numpy column at once (vectorized, no loop needed)"""
    raw = np.array([0, 16384, -16384, 8192])
    np.testing.assert_allclose(raw_to_g(raw), [0.0, 1.0, -1.0, 0.5])
    np.testing.assert_allclose(raw_to_dps(np.array([262, -131])), [2.0, -1.0])


def test_temperature_formula():
    """applies the MPU-6050 datasheet formula T = raw/340 + 36.53"""
    assert raw_to_celsius(0) == pytest.approx(36.53)
    assert raw_to_celsius(-1520) == pytest.approx(32.059, abs=1e-3)
    assert math.isfinite(raw_to_celsius(-32768))
