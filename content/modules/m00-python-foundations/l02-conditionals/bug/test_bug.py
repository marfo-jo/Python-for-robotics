from solution import battery_state


def test_ok():
    """a healthy pack (12.3 V) is 'OK'"""
    assert battery_state(12.3) == "OK"


def test_low():
    """10.9 V is 'LOW'"""
    assert battery_state(10.9) == "LOW"


def test_critical():
    """9.8 V is 'CRITICAL' (the robot must return to dock)"""
    assert battery_state(9.8) == "CRITICAL"


def test_boundaries():
    """exactly 11.1 V is 'OK' and exactly 10.5 V is 'LOW' (boundary)"""
    assert battery_state(11.1) == "OK"
    assert battery_state(10.5) == "LOW"
