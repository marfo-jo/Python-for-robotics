## Why tuples?

At the end of lesson 0.6, `parse_gga` returned a list like `['152305.00', 1, 9, 12.3]`. It worked, but think about what that list *is*. It isn't a collection of similar things that grows over time, like a log of satellite counts. It's **one record** with a fixed shape: slot 0 is the time, slot 1 is the quality, and so on. Nobody should ever `append` a fifth item to it, or overwrite the time by accident.

Python has a container made for exactly this: the **tuple**. In this lesson you'll use tuples to return a `(lat, lon)` pair from a function, unpack records cleanly, and see why "you can't change it" is a feature on a robot.

### The EE view: a tuple is a latched frame

When a UART receiver finishes a frame, it **latches** it into a holding register. Downstream logic reads the frame, but nothing can write into the middle of it. The next frame is a new latch, not an edit of the old one.

| Tuple idea | Hardware idea |
|---|---|
| `fix = ("152305.00", 42.33539, -71.0928)` | Latch one frame with fixed fields |
| `fix[1]` | Read the field at a known offset |
| `fix[1] = 0.0` → `TypeError` | The holding register is read-only |
| `time, lat, lon = fix` | Fan the frame's fields out to three named wires |
| A list of tuples | A FIFO of latched frames: the FIFO grows, each frame is fixed |

## Tuples: the ideas you need

### 1. Making a tuple

A tuple is a sequence of values separated by **commas**, usually wrapped in parentheses:

```python
fix = ("152305.00", 42.33539, -71.0928)    # (time, lat, lon)
pair = 42.33539, -71.0928                  # parentheses are optional: commas make it
empty = ()                                 # an empty tuple
one = (8,)                                 # ONE item needs a trailing comma
```

That last line surprises everyone. `(8)` is **not** a tuple: it's just the number 8 in grouping parentheses, the same as in `(2 + 3) * 4`. **It's the comma that makes a tuple**, not the parentheses.

### 2. Reading a tuple: same as a list

Indexing, negative indexes, slicing, `len()`, `in`, and `for` all work exactly like they do on lists:

```python
fix[0]        # '152305.00'
fix[-1]       # -71.0928
fix[1:]       # (42.33539, -71.0928): a slice of a tuple is a tuple
len(fix)      # 3
```

### 3. Tuples are immutable

Like a string, and unlike a list, a tuple can't be changed after it's made. No item assignment, no `append`, no `pop`:

```python
fix[1] = 0.0        # TypeError: 'tuple' object does not support item assignment
```

To "change" a record, you build a **new** one: `fix = (fix[0], 0.0, fix[2])`.

**Why is that a good thing?** Remember aliasing from lesson 0.5: two names, one list, and a change through one name shows up through the other. With a tuple, that danger disappears. If your robot stores its home waypoint as `home = (42.3372, -71.0928)`, you can pass `home` to any function, and **no** function can quietly move it. On a robot, a home position, a calibration offset, or a geofence corner that changes by accident is a real hazard. Making it a tuple turns that bug into an immediate, loud `TypeError` instead of a silent drift.

### 4. Returning several values

A function can only return **one** object, but that object can be a tuple. So "returning two values" is really returning one tuple:

```python
def position(sentence):
    fields = sentence.strip().split(",")
    lat = to_degrees(fields[2], fields[3])
    lon = to_degrees(fields[4], fields[5])
    return lat, lon            # the comma packs them into one tuple
```

(`to_degrees` converts the NMEA `ddmm.mmmm` format to decimal degrees, with south and west negative. It's given to you in this lesson. You'll take it apart and derive it in lesson 0.9.)

### 5. Unpacking

**Unpacking** takes a tuple apart into separate names, **by position**:

```python
lat, lon = position(sentence)         # first item -> lat, second -> lon
time, lat, lon = fix                  # three slots, three names
```

The number of names must match the number of items. `time, lat = fix` (two names, three items) raises `ValueError`.

And here's the catch that makes this lesson's bug so common: **unpacking matches by position, not by meaning.** `lon, lat = position(sentence)` is perfectly legal Python. It just puts the latitude into a variable called `lon`. Both are floats, so nothing crashes. Your robot simply thinks it's somewhere else. Lat/lon order bugs are a classic in mapping code, partly because math habits say (x, y), and x (east-west) is *longitude*, while GPS habits say (lat, lon). **Always check the docstring for the order.**

