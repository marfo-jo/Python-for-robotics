from solution import clamped


def test_clamps_spike():
    """an 87.4 m spike is clamped to the 20.0 m ceiling"""
    assert clamped([12.3, 13.0, 87.4, 12.9], 20.0) == [12.3, 13.0, 20.0, 12.9]


def test_raw_log_untouched():
    """the raw altitude log still has its spike after clamping"""
    raw = [12.3, 13.0, 87.4, 12.9]
    clamped(raw, 20.0)
    assert raw == [12.3, 13.0, 87.4, 12.9]


def test_returns_a_new_list():
    """the result is a separate list, not a second name for the raw log"""
    raw = [12.3, 13.0, 12.9]
    result = clamped(raw, 20.0)
    assert result == [12.3, 13.0, 12.9]
    assert result is not raw


def test_empty_log():
    """an empty log gives an empty list (edge case)"""
    assert clamped([], 20.0) == []
