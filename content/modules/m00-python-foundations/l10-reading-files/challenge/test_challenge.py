from solution import load_sentences

G1 = "$GPGGA,153012.00,4220.0101,N,07105.6600,W,1,09,0.9,10.2,M,-33.1,M,,*62"
G2 = "$GPGGA,153013.00,4220.0105,N,07105.6592,W,1,09,0.9,10.4,M,-33.1,M,,*69"
G3 = "$GPGGA,153014.00,4220.0110,N,07105.6584,W,1,10,0.8,10.5,M,-33.1,M,,*65"
RMC = "$GPRMC,153012.00,A,4220.0101,N,07105.6600,W,0.52,54.70,281026,,,A*71"
NO_FIX = "$GPGGA,153015.00,,,,,0,00,99.9,,M,,M,,*5C"
BAD_SUM = "$GPGGA,153014.00,4220.0110,N,07105.6584,W,1,10,0.8,10.5,M,-33.1,M,,*66"


def write_log(folder, text, name="gps_log.txt"):
    path = folder / name
    path.write_text(text, encoding="utf-8")
    return str(path)


def test_clean_log(tmp_path):
    """a clean 3-line log gives 3 sentences and 0 errors"""
    path = write_log(tmp_path, G1 + "\n" + G2 + "\n" + G3 + "\n")
    assert load_sentences(path) == ([G1, G2, G3], 0)


def test_sentences_are_stripped(tmp_path):
    """returned sentences have no newline or spaces on the ends"""
    path = write_log(tmp_path, "  " + G1 + "  \n\t" + G2 + "\n")
    sentences, errors = load_sentences(path)
    assert sentences == [G1, G2]
    assert errors == 0


def test_blank_lines_are_not_errors(tmp_path):
    """blank and whitespace-only lines are skipped and NOT counted as errors"""
    path = write_log(tmp_path, "\n" + G1 + "\n\n   \n" + G2 + "\n\n")
    assert load_sentences(path) == ([G1, G2], 0)


def test_truncated_last_line(tmp_path):
    """a last line cut off by power loss (no '*', no newline) counts as 1 error"""
    path = write_log(tmp_path, G1 + "\n" + G2 + "\n$GPGGA,153014.00,4220.01")
    assert load_sentences(path) == ([G1, G2], 1)


def test_junk_lines(tmp_path):
    """non-NMEA lines (a receiver boot banner, a comment) count as errors"""
    path = write_log(tmp_path, "u-blox NEO-M8N ROM 2.01\n" + G1 + "\n# test drive 2\n")
    assert load_sentences(path) == ([G1], 2)


def test_bad_checksum(tmp_path):
    """a sentence whose checksum doesn't match is rejected and counted as an error"""
    path = write_log(tmp_path, G1 + "\n" + BAD_SUM + "\n" + G2 + "\n")
    assert load_sentences(path) == ([G1, G2], 1)


def test_lowercase_checksum(tmp_path):
    """lowercase hex checksums like '*5c' are valid (edge case)"""
    lower = NO_FIX[:-2] + "5c"
    path = write_log(tmp_path, lower + "\n")
    assert load_sentences(path) == ([lower], 0)


def test_windows_line_endings(tmp_path):
    """a log saved with Windows \\r\\n line endings still works (edge case)"""
    path = tmp_path / "windows_log.txt"
    path.write_bytes((G1 + "\r\n" + RMC + "\r\n\r\n").encode("utf-8"))
    assert load_sentences(str(path)) == ([G1, RMC], 0)


def test_empty_file(tmp_path):
    """an empty file gives ([], 0) (edge case)"""
    path = write_log(tmp_path, "")
    assert load_sentences(path) == ([], 0)


def test_keeps_file_order(tmp_path):
    """sentences come back in file order, including RMC and no-fix sentences"""
    path = write_log(tmp_path, G2 + "\n" + RMC + "\n" + NO_FIX + "\n" + G1 + "\n")
    assert load_sentences(path) == ([G2, RMC, NO_FIX, G1], 0)


def test_path_in_subfolder(tmp_path):
    """works for a log in a sub-folder (use the path you are given; don't hard-code a name)"""
    folder = tmp_path / "logs" / "2026-10-28"
    folder.mkdir(parents=True)
    path = write_log(folder, G3 + "\n", name="run_07.txt")
    assert load_sentences(path) == ([G3], 0)


def test_realistic_field_log(tmp_path):
    """a realistic field log: banner, blank lines, corruption, a cut-off '*', and a truncated last line"""
    text = ("u-blox NEO-M8N ROM 2.01\n"
            "\n"
            + G1 + "\n"
            + RMC + "\n"
            + BAD_SUM + "\n"
            "$GPGGA,153014.00,4220.0*\n"
            "\n"
            + G2 + "\n"
            "# battery 11.2 V, 12°C\n"
            "$GPGGA,153015.00,4220.01")
    path = write_log(tmp_path, text)
    assert load_sentences(path) == ([G1, RMC, G2], 5)
