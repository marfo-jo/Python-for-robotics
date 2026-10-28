import pytest

from solution import parse_fixes, parse_gga

G1 = "$GPGGA,153012.00,4220.0101,N,07105.6600,W,1,09,0.9,10.2,M,-33.1,M,,*62"
G2 = "$GPGGA,153013.00,4220.0105,N,07105.6592,W,1,09,0.9,10.4,M,-33.1,M,,*69"
GN_DGPS = "$GNGGA,153016.00,4220.0114,N,07105.6577,W,2,11,0.7,10.6,M,-33.1,M,1.0,0000*50"
RMC = "$GPRMC,153012.00,A,4220.0101,N,07105.6600,W,0.52,54.70,281026,,,A*71"
NO_FIX = "$GPGGA,153015.00,,,,,0,00,99.9,,M,,M,,*5C"
BAD_SUM = "$GPGGA,153014.00,4220.0110,N,07105.6584,W,1,10,0.8,10.5,M,-33.1,M,,*66"
SHORT = "$GPGGA,153012.00,4220.0101,N*34"          # valid checksum, but cut short
SYDNEY = "$GPGGA,083000.00,3351.4070,S,15112.8240,E,1,08,1.0,25.0,M,22.1,M,,*4A"
BAD_SATS = "$GPGGA,153012.00,4220.0101,N,07105.6600,W,1,x9,0.9,10.2,M,-33.1,M,,*2A"


def test_parses_valid_fix():
    """a valid $GPGGA gives time, quality, sats, hdop, and alt with the right types"""
    assert parse_gga(G1) == {"time": "153012.00", "quality": 1, "sats": 9, "hdop": 0.9, "alt": 10.2}


def test_messy_but_valid_input():
    """accepts a $GNGGA talker, lowercase hex, spaces, and a trailing \\r\\n (edge case)"""
    fix = parse_gga(GN_DGPS + "\r\n")
    assert fix["quality"] == 2
    assert fix["sats"] == 11
    fix = parse_gga("  " + SYDNEY[:-2] + "4a\r\n")
    assert fix["sats"] == 8


def test_junk_and_truncated_raise():
    """a boot banner and a power-loss truncated line both raise ValueError"""
    with pytest.raises(ValueError):
        parse_gga("u-blox NEO-M8N ROM 2.01")
    with pytest.raises(ValueError):
        parse_gga("$GPGGA,153015.00,4220.01")


def test_bad_checksum_message():
    """a corrupted sentence raises ValueError and the message mentions 'checksum'"""
    with pytest.raises(ValueError, match="checksum"):
        parse_gga(BAD_SUM)


def test_other_sentence_type():
    """a valid $GPRMC raises ValueError whose message mentions 'GGA'"""
    with pytest.raises(ValueError, match="GGA"):
        parse_gga(RMC)


def test_no_fix_message():
    """fix quality 0 raises ValueError with the message 'no fix'"""
    with pytest.raises(ValueError, match="no fix"):
        parse_gga(NO_FIX)


def test_too_few_fields_is_valueerror():
    """a short sentence with a valid checksum raises ValueError, not IndexError"""
    with pytest.raises(ValueError, match="too few fields"):
        parse_gga(SHORT)


def test_non_numeric_field():
    """a satellites field of 'x9' raises ValueError (bad input, not a crash of another type)"""
    with pytest.raises(ValueError):
        parse_gga(BAD_SATS)


def test_parse_fixes_skips_and_records():
    """parse_fixes keeps the good fixes and records (line_number, message) for bad lines"""
    fixes, errors = parse_fixes([G1, "garbage", G2, BAD_SUM])
    assert [f["time"] for f in fixes] == ["153012.00", "153013.00"]
    assert [number for number, message in errors] == [2, 4]
    assert all(isinstance(message, str) and message for number, message in errors)


def test_parse_fixes_line_numbers_count_blank_lines():
    """line numbers start at 1 and blank lines are skipped but still counted (edge case)"""
    fixes, errors = parse_fixes(["", G1, "   ", NO_FIX, "\r\n", SHORT])
    assert len(fixes) == 1
    assert errors[0][0] == 4 and "no fix" in errors[0][1]
    assert errors[1][0] == 6 and "too few fields" in errors[1][1]


def test_parse_fixes_empty_input():
    """no lines, or only blank lines, gives ([], []) (edge case)"""
    assert parse_fixes([]) == ([], [])
    assert parse_fixes(["", "  ", "\n"]) == ([], [])


def test_parse_fixes_does_not_hide_bugs():
    """only ValueError is caught: a None in the list (a caller's bug) must still crash"""
    with pytest.raises((AttributeError, TypeError)):
        parse_fixes([G1, None])
