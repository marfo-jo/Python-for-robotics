from solution import checksum_ok, xor_checksum

GGA = "$GPGGA,123519,4807.038,N,01131.000,E,1,08,0.9,545.4,M,46.9,M,,*47"
GGA_BODY = "GPGGA,123519,4807.038,N,01131.000,E,1,08,0.9,545.4,M,46.9,M,,"
VTG = "$GPVTG,309.62,T,,M,0.13,N,0.2,K,A*03"
VTG_BODY = "GPVTG,309.62,T,,M,0.13,N,0.2,K,A"
RMC_LOWER = "$GNRMC,220516,A,4221.123,N,07105.456,W,0.13,309.62,281026,,,A*7c"
RMC_BODY = "GNRMC,220516,A,4221.123,N,07105.456,W,0.13,309.62,281026,,,A"


def test_xor_gga_body():
    """xor_checksum of the classic GGA body is '47'"""
    assert xor_checksum(GGA_BODY) == "47"


def test_xor_tiny_bodies():
    """xor_checksum of 'A' is '41', and of an empty body is '00' (edge case)"""
    assert xor_checksum("A") == "41"
    assert xor_checksum("") == "00"


def test_xor_zero_padded():
    """xor_checksum pads small results to 2 digits: '03', not '3' (edge case)"""
    assert xor_checksum(VTG_BODY) == "03"


def test_xor_uppercase_hex():
    """xor_checksum returns uppercase hex: '7C', not '7c' or '0x7c'"""
    assert xor_checksum(RMC_BODY) == "7C"


def test_ok_valid():
    """checksum_ok is True for a valid sentence"""
    assert checksum_ok(GGA) is True
    assert checksum_ok(VTG) is True


def test_ok_serial_line():
    """checksum_ok ignores spaces and a trailing \\r\\n from a serial read (edge case)"""
    assert checksum_ok("  " + GGA + "\r\n") is True


def test_ok_lowercase_hex():
    """checksum_ok accepts lowercase hex like '*7c' (edge case)"""
    assert checksum_ok(RMC_LOWER + "\r\n") is True


def test_ok_corrupted_character():
    """checksum_ok is False when one character was corrupted in transit"""
    assert checksum_ok(GGA.replace("4807.038", "4807.039")) is False


def test_ok_wrong_checksum():
    """checksum_ok is False for a wrong or truncated checksum ('*48', '*4')"""
    assert checksum_ok(GGA[:-2] + "48") is False
    assert checksum_ok(GGA[:-1]) is False


def test_ok_missing_star():
    """checksum_ok is False (no crash) when the '*' is missing (bad input)"""
    assert checksum_ok("$GPGGA,123519,4807.038,N,01131.000,E,1,08,0.9,545.4,M,46.9,M,,47") is False


def test_ok_missing_dollar_or_empty():
    """checksum_ok is False for a line missing its '$', and for an empty line (bad input)"""
    assert checksum_ok(GGA[1:]) is False
    assert checksum_ok("") is False
    assert checksum_ok("\r\n") is False
