## Why start here?

Every GPS receiver you'll touch, from the one in your EECE5554 lab to the u-blox on a delivery robot, talks in **NMEA 0183 sentences**: lines of plain text sent over a serial (UART) link, about once per second. Here is a real one:

```
$GPGGA,123519,4807.038,N,01131.000,E,1,08,0.9,545.4,M,46.9,M,,*47
```

To a robot, that line is just a **string**: a sequence of characters. Before you can use the latitude, you have to pull it out of the string. That skill (slicing text apart reliably, even when the data is messy) is the foundation of every sensor driver you'll write in this course, including Sprint 1.

### The EE view: a sentence is a frame

If you've looked at a UART line on a scope, you already know the idea. A serial frame has a **start marker**, a **payload**, and an **integrity check** (a parity bit). An NMEA sentence works the same way, just at the text level:

| Part | Example | Job |
|---|---|---|
| Start marker | `$` | "A new sentence starts here" (like the start bit) |
| Talker ID | `GP` | Who is talking: `GP` = GPS, `GN` = multi-constellation, `GL` = GLONASS |
| Sentence type | `GGA` | What kind of data: `GGA` = fix data, `RMC` = recommended minimum |
| Fields | `123519,4807.038,N,...` | The payload, separated by commas |
| Checksum marker | `*` | "The integrity check follows" |
| Checksum | `47` | Two hex digits, like parity but stronger (you'll compute it in lesson 0.4) |
| End | `\r\n` | Carriage return + line feed. **Invisible, but it's really there.** |

That last row causes more real driver bugs than any other. Keep it in mind.

## Strings: the four ideas you need

### 1. Indexing: positions start at 0

Each character has a position called an **index**. The first character is index **0**, not 1. Think of bit numbering in a register: bit 0 is the first bit.

```
 $  G  P  G  G  A  ,  1  2  3 ...
 0  1  2  3  4  5  6  7  8  9      ← positive index (from the start)
```

`sentence[0]` is `'$'`, and `sentence[1]` is `'G'`. **Negative** indexes count from the end: `sentence[-1]` is the last character, and `sentence[-2]` is the second to last.

### 2. Slicing: `[start:stop]` gives you a piece

`sentence[1:6]` gives the characters from index 1 **up to but not including** index 6. That's `'GPGGA'`, five characters, because 6 − 1 = 5.

This "include the start, exclude the stop" rule (a **half-open** range) trips up nearly every beginner at least once. It's deliberate: it means `s[0:3] + s[3:6] == s[0:6]` with no overlap and no gap, just like adjacent address ranges in memory.

You can leave either end blank: `s[:3]` means "from the start", and `s[3:]` means "to the end". Slicing never crashes for out-of-range stops: `"abc"[1:100]` is just `'bc'`.

### 3. Strings are immutable

You **cannot change** a string in place. `sentence[0] = "X"` raises a `TypeError`. Every string method returns a **new** string and leaves the original alone, like reading from ROM: you can copy and modify the copy, but the original never changes. That's why you always write `line = line.strip()`, not just `line.strip()`.

### 4. Methods do the heavy lifting

| Method | What it does | Example |
|---|---|---|
| `len(s)` | number of characters (a function, not a method) | `len("$GP")` → `3` |
| `s.strip()` | remove whitespace (spaces, `\r`, `\n`, tabs) from **both ends only** | `" A\r\n".strip()` → `'A'` |
| `s.split(",")` | cut at every comma, giving a list of pieces | `"a,,b".split(",")` → `['a', '', 'b']` |
| `s.find("*")` | index of the first `*`, or `-1` if there isn't one | |
| `s.index("*")` | like `find`, but raises `ValueError` if it's missing | |
| `s.startswith("$")` | `True` or `False` | |
| `s.upper()` | all uppercase (hex checksums can arrive as `4a` or `4A`) | |
| `"GGA" in s` | `True` if the text appears anywhere in s | |

Notice in `split`: two commas in a row produce an **empty string** `''`. GPS receivers send empty fields all the time, for example when there's no fix yet. Your code must expect them.

### The $GPGGA field layout (a reference, not something to memorize)

After `sentence.split(",")`, each field of a GGA sentence sits at a fixed **index**. Index 0 is `'$GPGGA'` itself, so the first data field is index 1. Here's the full layout:

{{ref:gga}}

**You don't need to memorize this table.** Real engineers keep the protocol spec open while they code, and so will you: any question, challenge, or bug in this course that depends on a field position shows the table right next to it. What you *do* need to know is the Python skill: `split(",")` gives you a list, and you read a field with its index, for example `fields[6]` for fix quality, using the table to look up the number.

Two facts that matter for your code (both are in the table's notes):

- Empty fields **keep their position**. A no-fix sentence still has 15 items; some are just `''`. That's why `fields[6]` is always fix quality.
- The checksum is glued to the **last** field, so the last item of the split list contains `*`.

## Worked examples

Read each example, **predict what it prints**, then run it. Change things and re-run. Breaking the examples on purpose is the fastest way to learn.

**Example 1: indexing and slicing a real sentence.**

{{example:ex1}}

**Example 2: a line straight from a serial port.** Data read from a serial port arrives with `\r\n` on the end. Watch what that does to `len()` and to the last characters, and how `strip()` fixes it.

{{example:ex2}}

**Example 3: robotics-realistic: identify what's talking and find the checksum.** Real receivers mix talkers (`$GPGGA` from GPS-only units, `$GNGGA` from multi-constellation units) and sometimes send lowercase hex. This is the kind of defensive slicing a real driver does.

{{example:ex3}}

## Predict, then check

Commit to an answer before you run anything. Wrong predictions go into your review queue, so you'll see them again until they stick.

{{predict:p1}}

{{predict:p2}}

{{predict:p3}}

## See it: split a sentence apart

Edit the sentence below and watch the indexes, the slice, and the `split(",")` result update live. Try deleting a field so two commas touch, or move the slice bounds past the end.

{{viz:v1}}

And here is a step-through trace of string operations. Press **Trace it**, then step line by line. Watch the variables table: notice that `raw` **never changes**. Every method creates a new string.

{{viz:v2}}

## Common beginner mistakes

1. **Off-by-one in slices.** Remember that `s[1:6]` stops *before* index 6. To get characters 1 to 5 inclusive, the stop is 6.
2. **Forgetting the invisible `\r\n`.** `line[-2:]` on a raw serial line gives `'\r\n'`, not the checksum. Strip first.
3. **Calling a method without keeping the result.** `line.strip()` alone does nothing useful, because strings are immutable. Write `line = line.strip()`.
4. **Counting fields by hand.** Use `split(",")` and index the list. Don't count characters.

## Challenge: identify a sentence

Write three small functions. (A function is like a circuit block with input and output terminals: `sentence` goes in, the `return` value comes out. You'll learn functions properly in lesson 0.6. For now, just fill in the expression after `return`.)

- `talker_id(sentence)` returns the 2-letter talker ID, for example `'GP'` from `'$GPGGA,...'`.
- `sentence_type(sentence)` returns the 3-letter type, for example `'GGA'`.
- `checksum_text(sentence)` returns the two checksum characters after the `*`, **uppercased**, for example `'47'`, or `'4A'` when the sentence ends in `*4a`.

The hidden tests use real-world messiness: stray spaces, a trailing `\r\n`, lowercase hex, and talkers other than `GP`. Use only what this lesson covered: indexing, slicing, and string methods.

{{challenge}}

## Find the bug

{{bug}}

## Explain it back

{{explain}}
