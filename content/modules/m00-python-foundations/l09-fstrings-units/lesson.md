## Why this lesson matters

In lesson 0.1 you pulled the latitude field out of a `$GPGGA` sentence and got the text `'4807.038'`. That looks like a number, but it is two things in disguise: **degrees** and **minutes**, glued together. It is not 4807 degrees, and it is not 48.07038 degrees either. Every map library, every ROS 2 `NavSatFix` message, and every distance formula you will use wants **signed decimal degrees**, like `48.1173`. Getting from one to the other is a unit conversion, and unit conversions are where robots quietly go wrong.

You already know this from the hardware side. A sensor that reports in counts, millivolts, or tenths of a degree is fine as long as everyone agrees on the units. The moment one block of the system assumes different units, the reading is wrong by a constant factor and **nothing crashes**. The robot just drives to the wrong place. This lesson gives you two tools to stop that from happening:

1. **Unit conversion done right**: NMEA `ddmm.mmmm` to signed decimal degrees, and the difference between `int()`, `float()`, and `round()`.
2. **f-strings**: printing numbers with a fixed number of decimals, a fixed width, and their units, so that your logs say exactly what they mean.

## f-strings: text with holes in it

Put an `f` in front of a string and you can drop any expression inside `{ }`. Python evaluates it and inserts the result as text:

```python
sats = 8
print(f"{sats} satellites")      # 8 satellites
print(f"{sats * 2} half-sats")   # any expression works: 16 half-sats
```

That replaces the clumsy `"sats: " + str(sats)`, which crashes with a `TypeError` if you forget the `str()`.

### The format spec: what goes after the colon

Inside the braces you can add a colon and a **format spec** that controls how the value looks: `{value:spec}`. Think of it as the display setting on a multimeter: the reading is the same, you are choosing how many digits to show.

| Spec | Meaning | Example | Result |
|---|---|---|---|
| `.6f` | fixed point, exactly 6 decimals | `f"{48.1173:.6f}"` | `48.117300` |
| `.0f` | no decimals (rounds) | `f"{545.4:.0f}"` | `545` |
| `8.2f` | width 8, 2 decimals | `f"[{545.4:8.2f}]"` | `[  545.40]` |
| `4d` | integer, width 4 | `f"[{8:4d}]"` | `[   8]` |
| `02d` | integer, width 2, zero-padded | `f"{8:02d}"` | `08` |
| `<6` | left-align in width 6 | `f"[{'GP':<6}]"` | `[GP    ]` |
| `>6` | right-align in width 6 | `f"[{'GP':>6}]"` | `[    GP]` |
| `+.1f` | always show the sign | `f"{3.5:+.1f}"` | `+3.5` |
| `,.0f` | thousands separator | `f"{82283.4:,.0f}"` | `82,283` |

Three details that trip people up:

- **Width counts every character**, including the minus sign and the decimal point. `545.40` is 6 characters, so width 8 adds 2 spaces in front.
- **Numbers right-align by default, text left-aligns by default.** That's what makes columns of numbers line up on the decimal point.
- **Width is a minimum, not a maximum.** A value that is too wide is never cut off; the column just gets wider.

Units go *outside* the braces, as plain text: `f"{alt:.1f} m"`, `f"{lat:.6f}°"`. Always print units. A log line that says `alt 10.2` is a guess; `alt 10.2 m` is a measurement.

## int(), float(), and round() are three different tools

Everything you get from `split(",")` is a **string**. To do math you must convert it, and you must choose the right converter.

| Call | What it does | Example |
|---|---|---|
| `int("08")` | text of a whole number → int | `8` (leading zeros are fine) |
| `int("4807.038")` | **crashes** | `ValueError`: that text isn't a whole number |
| `float("4807.038")` | text of any number → float | `4807.038` |
| `int(4807.038)` | float → int by **chopping** the decimals (toward zero) | `4807` |
| `int(-3.7)` | chops toward zero, not down | `-3` |
| `round(-3.7)` | nearest whole number | `-4` |
| `round(2.5)` | exact ties go to the **even** neighbor | `2` (and `round(3.5)` is `4`) |
| `round(48.11730041, 6)` | round to 6 places, result is still a float | `48.1173` |

