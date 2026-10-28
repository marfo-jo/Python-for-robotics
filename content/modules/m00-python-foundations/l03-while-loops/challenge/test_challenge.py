from solution import first_fix, settled_index

FIX_A = "$GPGGA,142208.00,4220.1155,N,07105.4886,W,1,04,2.1,13.0,M,-33.1,M,,*6F"
FIX_B = "$GNGGA,201530.00,4220.0101,N,07105.6600,W,4,12,0.6,10.2,M,-33.1,M,1.0,0000*52"
NO_FIX = "$GPGGA,,,,,,0,,,,,,,,*66"
EMPTY_QUALITY = "$GPGGA,,,,,,,,,,,,,,*56"
RMC = "$GNRMC,220516,A,4221.123,N,07105.456,W,0.13,309.62,281026,,,A*7C"
GSV = "$GPGSV,3,1,11,03,03,111,00,04,15,270,00,06,01,010,00,13,06,292,00*74"
TRUNCATED = "$GPGGA,1422"


def test_fix_on_first_line():
    """first_fix returns the very first line when it's already a fix (stripped)"""
    assert first_fix([FIX_A + "\r\n", FIX_B], 5) == FIX_A


def test_skips_no_fix_and_other_types():
    """first_fix skips no-fix GGA, empty-quality GGA, RMC, and GSV lines"""
    lines = [NO_FIX, RMC, EMPTY_QUALITY, GSV, FIX_B + "\r\n", FIX_A]
    assert first_fix(lines, 10) == FIX_B


def test_skips_blank_and_truncated():
    """first_fix survives blank lines and a truncated sentence from power-up (edge case)"""
    lines = ["", "\r\n", TRUNCATED, "  " + FIX_A + "  \r\n"]
    assert first_fix(lines, 10) == FIX_A


def test_no_fix_at_all():
    """first_fix returns '' when no line has a fix, even if max_tries is larger than the list (edge case)"""
    assert first_fix([NO_FIX, RMC, NO_FIX], 10) == ""


def test_gives_up_after_max_tries():
    """first_fix gives up after max_tries reads: a fix on read 4 is too late for max_tries=3"""
    assert first_fix([NO_FIX, NO_FIX, RMC, FIX_A], 3) == ""


def test_max_tries_boundary():
    """first_fix finds a fix on exactly the last allowed read (boundary)"""
    assert first_fix([NO_FIX, NO_FIX, RMC, FIX_A], 4) == FIX_A


def test_empty_input():
    """first_fix returns '' for an empty list or max_tries = 0 (edge case)"""
    assert first_fix([], 5) == ""
    assert first_fix([FIX_A], 0) == ""


def test_settled_normal():
    """settled_index finds where 3 readings in a row are below 1.0"""
    assert settled_index([5.0, 3.2, 0.9, 0.4, 0.3, 0.2], 1.0, 3) == 4


def test_settled_run_resets():
    """settled_index: a reading back above the threshold resets the count"""
    assert settled_index([0.5, 0.4, 2.0, 0.3, 0.2, 0.1], 1.0, 3) == 5


def test_never_settles():
    """settled_index returns -1 if it never settles, or the list is empty (edge case)"""
    assert settled_index([3.0, 0.5, 2.0, 0.4, 1.5], 1.0, 2) == -1
    assert settled_index([], 1.0, 1) == -1


def test_threshold_is_strict():
    """settled_index: a reading exactly AT the threshold is not below it (boundary)"""
    assert settled_index([1.0, 1.0, 0.99], 1.0, 1) == 2
