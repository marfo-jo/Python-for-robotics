from solution import checksum_text, sentence_type, talker_id

GGA = "$GPGGA,123519,4807.038,N,01131.000,E,1,08,0.9,545.4,M,46.9,M,,*47"
RMC = "$GNRMC,220516,A,4221.123,N,07105.456,W,0.13,309.62,281026,,,A*7c"


def test_talker_basic():
    """talker_id of a clean $GPGGA sentence is 'GP'"""
    assert talker_id(GGA) == "GP"


def test_talker_other_constellation():
    """talker_id works for other talkers ($GNRMC → 'GN')"""
    assert talker_id(RMC) == "GN"


def test_talker_with_whitespace():
    """talker_id ignores leading spaces and a trailing \\r\\n (edge case)"""
    assert talker_id("  " + GGA + "\r\n") == "GP"


def test_type_basic():
    """sentence_type of $GPGGA is 'GGA'"""
    assert sentence_type(GGA) == "GGA"


def test_type_rmc_with_whitespace():
    """sentence_type of a messy $GNRMC line is 'RMC' (edge case)"""
    assert sentence_type(" \t" + RMC + " \r\n") == "RMC"


def test_checksum_basic():
    """checksum_text of a clean sentence is '47'"""
    assert checksum_text(GGA) == "47"


def test_checksum_serial_line():
    """checksum_text ignores the trailing \\r\\n from a serial read (edge case)"""
    assert checksum_text(GGA + "\r\n") == "47"


def test_checksum_uppercases_hex():
    """checksum_text normalizes lowercase hex: '*7c' → '7C' (edge case)"""
    assert checksum_text(RMC) == "7C"


def test_checksum_short_sentence():
    """checksum_text works when the sentence is short and has empty fields (edge case)"""
    assert checksum_text("$GPGGA,,,,,,0,,,,,,,,*66\n") == "66"


def test_returns_strings():
    """all three functions return strings, not lists or numbers"""
    for value in (talker_id(GGA), sentence_type(GGA), checksum_text(GGA)):
        assert isinstance(value, str)
