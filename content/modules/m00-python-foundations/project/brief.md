## The job

You've been handed `gps_log.txt`: about a minute of raw output from a GPS receiver on a test drive near campus, captured straight off the serial port. Like every real log, it's messy. The receiver started cold (no fix yet), lost the sky under an overpass, had a buffer overrun, picked up some line noise, and the logger lost power mid-sentence at the end.

Your job is to write the diagnostic tool a field technician would want: **an NMEA log analyzer**. It reads the log, sorts every line into a bucket, and reports how healthy the GPS was. Think of it as the PLC fault-log review you'd do after a breakdown: count the faults, categorize them, and summarize the good data, without crashing on the bad data.

This project uses everything from Module 0: strings, conditionals, loops, the XOR checksum, lists, functions, tuples, dicts, f-strings, files, and exceptions. There is no new material. If you get stuck, the lesson that covers that step is the right place to look, and the hints unlock one tier at a time.

When the tests pass, you export it as `nmea_analyzer.py` with a README and put it on your GitHub. It's your first portfolio project, so write it like someone will read it.

## What a line can be

Every line of the file goes into **exactly one** of these four buckets. Apply the rules in this order, after `strip()`-ing the line:

| Bucket | Rule |
|---|---|
| `"blank"` | Nothing is left after `strip()`. A blank line is **not** malformed: it's just an empty frame. |
| `"malformed"` | The line doesn't start with `$`, **or** doesn't contain exactly one `*`, **or** the text after the `*` isn't exactly 2 hex digits (`0-9`, `A-F`, upper or lower case). |
| `"bad_checksum"` | Well-formed, but the XOR of every character between `$` and `*` doesn't match the two hex digits. |
| `"valid"` | The checksum matches. Hex digits may be lowercase: `*7c` matches a computed `7C`. |

