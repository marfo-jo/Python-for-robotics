"""Hidden tests for the Module 0 project: NMEA log analyzer.

The log file gps_log.txt is placed in the current folder before these run.
"""
import pytest

from solution import analyze_log, classify_line, format_summary, main

LOG = "gps_log.txt"
GGA = "$GPGGA,123519,4807.038,N,01131.000,E,1,08,0.9,545.4,M,46.9,M,,*47"
RMC_LOWER_HEX = "$GNRMC,220516,A,4221.123,N,07105.456,W,0.13,309.62,281026,,,A*7c"


def test_classify_valid_sentences():
    """classify_line says 'valid' for good sentences, including lowercase hex like '*7c'"""
    assert classify_line(GGA) == "valid"
    assert classify_line(RMC_LOWER_HEX) == "valid"


def test_classify_strips_serial_line_ending():
    """classify_line ignores spaces and the trailing \\r\\n from a serial read (edge case)"""
    assert classify_line("  " + GGA + "\r\n") == "valid"
    assert classify_line(GGA + "\n") == "valid"


def test_classify_bad_checksum():
    """classify_line says 'bad_checksum' when one character was corrupted in transit"""
    corrupted = GGA.replace(",08,", ",09,")
    assert classify_line(corrupted) == "bad_checksum"
    assert classify_line(corrupted + "\r\n") == "bad_checksum"


def test_classify_blank_lines():
    """classify_line says 'blank' (not 'malformed') for empty and whitespace-only lines"""
    assert classify_line("") == "blank"
    assert classify_line("\n") == "blank"
    assert classify_line("   \r\n") == "blank"


def test_classify_malformed_lines():
    """classify_line says 'malformed' for junk, truncated lines, and bad checksum fields"""
    assert classify_line("9.0,M,-33.1,M,,*5B") == "malformed"          # no '$'
    assert classify_line("$GPGGA,140026.00,4220.4951") == "malformed"  # truncated: no '*'
    assert classify_line("$GPGGA,123519,,,,,0,,,,,,,,*4") == "malformed"   # one hex digit
    assert classify_line("$GPGGA,123519,,,,,0,,,,,,,,*ZZ") == "malformed"  # not hex
    assert classify_line("$GPGGA,1*2*47") == "malformed"               # two '*'


def test_log_line_counts():
    """analyze_log counts every line of gps_log.txt into exactly one bucket"""
    s = analyze_log(LOG)
    assert s["total_lines"] == 65
    assert s["valid"] == 59
    assert s["bad_checksum"] == 3
    assert s["malformed"] == 2
    assert s["blank"] == 1


def test_log_by_type():
    """analyze_log counts valid sentences by type, whatever the talker (GP, GN)"""
    s = analyze_log(LOG)
    assert s["by_type"] == {"GGA": 27, "RMC": 28, "GSA": 3, "VTG": 1}


def test_log_fix_quality_counts():
    """analyze_log counts valid GGA fixes by quality, with int keys (0 = no fix)"""
    s = analyze_log(LOG)
    assert s["fix_quality_counts"] == {0: 5, 1: 16, 2: 6}
    assert s["fix_rate_pct"] == pytest.approx(81.4815, abs=0.01)


def test_log_max_satellites_ignores_corrupted_lines():
    """max_satellites uses only valid GGA sentences (corrupted lines claim 12 and 13)"""
    s = analyze_log(LOG)
    assert s["max_satellites"] == 11


def test_log_first_and_last_fix():
    """first/last fix times skip no-fix GGAs and the corrupted GGA at the end of the log"""
    s = analyze_log(LOG)
    assert s["first_fix_utc"] == "140000.00"
    assert s["last_fix_utc"] == "140024.00"


def test_log_with_only_empty_fields(tmp_path):
    """a cold-start log with empty fields gives no fix, 0 satellites, and no crash (edge case)"""
    log = tmp_path / "cold.txt"
    log.write_text(
        "$GPGGA,120000.00,,,,,,,,,,,,,*7B\n"        # even the quality field is empty
        "$GNRMC,120000.00,V,,,,,,,281026,,,N*6F\n"
        "$GPGGA,120001.00,,,,,0,,,,,,,,*4A\n"
    )
    s = analyze_log(str(log))
    assert s["valid"] == 3
    assert s["fix_quality_counts"] == {0: 2}
    assert s["max_satellites"] == 0
    assert s["first_fix_utc"] is None
    assert s["last_fix_utc"] is None
    assert s["fix_rate_pct"] == 0.0


def test_empty_log_file(tmp_path):
    """an empty log file gives all-zero counts, empty dicts, and no ZeroDivisionError (edge case)"""
    log = tmp_path / "empty.txt"
    log.write_text("")
    s = analyze_log(str(log))
    assert s["total_lines"] == 0
    assert s["valid"] == 0
    assert s["by_type"] == {}
    assert s["fix_quality_counts"] == {}
    assert s["fix_rate_pct"] == 0.0
    assert s["max_satellites"] == 0
    assert s["first_fix_utc"] is None


def test_format_summary_lines():
    """format_summary has the required lines, with the fix rate to 1 decimal and 'none' for no fix"""
    summary = {
        "total_lines": 10, "blank": 1, "malformed": 2, "bad_checksum": 3, "valid": 4,
        "by_type": {"GGA": 3, "RMC": 1}, "fix_quality_counts": {0: 1, 1: 2},
        "fix_rate_pct": 66.66666, "max_satellites": 9,
        "first_fix_utc": "101500.00", "last_fix_utc": None,
    }
    text = format_summary(summary)
    assert isinstance(text, str)
    lines = [line.strip() for line in text.splitlines()]
    for required in ["Lines read: 10", "Valid: 4", "Bad checksum: 3", "Malformed: 2",
                     "Blank: 1", "Fix rate: 66.7%", "Max satellites: 9",
                     "First fix (UTC): 101500.00", "Last fix (UTC): none"]:
        assert required in lines, f"missing line: {required!r}"


def test_main_prints_and_writes_summary(tmp_path, capsys):
    """main() prints the summary and writes the same text to the output file"""
    out = tmp_path / "summary.txt"
    result = main(LOG, str(out))
    printed = capsys.readouterr().out
    expected = format_summary(analyze_log(LOG))
    assert result["valid"] == 59
    assert "Valid: 59" in printed
    assert out.read_text().strip() == expected.strip()
