from solution import good_enough, satellites

GGA_9 = "$GPGGA,152305.00,4220.1234,N,07105.5678,W,1,09,1.1,12.3,M,-33.1,M,,*64"
GGA_3 = "$GPGGA,152306.00,4220.1240,N,07105.5690,W,1,03,2.8,13.0,M,-33.1,M,,*60"


def test_satellites_value():
    """satellites() hands back 9 for a 9-satellite fix"""
    assert satellites(GGA_9) == 9


def test_good_fix_passes():
    """a 9-satellite fix passes the default filter"""
    assert good_enough(GGA_9) is True


def test_weak_fix_rejected():
    """a 3-satellite fix is rejected by the default filter"""
    assert good_enough(GGA_3) is False


def test_custom_minimum():
    """a 3-satellite fix passes when minimum=3"""
    assert good_enough(GGA_3, minimum=3) is True
