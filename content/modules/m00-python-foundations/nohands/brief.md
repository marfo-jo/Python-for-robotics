## The rules

**Closed book. 30 minutes. No notes, no lessons, no AI tutor, no searching, no pasting.** You may run your code as often as you like. That's what an engineer does at a bench, and it's what you'll do in a live coding interview.

This checkpoint proves that the Module 0 skills are yours, not the course's. If you don't finish in 30 minutes, keep going until the tests pass, note how long it took, and come back in a few days to do it again from a blank file. Passing slowly is still passing. Passing because you looked something up isn't, and only you know which one happened.

## The task

Write one function:

```python
def parse_rmc(sentence):
```

`sentence` is one line from a GPS receiver, for example:

```
$GNRMC,140000.00,A,4220.38800,N,07105.35200,W,1.200,45.10,281026,,,A*5B
```

The RMC ("recommended minimum") fields, numbered after you `split(",")` the text between `$` and `*`:

| Index | Example | Meaning |
|---|---|---|
| 0 | `GNRMC` | talker + sentence type |
| 1 | `140000.00` | UTC time, hhmmss.ss |
| 2 | `A` | status: `A` = active (valid fix), `V` = void (no valid fix) |
| 3, 4 | `4220.38800`, `N` | latitude **ddmm.mmmm**, and `N` or `S` |
| 5, 6 | `07105.35200`, `W` | longitude **dddmm.mmmm**, and `E` or `W` |
| 7 | `1.200` | speed over ground, knots |
| 8 | `45.10` | course over ground, degrees (can be **empty** when the receiver isn't moving) |
| 9 | `281026` | date, ddmmyy |
| 10 and on | | magnetic variation and mode (ignore them) |

### Return `None` when

- the line (after `strip()`) doesn't start with `$` or doesn't contain a `*`,
- the XOR checksum of the characters between `$` and `*` doesn't match the two hex digits after `*` (which may be upper or lower case),
- the sentence type isn't `RMC` (any 2-letter talker, so `$GPRMC` and `$GNRMC` both count),
- the status is anything other than `A`.

### Otherwise return a dict with exactly these keys

| Key | Type | Example (sentence above) |
|---|---|---|
| `"utc"` | str | `"140000.00"` |
| `"date"` | str | `"281026"` |
| `"lat"` | float, decimal degrees, **negative for S** | `42.3398` |
| `"lon"` | float, decimal degrees, **negative for W** | `-71.0892` |
| `"speed_knots"` | float | `1.2` |
| `"course_deg"` | float, or `None` if the field is empty | `45.1` |

The line may arrive with surrounding spaces or a trailing `"\r\n"`, as it would from a serial port.

## How it's graded

9 hidden tests: normal sentences in both hemispheres, the degree-minute conversion, an empty course field, void status, a corrupted checksum, a serial line ending with lowercase hex, malformed lines and other sentence types, and positions near 0 degrees.

Before you start typing, spend two minutes writing the steps as comments. Then turn each comment into code, running it as you go.
