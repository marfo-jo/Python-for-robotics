import pytest

from solution import gga_fixes, parse_latlon, path_length, to_local_xy, track_length

P1 = "$GPGGA,153020.00,4220.0200,N,07105.6400,W,1,09,0.9,10.3,M,-33.1,M,,*62"
P2 = "$GPGGA,153040.00,4220.0400,N,07105.6400,W,1,09,0.9,10.3,M,-33.1,M,,*62"
P3 = "$GPGGA,153100.00,4220.0400,N,07105.6100,W,1,10,0.8,10.4,M,-33.1,M,,*6C"
NO_FIX = "$GPGGA,153015.00,,,,,0,00,99.9,,M,,M,,*5C"
RMC = "$GPRMC,153020.00,A,4220.0301,N,07105.6100,W,5.20,54.70,281026,,,A*75"


def test_stage1_keeps_fixes():
    """stage 1: gga_fixes keeps GGA fixes, stripped, in order"""
    assert gga_fixes([P1 + "\r\n", "  " + P2]) == [P1, P2]


def test_stage1_drops_no_fix():
    """stage 1: gga_fixes drops a no-fix sentence (fix quality '0')"""
    assert gga_fixes([P1, NO_FIX, P2]) == [P1, P2]


def test_stage1_drops_other_lines():
    """stage 1: gga_fixes drops blank lines and other sentence types (RMC)"""
    assert gga_fixes(["", RMC, "   ", P3]) == [P3]


def test_stage2_parse_latlon():
    """stage 2: parse_latlon gives signed decimal degrees (north +, west -)"""
    lat, lon = parse_latlon(P1)
    assert lat == pytest.approx(42.3336667, abs=1e-6)
    assert lon == pytest.approx(-71.094, abs=1e-6)


def test_stage3_origin_is_zero():
    """stage 3: the origin itself maps to (0, 0)"""
    x, y = to_local_xy(42.0, -71.0, 42.0, -71.0)
    assert x == pytest.approx(0.0, abs=1e-9)
    assert y == pytest.approx(0.0, abs=1e-9)


def test_stage3_north():
    """stage 3: 0.001° north of the origin is about 111.19 m in y, 0 in x"""
    x, y = to_local_xy(42.001, -71.0, 42.0, -71.0)
    assert x == pytest.approx(0.0, abs=1e-6)
    assert y == pytest.approx(111.195, abs=0.01)


def test_stage3_east_shrinks_with_latitude():
    """stage 3: 0.001° east at latitude 42° is about 82.63 m, cos(42°) of the north-south distance"""
    x, y = to_local_xy(42.0, -70.999, 42.0, -71.0)
    assert x == pytest.approx(82.634, abs=0.01)
    assert y == pytest.approx(0.0, abs=1e-6)


def test_stage4_two_segments():
    """stage 4: path (0,0) → (3,4) → (6,8) is 10 m long (two 3-4-5 segments)"""
    assert path_length([(0, 0), (3, 4), (6, 8)]) == pytest.approx(10.0)


def test_stage4_one_segment():
    """stage 4: a path of two points is one segment: (0,0) → (3,4) is 5 m (edge case)"""
    assert path_length([(0, 0), (3, 4)]) == pytest.approx(5.0)


def test_stage4_too_few_points():
    """stage 4: zero or one point is a path of length 0 (edge case)"""
    assert path_length([]) == 0.0
    assert path_length([(5, 5)]) == 0.0


def test_end_to_end_messy_log():
    """whole pipeline: a messy log (no-fix, RMC, blank, \\r\\n) gives about 78.2 m"""
    log = [NO_FIX + "\r\n", P1 + "\r\n", RMC + "\r\n", "\r\n", P2 + "\r\n", NO_FIX + "\r\n", P3 + "\r\n"]
    assert track_length(log) == pytest.approx(78.16, abs=0.05)
