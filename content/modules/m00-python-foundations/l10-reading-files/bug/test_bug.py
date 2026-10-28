from solution import log_summary

G1 = "$GPGGA,153012.00,4220.0101,N,07105.6600,W,1,09,0.9,10.2,M,-33.1,M,,*62"
G2 = "$GPGGA,153013.00,4220.0105,N,07105.6592,W,1,09,0.9,10.4,M,-33.1,M,,*69"
RMC = "$GPRMC,153012.00,A,4220.0101,N,07105.6600,W,0.52,54.70,281026,,,A*71"


def test_counts_gga(tmp_path):
    """a log with 2 GGA and 1 RMC sentence gives (3, 2)"""
    path = tmp_path / "log.txt"
    path.write_text(G1 + "\n" + RMC + "\n" + G2 + "\n", encoding="utf-8")
    assert log_summary(str(path)) == (3, 2)


def test_blank_lines_not_counted(tmp_path):
    """blank lines are not counted: (2, 1)"""
    path = tmp_path / "log.txt"
    path.write_text("\n" + G1 + "\n\n" + RMC + "\n\n", encoding="utf-8")
    assert log_summary(str(path)) == (2, 1)


def test_gnss_talker(tmp_path):
    """GGA from a multi-constellation receiver ($GNGGA) counts too"""
    path = tmp_path / "log.txt"
    path.write_text("$GNGGA,153016.00,4220.0114,N,07105.6577,W,2,11,0.7,10.6,M,-33.1,M,1.0,0000*50\n", encoding="utf-8")
    assert log_summary(str(path)) == (1, 1)
