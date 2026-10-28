## Why lists?

So far you've handled one sentence at a time. A real GPS log is hundreds of sentences, one per second, and a driver has to answer questions about **many** readings: How many satellites did each fix have? What was the worst HDOP in the last minute? What were the last 5 altitudes, so I can smooth them?

You've actually used a list already: `split(",")` returns one. In this lesson you'll learn to build your own, read and slice them safely, and avoid the two bugs that bite every beginner: **off-by-one indexes** and **aliasing** (two names for one list).

### The EE view: a list is a buffer

Think of a list as a block of RAM holding a **buffer of samples**, like the ring buffer a UART driver fills with received bytes:

| List idea | Hardware idea |
|---|---|
| `readings = []` | Allocate an empty buffer |
| `readings.append(12.3)` | Write the next sample at the end |
| `readings[0]` | Read the sample at address offset 0 |
| `len(readings)` | How many samples are stored |
| `readings.pop(0)` | Drop the oldest sample (like a shift register shifting one bit out) |
| `b = readings` | A second pointer to the **same** buffer (not a copy!) |

That last row is where the bugs live. Keep it in mind.

## Lists: the ideas you need

### 1. Building a list

Square brackets make a list. Items are separated by commas and can be any type:

```python
sats = [9, 3, 7, 8]               # ints
hdops = [1.1, 2.8, 1.4]           # floats
fields = "$GPGGA,123519".split(",")   # ['$GPGGA', '123519']: strings
log = []                          # an EMPTY list, ready to grow
```

The most common pattern in a sensor driver is **start empty, then append in a loop**:

```python
sats = []
for line in log_lines:
    fields = line.split(",")
    sats.append(int(fields[7]))   # int() turns the text "09" into the number 9
```

`append` adds one item to the **end**. It changes the list itself and returns nothing, so write `sats.append(x)`, never `sats = sats.append(x)` (that would replace your list with `None`, Python's "no value" object, which you'll meet properly in lesson 0.6).

### 2. Indexing: the last index is `len - 1`

Lists index exactly like strings: the first item is index **0**, and negative indexes count from the end.

```
fields:  '$GPGGA'  '123519'  '4807.038'  'N'  ...  '*47'
index:       0         1          2       3   ...   14     ← len(fields) is 15
negative:  -15       -14        -13     -12   ...   -1
```

A $GPGGA sentence has **15** fields, so the valid indexes are **0 to 14**. `fields[15]` doesn't exist, and Python raises **`IndexError`**. That's the classic off-by-one: `len()` counts items starting from 1, but indexes start from 0. The last item is always `fields[len(fields) - 1]`, which is exactly what `fields[-1]` means.

**Why this matters on a robot.** Serial lines get cut off: the receiver resets, a buffer overflows, or you start reading halfway through a sentence. A cut-off line like `"$GPGGA,152310.00,4220.12"` splits into only **3** fields. If your parser blindly reads `fields[7]`, it crashes, and a crashed GPS driver means a robot with no position. So you **check the length first**:

```python
if len(fields) > 7:          # index 7 exists only if there are at least 8 items
    sats = fields[7]
```

Read `len(fields) > 7` as "there are more than 7 items, so indexes 0 to 7 all exist." In general: **to use index `i`, you need `len(fields) > i`.** Python checks an `and` from left to right and stops at the first `False` side (this is called **short-circuiting**), so you can safely write `len(fields) > 7 and fields[7] != ""` in one condition: the second check never runs on a short list.

### 3. Slicing: always a new list

Slices work just like string slices: `[start:stop)`, start included, stop excluded, and slicing past the end never raises.

```python
alts = [12.3, 13.0, 12.8, 12.9, 13.1]
alts[1:3]     # [13.0, 12.8]
alts[-3:]     # [12.8, 12.9, 13.1]: the newest 3
alts[:2]      # [12.3, 13.0]: the oldest 2
alts[0:100]   # the whole list, no error
alts[:]       # the whole list, as a NEW copy
```

Two facts to remember:

- **A slice is a new list.** Changing the slice never changes the original. That makes `alts[:]` the standard way to copy a list.
- **The `-0` trap.** `alts[-n:]` gives the newest `n` items, *except* when `n` is 0. There's no such thing as negative zero for integers: `-0` is `0`, so `alts[-0:]` is `alts[0:]`, the **whole** list. If `n` can be 0, handle it separately.

### 4. `len`, `in`, `min`, `max`, `sum`

| Expression | Result | Note |
|---|---|---|
| `len(sats)` | number of items | `len([])` is 0 |
| `8 in sats` | `True` if some item `== 8` | compares **whole items** |
| `min(hdops)`, `max(hdops)` | smallest / largest item | crashes on an empty list |
| `sum(sats)` | total of the items | numbers only |

Careful with `in`: on a **string** it searches for text inside it (`"GGA" in line`), but on a **list** it compares whole items. `"GGA" in fields` is `False`, because no item is exactly `"GGA"` (the item is `"$GPGGA"`). And `9 in fields` is `False` because the items are strings: the number `9` is never equal to the text `"09"`.

