from solution import count_types, gga_to_dict

GGA_9 = "$GPGGA,152305.00,4220.1234,N,07105.5678,W,1,09,1.1,12.3,M,-33.1,M,,*64"
GNGGA = "$GNGGA,201530.00,4220.0101,N,07105.6600,W,4,12,0.6,10.2,M,-33.1,M,1.0,0000*52"
RMC = "$GPRMC,152305.00,A,4220.1234,N,07105.5678,W,0.05,87.30,281026,,,A*75"
GSV = "$GPGSV,3,1,11,03,03,111,00,04,15,270,00,06,01,010,00,13,06,292,00*74"
VTG = "$GPVTG,309.62,T,,M,0.13,N,0.2,K,A*03"
NO_FIX = "$GPGGA,,,,,,0,00,,,M,,M,,*66"
ALL_EMPTY = "$GPGGA,,,,,,0,,,,,,,,*66"
CUT_OFF = "$GPGGA,152310.00,4220.12"


def test_gga_values():
    """gga_to_dict maps each field name to its value for a normal fix"""
    assert gga_to_dict(GGA_9) == {"time": "152305.00", "quality": 1, "satellites": 9,
                                  "hdop": 1.1, "altitude": 12.3}


def test_gga_types():
    """the result is a dict; quality and satellites are ints, hdop and altitude floats"""
    fix = gga_to_dict(GNGGA)
    assert isinstance(fix, dict)
    assert isinstance(fix["quality"], int) and isinstance(fix["satellites"], int)
    assert isinstance(fix["hdop"], float) and isinstance(fix["altitude"], float)


def test_gga_other_talker_whitespace():
    """gga_to_dict handles $GNGGA with stray spaces and \\r\\n (edge case)"""
    assert gga_to_dict("  " + GNGGA + "\r\n") == {"time": "201530.00", "quality": 4, "satellites": 12,
                                                 "hdop": 0.6, "altitude": 10.2}


def test_gga_no_fix_leaves_keys_out():
    """a no-fix sentence keeps only its non-empty fields, without crashing (edge case)"""
    assert gga_to_dict(NO_FIX) == {"quality": 0, "satellites": 0}


def test_gga_all_empty():
    """when only the quality field has a value, only 'quality' is in the dict (edge case)"""
    assert gga_to_dict(ALL_EMPTY) == {"quality": 0}


def test_gga_bad_input():
    """gga_to_dict returns None for an RMC sentence and for a cut-off line (bad input)"""
    assert gga_to_dict(RMC) is None
    assert gga_to_dict(CUT_OFF) is None


def test_count_basic():
    """count_types counts each type, and types that never appear aren't keys"""
    counts = count_types([GGA_9, RMC, GGA_9, GSV])
    assert counts == {"GGA": 2, "RMC": 1, "GSV": 1}
    assert "VTG" not in counts


def test_count_talker_independent():
    """$GPGGA and $GNGGA both count as 'GGA'"""
    assert count_types([GGA_9, GNGGA, VTG]) == {"GGA": 2, "VTG": 1}


def test_count_empty_log():
    """an empty list gives an empty dict (edge case)"""
    assert count_types([]) == {}


def test_count_skips_blank_and_garbage():
    """blank lines and partial lines without a '$' are skipped (bad input)"""
    log = ["", "   \r\n", "GA,152305.00,4220.1234,N*1F", RMC, "\n"]
    assert count_types(log) == {"RMC": 1}


def test_count_serial_whitespace():
    """lines with leading spaces and a trailing \\r\\n still count (edge case)"""
    assert count_types(["  " + GGA_9 + "\r\n", RMC + "\r\n"]) == {"GGA": 1, "RMC": 1}
