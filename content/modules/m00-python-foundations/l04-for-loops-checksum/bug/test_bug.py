from solution import with_checksum


def test_update_rate_command():
    """PMTK220,1000 (1 Hz update rate) gets checksum 1F"""
    assert with_checksum("PMTK220,1000") == "$PMTK220,1000*1F\r\n"


def test_output_sentences_command():
    """PMTK314 (choose which sentences to output) gets checksum 28"""
    body = "PMTK314,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0"
    assert with_checksum(body) == "$" + body + "*28\r\n"


def test_gga_round_trip():
    """rebuilding the classic GGA sentence from its body gives *47"""
    body = "GPGGA,123519,4807.038,N,01131.000,E,1,08,0.9,545.4,M,46.9,M,,"
    assert with_checksum(body) == "$" + body + "*47\r\n"


def test_frame_shape():
    """the command starts with '$' and ends with '*', 2 hex digits, and \\r\\n"""
    out = with_checksum("PMTK251,115200")
    assert out.startswith("$PMTK251,115200*")
    assert out.endswith("\r\n")
    assert len(out) == len("$PMTK251,115200*1F\r\n")