Two lessons hide in that table. First, `int()` on a float is a **truncation**, like an ADC that throws away the low bits; it is not rounding. Second, `round(x, 6)` changes the *value*, while `f"{x:.6f}"` only changes how it is *displayed*. Keep full precision for math and round only when you print. And `round()` can't help you with display anyway: `round(5.5, 6)` is just `5.5`, so it prints as `5.5`, not `5.500000`. For a fixed number of digits, use the format spec.

### Floats are not exact

A float is stored in binary, so most decimal fractions are approximations. `4807.038 - 4800` gives `7.037999999999556`, not `7.038`. This is normal, it's tiny (about 10⁻¹² here), and it's why you should never compare floats with `==`. Compare with a tolerance instead: `abs(a - b) < 1e-9`. The hidden tests in this course do the same thing using `pytest.approx`.

## NMEA positions: degrees and minutes, glued together

A degree is split into **60 minutes** (like an hour into 60 minutes of time). NMEA packs the degrees and the minutes into one field:

```
latitude   4220.0101   = 42° 20.0101'      format ddmm.mmmm   (2 degree digits)
longitude 07105.6600   = 71° 05.6600'      format dddmm.mmmm  (3 degree digits)
```

The **minutes are always the two digits just before the decimal point, plus everything after it**. Whatever is in front of those is the degrees. Latitude needs only 2 degree digits (it never exceeds 90°), and longitude needs 3 (up to 180°).

To convert to decimal degrees, divide the minutes by 60 and add:

$$\text{decimal degrees} = \text{degrees} + \frac{\text{minutes}}{60}$$

For `4220.0101`: 42 + 20.0101 / 60 = 42 + 0.333502 = **42.333502**.

You don't have to memorize the format or the sign rule below. They're collected in this reference table, and the questions, challenge, and bug that need them show it next to them:

{{ref:ddmm}}

### The sign comes from the hemisphere letter

The number in the field is always positive. Direction lives in the **next** field:

- `N` (north of the equator) and `E` (east of Greenwich): **positive**
- `S` (south) and `W` (west): **negative**

Boston is north and west, so a fix there is roughly `(42.33, -71.09)`. Forget the minus sign on a `W` and your robot in Boston plots in Central Asia, near the Kazakhstan border.

### Two ways to split degrees from minutes

**By position of the decimal point** (string slicing, lesson 0.1): find the `.`, the minutes start 2 characters before it.

**By arithmetic**: treat the whole field as one number. `4220.0101 // 100` is `42.0` (the degrees), and the remainder after taking away `42 * 100` is `20.0101` (the minutes). Floor division `//` throws away everything after "how many whole hundreds", which is exactly the degrees.

Both work for latitude *and* longitude without knowing which one you have. A fixed slice like `text[:2]` works for latitude only, and silently gives garbage for longitude.

### The units mistake everyone makes once

It's tempting to read `4220.0101` as "42.200101 degrees" by dividing by 100. That treats the minutes as if they were hundredths of a degree. They aren't: 20 minutes is a third of a degree (0.3333), not 0.20. The error is up to 0.4° in latitude, which is about **45 km**. The program runs, prints a reasonable-looking number, and puts your robot in the wrong town. You'll see exactly this in Example 3 and in the bug below.

## Why 6 decimal places?