The checksum rule and the parts of a sentence, as references (you don't need to memorize them):

{{ref:checksum}}

{{ref:anatomy}}

Only **valid** sentences count toward any statistic below. A corrupted sentence might claim 13 satellites; you can't trust anything in it.

## Required functions

Your file must define these four functions with exactly these names and parameters. You may (and should) add helpers, such as `checksum(body)` and `parse_gga(sentence)`.

### `classify_line(line) -> str`

Returns `"blank"`, `"malformed"`, `"bad_checksum"`, or `"valid"` for one line, using the rules above. It must cope with leading/trailing spaces and a trailing `"\r\n"` or `"\n"`.

### `analyze_log(path) -> dict`

Opens the file at `path`, classifies every line, and returns a dict with **exactly these keys**:

| Key | Type | Meaning |
|---|---|---|
| `total_lines` | int | Every line in the file, including blank and broken ones |
| `blank` | int | Lines classified `"blank"` |
| `malformed` | int | Lines classified `"malformed"` |
| `bad_checksum` | int | Lines classified `"bad_checksum"` |
| `valid` | int | Lines classified `"valid"` |
| `by_type` | dict str → int | Valid sentences counted by sentence type, ignoring the talker: `$GPGGA` and `$GNGGA` both count as `"GGA"`. Every talker in this course is 2 letters, so the type is the 3 characters after them. |
| `fix_quality_counts` | dict **int** → int | Valid GGA sentences counted by fix quality (GGA field 6). Keys are ints: `{0: 5, 1: 16}`, not `{"0": 5}`. An **empty** quality field counts as `0`. |
| `fix_rate_pct` | float | Percentage of valid GGA sentences with quality > 0. `0.0` if there are no valid GGA sentences (don't divide by zero). |
| `max_satellites` | int | Largest satellite count (GGA field 7) among valid GGA sentences. An **empty** satellites field counts as `0`. `0` if there are none. |
| `first_fix_utc` | str or None | UTC time text (GGA field 1, for example `"140000.00"`) of the first valid GGA with quality > 0. `None` if there's no fix in the whole log. |
| `last_fix_utc` | str or None | Same, for the last one. |

The four counts must add up: `blank + malformed + bad_checksum + valid == total_lines`.

A reminder of the GGA fields (index after `split(",")` on the text between `$` and `*`):

```
GPGGA,140000.00,4220.38800,N,07105.35200,W,1,06,1.37,12.3,M,-33.1,M,,
  0       1         2      3      4      5 6  7   8    9  10  11  12 13 14
```

The full GGA field table and the fix-quality codes (keep them open while you code; nobody memorizes these):

{{ref:gga}}

{{ref:fixquality}}

### `format_summary(summary) -> str`

Takes the dict from `analyze_log` and returns a multi-line report (one string, lines joined with `"\n"`). It must contain these lines exactly (other lines, like a title or a sentence-type breakdown, are welcome):

```
Lines read: 65
Valid: 59
Bad checksum: 3
Malformed: 2
Blank: 1
Fix rate: 81.5%
Max satellites: 11
First fix (UTC): 140000.00
Last fix (UTC): 140024.00
```

The fix rate has exactly **one decimal place**. When a fix time is `None`, print `none` instead: `Last fix (UTC): none`.

(Yes, those are the real numbers for `gps_log.txt`. Knowing the target doesn't help you much: the tests also run your code on other logs.)

### `main(log_path="gps_log.txt", out_path="gps_summary.txt") -> dict`

Runs `analyze_log(log_path)`, **prints** `format_summary(...)`, **writes** the same text to `out_path`, and returns the summary dict.

Writing a file is the mirror image of reading one. Open it in write mode (`"w"` replaces anything already there) and call `write` with a string:

```python
with open(out_path, "w") as f:
    f.write(text + "\n")
```

### The command line

End your file with:

```python
if __name__ == "__main__":
    main()
```

so that on your own machine, with `gps_log.txt` in the same folder:

```
(robotics-course) PS> python nmea_analyzer.py
```

prints the report and creates `gps_summary.txt`. The `if __name__ == "__main__":` line means "only run this when the file is run directly, not when it's imported", which is why the tests can import your functions without the analyzer running on its own.

## How it's graded

14 hidden tests: line classification (including `\r\n`, lowercase hex, blanks, and five kinds of malformed line), exact counts on `gps_log.txt`, statistics that must ignore corrupted lines, a cold-start log full of empty fields, an **empty** file, the summary format, and `main()`. Read each failing test's name: it tells you which rule you broke.

Before you write any code, open [gps_log.txt](content/data/gps_log.txt) (it's also at `content/data/gps_log.txt` in the course repo) and find, by eye, the blank line, the two malformed lines, and the three bad checksums. If you can't point at them, you don't understand the data yet, and no amount of code will fix that.

## Make it a portfolio repo

1. Create a public GitHub repo named something like `nmea-log-analyzer`.
2. Download your passing code (`nmea_analyzer.py`) and the README template from the buttons below. Save [gps_log.txt](content/data/gps_log.txt) next to them.
3. Run it locally in the `robotics-course` env (`python nmea_analyzer.py`) and commit the `gps_summary.txt` it writes, so a reviewer sees real output. After lesson S.9 (pytest basics) you'll come back and add your own `test_nmea_analyzer.py`: a repo with passing tests is worth far more to a reviewer than one without.
4. Fill in every `<placeholder>` in the README **yourself**. The "design decisions" and "what I'd do next" sections are the parts interviewers ask about.
5. Commit and push. Pin the repo on your GitHub profile.

## Stretch goals (not graded)

- Accept the log path on the command line (`sys.argv[1]`), defaulting to `gps_log.txt`.
- Add the total distance travelled, using the RMC speed (knots) and the 1 s spacing. 1 knot = 1852 m per hour = 0.514444 m/s.
- Report the longest gap without a fix, in seconds, by converting `hhmmss.ss` to seconds since midnight.

{{ref:rmc}}

{{ref:utctime}}
