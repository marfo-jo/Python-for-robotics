**About 20 minutes.** Just enough of Python's `csv` module to write a sensor log that survives crashes and opens cleanly in numpy and Excel. Module S lesson S.1 covers files in depth later.

## Why CSV, and what makes a good log

A CSV ("comma-separated values") file is a table in plain text: one header row of column names, then one row per sample. It's the lowest common denominator: numpy, pandas, Excel, and every colleague can open it.

A good sensor log, like a good maintenance log, answers "what happened, when, measured how?" without the person who recorded it in the room. So:

- **One header row** with names that include units where it isn't obvious: `host_time_s`, `t_ms`, `temp_c`.
- **Raw values**, not only converted ones. You can always re-convert raw counts with a corrected scale factor; you can never un-convert.
- **A timestamp on every row**, ideally from the device's own clock (`t_ms`) plus the host's receive time.
- **A unique file name per run**, so a new recording never overwrites an old one.
- **Nothing else in the file.** Notes about the setup (firmware version, DLPF setting, how the IMU was mounted) go in your README, a lab notebook, or a small text or JSON file next to the log with the same name.

## Writing rows

```python
import csv

rows = [(0.00, 21.50, 1), (0.50, 21.56, 1), (1.00, 21.61, 0)]

with open("demo_log.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["time_s", "temp_c", "fan_on"])
    for row in rows:
        writer.writerow(row)

with open("demo_log.csv", newline="") as f:
    for record in csv.reader(f):
        print(record)
```

Output:

```
['time_s', 'temp_c', 'fan_on']
['0.0', '21.5', '1']
['0.5', '21.56', '1']
['1.0', '21.61', '0']
```

Line by line:

- `open(..., "w", newline="")`: `"w"` creates the file (or **erases** an existing one). `newline=""` is required for the `csv` module. Without it, on Windows, every row is followed by a **blank line**, because both Python and the `csv` module add a line ending.
- `csv.writer(f)` wraps the file. `writerow` takes any sequence (a list or a tuple) and handles commas and quoting for you. Don't build rows with `",".join(...)` by hand.
- The `with` block closes the file at the end, even if an exception happens inside it.

Notice what came back when reading: **every value is a string** (`'21.5'`, not `21.5`). CSV has no types. Convert when you read (`float(...)`, `int(...)`), or load numeric logs with numpy (see [plotting a CSV log](#/t/sprints/bg-plot)), which converts for you.

## Reading by column name

`csv.DictReader` uses the header row as keys, which is clearer than remembering column numbers:

```python
import csv

with open("demo_log.csv", newline="") as f:
    reader = csv.DictReader(f)
    for rec in reader:
        print(rec["temp_c"], type(rec["temp_c"]).__name__, float(rec["temp_c"]) + 1)
```

Output:

```
21.5 str 22.5
21.56 str 22.56
21.61 str 22.61
```

## A unique, timestamped file name

```python
from datetime import datetime
from pathlib import Path

stamp = datetime(2026, 11, 8, 14, 15, 2).strftime("%Y%m%d_%H%M%S")
path = Path("data") / f"imu_{stamp}.csv"
print(path.as_posix())
```

Output:

```
data/imu_20261108_141502.csv
```

In your logger, use `datetime.now()` instead of a fixed date. The `YYYYMMDD_HHMMSS` order means the files sort by time in File Explorer. `Path("data") / name` builds the path with the right separator on any OS. Make sure the folder exists first (`path.parent.mkdir(exist_ok=True)`).

## Surviving a crash or a Ctrl+C

Python doesn't write each row to the disk immediately: it collects them in a buffer and writes in big chunks, which is much faster. The catch: if the script is killed, whatever is still in the buffer is lost.

- The `with` block flushes and closes the file on a normal exit **and** on an exception, including `KeyboardInterrupt` (Ctrl+C), so the main defense is simply: always use `with`.
- For long recordings (the 3-hour Allan log), also call `f.flush()` about **once per second**. Then even a power cut or a hard crash loses at most a second. Don't flush every row at 100 Hz: it's slow and gains nothing.

## Common beginner mistakes

- Missing `newline=""`: blank lines between rows on Windows.
- `"w"` on an existing log: it's erased without warning. Timestamped names prevent this.
- Writing the header inside the loop, so it appears on every row.
- Writing floats with 15 digits (`0.30000000000000004`) when the sensor resolution is 4 digits. For converted values, round when writing; for raw integers, there's nothing to round.
- Putting comment lines or notes inside the CSV. Some tools skip them, others choke on them.
- Opening and closing the file for every row. It works, but it's slow and hammers the disk.

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| Blank line after every row | `newline=""` missing | Add it to `open(...)`. |
| `PermissionError` when opening the log | The file is open in Excel (Excel locks files on Windows) | Close it in Excel, or copy it before opening. |
| The log ends a few seconds early after Ctrl+C | No `with` block, so the buffer was never flushed | Use `with`, and catch `KeyboardInterrupt` around the loop, not around the `with`. |
| Numbers come back as strings | That's CSV | Convert on read, or use `np.loadtxt`. |
| Excel shows `1.23E+05` or drops leading zeros | Excel guessing formats | Only a display issue; the file is fine. |
