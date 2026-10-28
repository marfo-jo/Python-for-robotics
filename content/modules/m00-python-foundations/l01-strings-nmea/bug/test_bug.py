from solution import fix_quality


def test_gps_fix():
    """a normal GPS fix returns '1'"""
    assert fix_quality("$GPGGA,123519,4807.038,N,01131.000,E,1,08,0.9,545.4,M,46.9,M,,*47") == "1"


def test_rtk_fix():
    """an RTK fixed solution returns '4'"""
    assert fix_quality("$GNGGA,201530.00,4220.0101,N,07105.6600,W,4,12,0.6,10.2,M,-33.1,M,1.0,0000*52") == "4"


def test_no_fix_empty_fields():
    """a no-fix sentence with empty position fields returns '0' (edge case)"""
    assert fix_quality("$GPGGA,,,,,,0,00,,,M,,M,,*66\r\n") == "0"
