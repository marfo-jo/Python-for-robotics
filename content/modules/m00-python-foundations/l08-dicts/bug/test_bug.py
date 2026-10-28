from solution import handle

GGA_9 = "$GPGGA,152305.00,4220.1234,N,07105.5678,W,1,09,1.1,12.3,M,-33.1,M,,*64"
GNGGA = "$GNGGA,201530.00,4220.0101,N,07105.6600,W,4,12,0.6,10.2,M,-33.1,M,1.0,0000*52"
RMC = "$GPRMC,152305.00,A,4220.1234,N,07105.5678,W,0.05,87.30,281026,,,A*75"
GSV = "$GPGSV,3,1,11,03,03,111,00,04,15,270,00,06,01,010,00,13,06,292,00*74"


def test_gga_is_handled():
    """a $GPGGA sentence reaches the GGA handler"""
    assert handle(GGA_9) == {"type": "GGA", "satellites": 9}


def test_rmc_is_handled():
    """a $GPRMC sentence reaches the RMC handler"""
    assert handle(RMC) == {"type": "RMC", "status": "A"}


def test_other_talker():
    """a $GNGGA line with a trailing \\r\\n also reaches the GGA handler"""
    assert handle(GNGGA + "\r\n") == {"type": "GGA", "satellites": 12}


def test_unknown_type_ignored():
    """a type with no handler (GSV) still returns None"""
    assert handle(GSV) is None
