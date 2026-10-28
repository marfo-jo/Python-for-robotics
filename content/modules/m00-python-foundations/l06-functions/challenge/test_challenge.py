from solution import is_gga, parse_gga

GGA_9 = "$GPGGA,152305.00,4220.1234,N,07105.5678,W,1,09,1.1,12.3,M,-33.1,M,,*64"
GGA_3 = "$GPGGA,152306.00,4220.1240,N,07105.5690,W,1,03,2.8,13.0,M,-33.1,M,,*60"
GNGGA_RTK = "$GNGGA,201530.00,4220.0101,N,07105.6600,W,4,12,0.6,10.2,M,-33.1,M,1.0,0000*52"
BELOW_SEA = "$GPGGA,101010.00,3627.6000,N,11651.3000,W,1,06,1.3,-85.2,M,-30.0,M,,*40"
RMC = "$GPRMC,152305.00,A,4220.1234,N,07105.5678,W,0.05,87.30,281026,,,A*75"
NO_FIX = "$GPGGA,,,,,,0,00,,,M,,M,,*66"
CUT_OFF = "$GPGGA,152310.00,4220.12"


def test_is_gga_basic():
    """is_gga returns True for a $GPGGA sentence"""
    assert is_gga(GGA_9) is True


def test_is_gga_any_talker_and_whitespace():
    """is_gga accepts other talkers ($GNGGA) and a trailing \\r\\n (edge case)"""
    assert is_gga("  " + GNGGA_RTK + "\r\n") is True


def test_is_gga_rejects_non_gga():
    """is_gga returns False for RMC, a missing '$', an empty string, and a cut-off line (bad input)"""
    assert is_gga(RMC) is False
    assert is_gga(GGA_9[1:]) is False
    assert is_gga("") is False
    assert is_gga(CUT_OFF) is False


def test_parse_returns_a_value():
    """parse_gga RETURNS its result (printing it instead gives the caller None)"""
    assert parse_gga(GGA_9) is not None


def test_parse_values():
    """parse_gga gives [time, quality, satellites, altitude] for a normal fix"""
    assert parse_gga(GGA_9) == ["152305.00", 1, 9, 12.3]


def test_parse_types():
    """time is text; quality and satellites are ints; altitude is a float"""
    time, quality, sats, alt = parse_gga(GNGGA_RTK)
    assert isinstance(time, str)
    assert isinstance(quality, int) and isinstance(sats, int)
    assert isinstance(alt, float)


def test_parse_other_talker_negative_altitude():
    """parse_gga handles $GNGGA with \\r\\n, and an altitude below sea level (edge case)"""
    assert parse_gga(GNGGA_RTK + "\r\n") == ["201530.00", 4, 12, 10.2]
    assert parse_gga(BELOW_SEA) == ["101010.00", 1, 6, -85.2]


def test_parse_not_gga():
    """parse_gga returns None for an RMC sentence"""
    assert parse_gga(RMC) is None


def test_parse_no_fix():
    """parse_gga returns None for a no-fix sentence with empty fields, without crashing (edge case)"""
    assert parse_gga(NO_FIX) is None


def test_parse_cut_off():
    """parse_gga returns None for a cut-off line instead of raising IndexError (bad input)"""
    assert parse_gga(CUT_OFF) is None


def test_min_sats_default():
    """with the default min_sats=4, a 3-satellite fix is rejected"""
    assert parse_gga(GGA_3) is None


def test_min_sats_argument():
    """passing min_sats changes the threshold both ways"""
    assert parse_gga(GGA_3, min_sats=3) == ["152306.00", 1, 3, 13.0]
    assert parse_gga(GGA_9, 10) is None
