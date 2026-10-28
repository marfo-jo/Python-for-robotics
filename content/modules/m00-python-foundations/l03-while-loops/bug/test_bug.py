import pytest

from solution import gyro_bias


def test_uses_exactly_the_first_n():
    """averages samples 0 to n-1 and ignores later samples (the robot started moving)"""
    assert gyro_bias([0.021, 0.019, 0.020, 0.020, 0.250], 4) == pytest.approx(0.020)


def test_first_sample_counts():
    """the very first sample (index 0) is included in the average"""
    assert gyro_bias([0.4, 0.0, 0.0, 0.0, 9.9], 4) == pytest.approx(0.1)


def test_whole_buffer():
    """n equal to the buffer length works without an IndexError (edge case)"""
    assert gyro_bias([0.01, 0.03], 2) == pytest.approx(0.02)


def test_single_sample():
    """n = 1 returns the first sample itself (edge case)"""
    assert gyro_bias([-0.015, 0.5, 0.5], 1) == pytest.approx(-0.015)
