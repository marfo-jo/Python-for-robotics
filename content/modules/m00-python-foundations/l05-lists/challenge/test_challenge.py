from solution import last_n, satellite_counts

GGA_9 = "$GPGGA,152305.00,4220.1234,N,07105.5678,W,1,09,1.1,12.3,M,-33.1,M,,*64"
GGA_3 = "$GPGGA,152306.00,4220.1240,N,07105.5690,W,1,03,2.8,13.0,M,-33.1,M,,*60"
GNGGA_12 = "$GNGGA,201530.00,4220.0101,N,07105.6600,W,4,12,0.6,10.2,M,-33.1,M,1.0,0000*52"
RMC = "$GNRMC,220516,A,4221.123,N,07105.456,W,0.13,309.62,281026,,,A*7C"
GSV = "$GPGSV,3,1,11,03,03,111,00,04,15,270,00,06,01,010,00,13,06,292,00*74"
VTG = "$GPVTG,309.62,T,,M,0.13,N,0.2,K,A*03"
NO_FIX_00 = "$GPGGA,,,,,,0,00,,,M,,M,,*66"
NO_FIX_EMPTY = "$GPGGA,,,,,,0,,,,,,,,*66"
CUT_OFF = "$GPGGA,152310.00,4220.12"


def test_counts_basic():
    """satellite_counts collects one count per GGA sentence, in order"""
    assert satellite_counts([GGA_9, GGA_3, GNGGA_12]) == [9, 3, 12]


def test_counts_are_ints():
    """the counts are numbers (9), not text ('09')"""
    for value in satellite_counts([GGA_9, GNGGA_12]):
        assert isinstance(value, int)


def test_skips_other_sentence_types():
    """RMC, GSV, and VTG sentences are skipped"""
    assert satellite_counts([RMC, GGA_9, GSV, VTG]) == [9]


def test_no_fix_zero_satellites():
    """a no-fix sentence that reports '00' satellites counts as 0 (edge case)"""
    assert satellite_counts([NO_FIX_00]) == [0]


def test_skips_empty_satellite_field():
    """a sentence whose satellites field is empty is skipped (edge case)"""
    assert satellite_counts([NO_FIX_EMPTY, GGA_3]) == [3]


def test_skips_cut_off_sentence():
    """a sentence cut off mid-transmission is skipped, not an IndexError (bad input)"""
    assert satellite_counts([GGA_9, CUT_OFF, GGA_3]) == [9, 3]


def test_serial_whitespace():
    """lines with stray spaces and a trailing \\r\\n still count (edge case)"""
    assert satellite_counts(["  " + GGA_9 + "\r\n", GNGGA_12 + "\n"]) == [9, 12]


def test_empty_log():
    """an empty list of sentences gives an empty list (edge case)"""
    assert satellite_counts([]) == []


def test_last_n_basic():
    """last_n keeps the newest 3 of 5 readings"""
    assert last_n([12.3, 13.0, 12.8, 12.9, 13.1], 3) == [12.8, 12.9, 13.1]


def test_last_n_fewer_than_n():
    """last_n returns every reading when there are fewer than n (edge case)"""
    assert last_n([12.3, 13.0], 5) == [12.3, 13.0]


def test_last_n_zero():
    """last_n(readings, 0) is an empty list (edge case)"""
    assert last_n([12.3, 13.0, 12.8], 0) == []


def test_last_n_does_not_touch_input():
    """last_n leaves the original list alone, and its result is a separate list"""
    readings = [12.3, 13.0, 12.8, 12.9, 13.1]
    result = last_n(readings, 2)
    assert readings == [12.3, 13.0, 12.8, 12.9, 13.1]
    result.append(0.0)
    assert readings == [12.3, 13.0, 12.8, 12.9, 13.1]
