# NMEA Log Analyzer

<!-- Replace every <placeholder>, then delete these comments. Write it in your own words:
     an interviewer will ask you about every sentence here. -->

A Python command-line tool that reads a raw GPS log in NMEA 0183 format, validates every
sentence's XOR checksum, and reports how healthy the receiver's data was.

<one or two sentences: why you built it, for example the EECE5554 GPS lab, and what problem it solves>

## What it does

- Sorts every line into **blank**, **malformed**, **bad checksum**, or **valid**
- Counts valid sentences by type (GGA, RMC, GSA, ...)
- Counts GGA fixes by fix quality and computes the fix rate
- Finds the maximum satellite count and the first and last fix times
- Prints a summary and writes it to `gps_summary.txt`

## Example output

Run on the included `gps_log.txt` (<number> lines):

```
<paste the exact output of: python nmea_analyzer.py>
```

## Usage

Requires Python 3.10+ and nothing outside the standard library.

```
python nmea_analyzer.py
```

<if you did the sys.argv stretch goal, show: python nmea_analyzer.py path/to/log.txt>

## How it works

1. <how you decide a line is malformed vs. a bad checksum>
2. <how the XOR checksum is computed, in one or two sentences>
3. <how GGA fields are pulled out and what happens with empty fields>
4. <how the statistics are accumulated: which data structures and why>

## Design decisions

- **Corrupted sentences never feed the statistics.** <why: what would go wrong if they did? Find the example in gps_log.txt>
- **Empty fields are treated as 0, not as errors.** <why: what does a receiver send before it has a fix?>
- <one more decision you made, for example how you structured the functions>

## Testing

<how you checked it: the 14 course tests (blank lines, \r\n line endings, lowercase hex,
truncated lines, cold-start logs with empty fields, an empty file), plus anything you checked by hand>

## What I'd do next

- <for example: report the longest gap without a fix>
- <for example: read straight from a serial port with pyserial>
- <for example: publish the fixes as a ROS 2 sensor_msgs/NavSatFix topic>

## What I learned

<two or three honest sentences: what was hard, what bug took longest to find, and how you found it>

---
Built by <your name> as part of a self-directed Python for Robotics course. <link to your GitHub profile or LinkedIn>
