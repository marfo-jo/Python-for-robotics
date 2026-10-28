"""NMEA log analyzer: Module 0 project.

Read a GPS log, sort every line into blank / malformed / bad_checksum / valid,
and report fix-quality statistics. The brief above has the full rules.
Replace every TODO with your own code. Add helper functions if you like
(a checksum function and a GGA parser are good ideas).
"""


def classify_line(line):
    """Return "blank", "malformed", "bad_checksum", or "valid" for one log line.

    - "blank":        nothing left after strip()
    - "malformed":    doesn't start with '$', doesn't have exactly one '*',
                      or the text after '*' isn't exactly 2 hex digits
    - "bad_checksum": well-formed, but the XOR checksum doesn't match
    - "valid":        the checksum matches (hex digits may be upper or lower case)
    """
    # TODO
    return ""


def analyze_log(path):
    """Read the log at `path` and return the summary dict described in the brief.

    Keys: total_lines, blank, malformed, bad_checksum, valid, by_type,
    fix_quality_counts, fix_rate_pct, max_satellites, first_fix_utc, last_fix_utc
    """
    # TODO
    return {}


def format_summary(summary):
    """Return the human-readable report (one string, lines joined with newlines)."""
    # TODO
    return ""


def main(log_path="gps_log.txt", out_path="gps_summary.txt"):
    """Analyze log_path, print the report, write it to out_path, return the summary dict."""
    # TODO
    return {}


if __name__ == "__main__":
    main()