### 5. Lists are mutable (strings were not)

In lesson 0.1 you learned that strings are immutable: `s[0] = "!"` is a `TypeError`. Lists are the opposite. You can change them in place:

```python
alts[2] = 20.0       # replace one item
alts.append(13.4)    # add to the end
alts.pop(0)          # remove (and return) the item at index 0
```

This is what makes lists useful as buffers. It's also what makes the next idea dangerous.

### 6. Aliasing: two names, one list

Here's the surprise. Assignment never copies a list:

```python
window = [12.3, 13.0]
backup = window          # NOT a copy
backup.append(12.8)
print(window)            # [12.3, 13.0, 12.8]  ← window changed too!
```

`backup = window` makes `backup` a second **name** for the same list, like landing two wires on the same terminal. There is only one list in memory. Whatever you do through one name, you see through the other. This is called **aliasing**.

You can ask Python directly whether two names refer to the same object with `is`:

```python
backup is window         # True: same list
window[:] is window      # False: a slice is a new list
backup == window         # True: == compares CONTENTS, `is` compares identity
```

When you need an independent copy (a snapshot of the buffer, a "before" version, a clamped version for plotting), make one explicitly with `window[:]` or `list(window)`.

Why did strings never have this problem? Because you can't change a string, it doesn't matter how many names point at it. Aliasing only bites with things that can change.

### 7. Looping over a list: `for` and `enumerate`

You already know `for` from lesson 0.4. Over a list, it hands you each item in order:

```python
for h in hdops:
    print(h)
```

Often you also need the **position** (which fix was bad?). You could loop over `range(len(hdops))` and index, but `enumerate` does it more clearly. It hands you `(position, item)` pairs, and you catch both:

```python
for i, h in enumerate(hdops):
    if h > 2.0:
        print("fix", i, "has a poor HDOP:", h)
```

`enumerate` starts counting at 0, so `i` lines up with the list indexes. (The `i, h` part is called **unpacking**. You'll see exactly how it works in lesson 0.7.)

## Worked examples

Read each example, **predict what it prints**, then run it. Change things and re-run.

**Example 1: a sentence's fields are a list.** Indexing, slicing, `len`, and `in` on the list that `split` gives you.

{{example:ex1}}

**Example 2: collect satellites and HDOP from a log.** Start empty, append in a loop, then summarize with `min`, `max`, `sum`, and `enumerate`. (HDOP, horizontal dilution of precision, measures how good the satellite geometry is. Lower is better; above about 2 is poor.)

{{example:ex2}}

**Example 3: a rolling window of altitudes, and an aliasing surprise.** Keep the newest 3 readings for a moving average, the way a driver smooths noisy altitude. Then watch what happens to `saved` versus `copy`.

{{example:ex3}}

**Example 4: robotics-realistic: cut-off lines.** This is defensive indexing in a real driver: check the length (and for an empty field) before you read an index.

{{example:ex4}}

## Predict, then check

Commit to an answer before you run anything.

{{predict:p1}}

{{predict:p2}}

{{predict:p3}}

## See it: names and lists

Press **Trace it** and step through. In the variables table, watch which names change when `log.append(12.8)` runs.

{{viz:v1}}

And here is the "find the worst fix" pattern, step by step. Watch `i` and `h` move together.

{{viz:v2}}

## Common beginner mistakes

1. **Off-by-one at the end.** The last index is `len(x) - 1`. `x[len(x)]` is always an `IndexError`. Use `x[-1]` for the last item.
2. **Indexing before checking the length.** A cut-off serial line has fewer fields. Check `len(fields) > i` before `fields[i]`.
3. **`x = x.append(item)`.** `append` changes the list and returns `None`. Just write `x.append(item)`.
4. **Thinking `b = a` copies a list.** It doesn't. Both names are the same list. Copy with `a[:]`.
5. **`in` with the wrong type.** List items from `split` are strings. `9 in fields` is `False` even when `"09"` is there. Convert first, or compare with a string.
6. **The `-0` trap.** `x[-n:]` returns the whole list when `n` is 0.
7. **`min`/`max` on an empty list.** They raise `ValueError`. Make sure you collected at least one reading first.

## Challenge: satellites and a rolling window

Write two functions. (Fill in each body; functions are covered properly in lesson 0.6.)

- `satellite_counts(sentences)`: `sentences` is a list of NMEA lines. Return a **list of ints**: the satellite count (field 7) of each GGA sentence, in order. Any talker counts (`$GPGGA`, `$GNGGA`, ...). **Skip** a line if it isn't GGA, if it's too short to have a satellites field (cut off), or if its satellites field is empty. A no-fix sentence that says `00` satellites counts as `0`. Lines may have stray spaces or `\r\n`.
- `last_n(readings, n)`: return a **new** list with the newest `n` readings (the end of the list). If there are fewer than `n`, return them all. `last_n(readings, 0)` is `[]`. Don't change `readings`.

The hidden tests include cut-off lines, empty fields, other sentence types, and a check that your result isn't an alias of the input.

{{challenge}}

## Find the bug

{{bug}}

## Explain it back

{{explain}}
