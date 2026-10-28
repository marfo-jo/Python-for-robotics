from solution import fix_status, is_usable

GPS = "$GPGGA,123519,4807.038,N,01131.000,E,1,08,0.9,545.4,M,46.9,M,,*47"
RTK = "$GNGGA,201530.00,4220.0101,N,07105.6600,W,4,12,0.6,10.2,M,-33.1,M,1.0,0000*52"
DGPS = "$GPGGA,142205.00,4220.1150,N,07105.4890,W,2,09,0.8,12.7,M,-33.1,M,3.2,0131*4F"
FLOAT = "$GNGGA,142206.00,4220.1152,N,07105.4888,W,5,11,0.7,12.9,M,-33.1,M,1.2,0000*57"
NO_FIX = "$GPGGA,,,,,,0,00,,,M,,M,,*66"
EMPTY_QUALITY = "$GPGGA,,,,,,,,,,,,,,*56"
DEAD_RECKONING = "$GPGGA,142209.00,4220.1156,N,07105.4885,W,6,05,1.9,13.0,M,-33.1,M,,*63"
FOUR_SATS = "$GPGGA,142208.00,4220.1155,N,07105.4886,W,1,04,2.1,13.0,M,-33.1,M,,*6F"
THREE_SATS = "$GPGGA,142207.00,4220.1153,N,07105.4887,W,1,03,4.5,13.1,M,-33.1,M,,*63"
NO_SATS_FIELD = "$GPGGA,142210.00,4220.1157,N,07105.4884,W,1,,1.9,13.0,M,-33.1,M,,*69"
RMC = "$GNRMC,220516,A,4221.123,N,07105.456,W,0.13,309.62,281026,,,A*7C"


def test_status_gps():
    """fix_status of a normal GPS fix (quality '1') is 'GPS'"""
    assert fix_status(GPS) == "GPS"


def test_status_rtk_fixed_other_talker():
    """fix_status works for $GNGGA too: quality '4' is 'RTK fixed'"""
    assert fix_status(RTK) == "RTK fixed"


def test_status_dgps_and_float():
    """fix_status: quality '2' is 'DGPS' and quality '5' is 'RTK float'"""
    assert fix_status(DGPS) == "DGPS"
    assert fix_status(FLOAT) == "RTK float"


def test_status_no_fix_serial_line():
    """fix_status of a no-fix line with \\r\\n on the end is 'no fix' (edge case)"""
    assert fix_status(NO_FIX + "\r\n") == "no fix"


def test_status_empty_quality():
    """fix_status is 'no data' when the quality field is empty (edge case)"""
    assert fix_status(EMPTY_QUALITY) == "no data"


def test_status_rejects_rmc():
    """fix_status of an RMC sentence is 'not GGA' (bad input)"""
    assert fix_status("  " + RMC + "\r\n") == "not GGA"


def test_status_rejects_missing_dollar():
    """fix_status is 'not GGA' when the '$' start marker is missing (bad input)"""
    assert fix_status("GPGGA,123519,4807.038,N,01131.000,E,1,08,0.9,545.4,M,46.9,M,,*47") == "not GGA"


def test_status_other_code():
    """fix_status of quality '6' (dead reckoning) is 'other'"""
    assert fix_status(DEAD_RECKONING) == "other"


def test_usable_normal():
    """is_usable: a GPS fix with 8 satellites is usable when 6 are required"""
    assert is_usable(GPS, 6) is True


def test_usable_boundary():
    """is_usable: exactly min_sats satellites ('04' with min 4) is enough (boundary)"""
    assert is_usable(FOUR_SATS + "\r\n", 4) is True


def test_usable_too_few_or_empty():
    """is_usable is False for 3 of 4 satellites, and doesn't crash on an empty satellite field (edge case)"""
    assert is_usable(THREE_SATS, 4) is False
    assert is_usable(NO_SATS_FIELD, 4) is False


def test_usable_rejects_non_fixes():
    """is_usable is False for no fix, dead reckoning, and non-GGA sentences (bad input)"""
    assert is_usable(NO_FIX, 0) is False
    assert is_usable(DEAD_RECKONING, 4) is False
    assert is_usable(RMC, 0) is False