### 6. Unpacking in a `for` loop

When you loop over a list of tuples, you can unpack each one right in the `for` line:

```python
track = [("152305.00", 42.33539, -71.0928), ("152306.00", 42.3354, -71.09282)]
for time, lat, lon in track:
    print(time, lat)
```

That's what `for i, h in enumerate(hdops)` was doing in lesson 0.5: `enumerate` produces `(index, item)` tuples, and you unpacked each one. You can even nest it: `for i, (time, lat, lon) in enumerate(track):`.

### 7. Swapping in one line

```python
lat, lon = lon, lat
```

Python evaluates the **entire right side first**, packing it into a temporary tuple, and only then unpacks into the names on the left. So neither value is overwritten too early. Without this, you'd need a temporary variable, like swapping two registers through a scratch register.

### 8. Tuple or list?

| Use a **tuple** when... | Use a **list** when... |
|---|---|
| it's one record with a fixed number of slots | it's a collection that grows or shrinks |
| each slot has its own meaning (time, lat, lon) | every item means the same kind of thing (satellite counts) |
| it should never change after it's made | you need to append, pop, or edit items |
| example: `(lat, lon)`, `(time, lat, lon)` | example: a log, a rolling window, a track |

The two work together all the time: a **track** is a *list* (it grows by one fix per second) of *tuples* (each fix has a fixed shape).

## Worked examples

Read each example, **predict what it prints**, then run it.

**Example 1: tuple basics.** Make one, read it, unpack it, and spot the one-item trap.

{{example:ex1}}

**Example 2: return a `(lat, lon)` pair, and swap in one line.** A function hands back two values as one tuple, and the caller unpacks it.

{{example:ex2}}

**Example 3: a track, a list of `(time, lat, lon)` records.** The list grows; each record stays fixed. Watch the unpacking in each `for` line.

{{example:ex3}}

**Example 4: robotics-realistic: why immutability helps.** The same "nudge north" helper, written for a list and for a tuple. One of them silently moves the robot's home waypoint.

{{example:ex4}}

## Predict, then check

{{predict:p1}}

{{predict:p2}}

{{predict:p3}}

## See it: records in motion

Press **Trace it** and step through. In the variables table, watch all three loop names change together, and watch the swap happen in one step.

{{viz:v1}}

And here is immutability doing its job. The last line is meant to fail.

{{viz:v2}}

## Common beginner mistakes

1. **Swapping lat and lon.** Unpacking matches by position, not by name. `lon, lat = position(s)` runs fine and gives wrong answers. Check the order in the docstring.
2. **The one-item tuple.** `(8)` is an int. Write `(8,)`.
3. **Trying to edit a tuple.** `fix[1] = 0.0` is a `TypeError`. Build a new tuple instead.
4. **Wrong number of names.** `time, lat = fix` on a 3-item tuple raises `ValueError`. One name per slot.
5. **Swapping with two lines.** `lat = lon` then `lon = lat` leaves both equal. Use `lat, lon = lon, lat`.
6. **Starting a running min/max at 0.** If every longitude is negative (anywhere west of Greenwich, like Boston), a max that starts at 0 stays 0. Start from the first real value.
7. **Using a list for a fixed record.** It works until something appends to it or edits it by accident. A tuple makes that impossible.

## Challenge: fix records and a bounding box

`to_degrees(ddmm, hemisphere)` is given in the starter. Keep it and use it. Write:

- `fix_record(sentence)`: return a **tuple** `(utc_time, lat, lon)` from a GGA sentence (any talker). `utc_time` is the text of field 1; `lat` and `lon` are signed decimal degrees from `to_degrees(field 2, field 3)` and `to_degrees(field 4, field 5)`. Return `None` if the sentence isn't GGA, has fewer than 15 fields, or its latitude or longitude field is empty.
- `bounding_box(records)`: given a list of `(utc_time, lat, lon)` records, return `((min_lat, min_lon), (max_lat, max_lon))`, the south-west and north-east corners of the smallest rectangle that contains them all. Return `None` for an empty list.

The hidden tests check the tuple type, the lat-before-lon order, southern and western hemispheres, and a track where every longitude is negative.

{{challenge}}

## Find the bug

{{bug}}

## Explain it back

{{explain}}