One degree of latitude is about 111,320 m (the Earth's circumference, about 40,075 km, divided by 360). So the last digit you print decides the smallest position change your log can show:

| Decimal places | Smallest step | North-south |
|---|---|---|
| 4 | 0.0001° | about 11 m |
| 5 | 0.00001° | about 1.1 m |
| **6** | **0.000001°** | **about 0.11 m** |
| 7 | 0.0000001° | about 0.011 m |

A normal GPS receiver is accurate to a few meters and an RTK receiver to a couple of centimeters, so **6 decimal places (about 0.1 m)** is the usual choice: fine enough for RTK-grade work, without pretending to more precision than you have. Printing 3 decimals (about 111 m) would erase your whole robot run. East-west steps are smaller than north-south ones away from the equator, because lines of longitude converge toward the poles: at Boston, one degree of longitude is only about 82 km. Example 4 computes this with `math.cos`.

## Worked examples

Read each example, predict what it prints, then run it. Change the format specs and re-run: it's the fastest way to learn them.

**Example 1: f-string format specs.** Precision, width, zero-padding, alignment, signs, and units.

{{example:ex1}}

**Example 2: int(), float(), round(), and float error.** Watch `int()` chop, `round()` round, and a subtraction come out not-quite-exact.

{{example:ex2}}

**Example 3: robotics-realistic: a $GPGGA fix in signed decimal degrees.** The full conversion for both fields, the hemisphere signs, and how far off the "divide by 100" mistake puts you.

{{example:ex3}}

**Example 4: why 6 decimal places is about 0.1 m.** A formatted table of what each decimal place means in meters, north-south and east-west, at Boston's latitude. (`import math` gives you `math.cos`; `math.radians` converts degrees to radians, because `cos` expects radians.)

{{example:ex4}}

## Predict, then check

{{predict:p1}}

{{predict:p2}}

{{predict:p3}}

## See it: trace a longitude conversion

Before you step through, write down your prediction: what values will `degrees` and `minutes` get for `'07105.6600'`, and what will be printed? Then trace it and watch the variables table. Notice that `int('071')` quietly drops the leading zero, and that the sign is applied *after* the conversion.

{{viz:v1}}

And here is the sentence the trace came from. Find fields 2 to 5: the latitude, its hemisphere, the longitude, and its hemisphere.

{{viz:v2}}

## Common beginner mistakes

1. **Minutes treated as decimal degrees.** `float("4220.0101") / 100` gives 42.200101, which is wrong by about 15 km. Minutes must be divided by **60**.
2. **Forgetting the W (or S) sign.** The field itself is always positive. Every western-hemisphere longitude must come out negative, or your map is mirrored across Greenwich.
3. **A fixed slice for both fields.** `text[:2]` works for latitude but not for 3-digit longitude. Split at the decimal point, or use `// 100`.
4. **`int()` on text with a decimal point.** `int("4807.038")` raises `ValueError`. Use `float()` first, or slice off only the digits you want.
5. **Using `round()` for display.** `round(5.5, 6)` is `5.5`, so it prints as `5.5`. To always show 6 decimals, use `f"{x:.6f}"`.
6. **Rounding too early.** Round (or format) only when printing. Rounding in the middle of a calculation throws away precision you can never get back.
7. **No units in the log.** Future-you won't remember whether that column was meters, feet, or degrees. Put units in every f-string.

## Challenge: convert and label a fix

Write two functions:

- `nmea_to_decimal(value, hemisphere)` takes the position text and its hemisphere letter, for example `('4220.0101', 'N')` or `('07105.6600', 'W')`, and returns **signed decimal degrees** as a float. You are *not* told whether the value is latitude (2 degree digits) or longitude (3 degree digits), so your split has to work for both. If either argument is an empty string (no fix yet), return `None`.
- `format_position(lat, lon)` takes signed decimal degrees and returns a label like `'42.333502°N, 71.094333°W'`: the absolute value with **exactly 6 decimals**, a degree sign, and the hemisphere letter (`N` for lat ≥ 0, else `S`; `E` for lon ≥ 0, else `W`), with `', '` between them. No minus signs: the letter carries the direction.

The hidden tests include the southern and eastern hemispheres, longitudes over 100°, the equator, fewer decimal places, and empty fields.

{{challenge}}

## Find the bug

{{bug}}

## Explain it back

{{explain}}
