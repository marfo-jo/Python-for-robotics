import pytest

from solution import speeds, utc_seconds


def test_within_one_minute():
    """steady 1.5 m/s within the same minute gives [1.5, 1.5]"""
    samples = [("153057.00", 0.0), ("153058.00", 1.5), ("153059.00", 3.0)]
    assert speeds(samples) == pytest.approx([1.5, 1.5])


def test_across_a_minute_boundary():
    """15:30:59 → 15:31:00 is 1 second, so 1.5 m gives 1.5 m/s"""
    samples = [("153059.00", 3.0), ("153100.00", 4.5)]
    assert speeds(samples) == pytest.approx([1.5])


def test_across_an_hour_boundary():
    """15:59:59.5 → 16:00:00.5 is 1 second, so 2 m gives 2 m/s (edge case)"""
    samples = [("155959.50", 0.0), ("160000.50", 2.0)]
    assert speeds(samples) == pytest.approx([2.0])


def test_utc_seconds():
    """'153012.25' is 15 h 30 min 12.25 s = 55812.25 seconds since midnight"""
    assert utc_seconds("153012.25") == pytest.approx(55812.25)
