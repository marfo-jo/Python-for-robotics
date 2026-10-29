## Why this matters

A GPS receiver sends its sentences over a UART at 9600 baud, often through a long cable next to motor drivers. Bits get flipped. A single corrupted digit can turn latitude `4807.038` into `4807.938`, a jump of 1.6 km, and a robot that trusts it will swerve toward a position it never had.

That's what the two hex digits after the `*` are for. In lesson 0.1 you sliced them out as text. In this lesson you'll **compute** them yourself and compare. If your answer doesn't match the receiver's, the sentence was corrupted, and your driver throws it away.

To compute the checksum you have to visit every character of the sentence, one at a time. That's the job of the `for` loop.

## The `for` loop

In lesson 0.3 you wrote loops like this:

```python
i = 0
while i < len(line):
    ch = line[i]
    ...
    i += 1
```

That's three parts you have to get right (initialize, condition, progress), and forgetting `i += 1` hangs the program. Walking through a sequence item by item is so common that Python has a loop that does all three for you:

```python
for ch in line:
    ...
```

Read it as "for each character `ch` in `line`". On each pass, Python puts the next item into the **loop variable** `ch` and runs the body. When there are no items left, the loop ends. There's no counter to forget and no way to run off the end. You can name the loop variable anything; `ch` for characters and `line` for lines are common.

A `for` loop works on anything that holds a sequence of items:

| Loop | `ch` / `line` / `i` takes the values |
|---|---|
| `for ch in "$GP":` | `'$'`, `'G'`, `'P'` |
| `for line in ["$GPGGA,...", "$GNRMC,..."]:` | each string in the list |
| `for i in range(3):` | `0`, `1`, `2` |

`break` works inside `for` loops too, exactly as in 0.3.

### `while` or `for`?

- Use **`for`** when you're visiting each item of something you already have (every character, every line, every number in a range). You know the number of passes in advance.
- Use **`while`** when you're waiting for a condition and don't know how many passes it will take (retry until a fix, wait until settled).

## `range`: counting without a counter

`range` produces a sequence of whole numbers. Like slicing, it **includes the start and excludes the stop** (half-open).

| Call | Values | Note |
|---|---|---|
| `range(5)` | 0, 1, 2, 3, 4 | starts at 0; 5 values |
| `range(2, 5)` | 2, 3, 4 | from 2 up to (not including) 5 |
| `range(1, 10, 4)` | 1, 5, 9 | step of 4 |
| `range(6, 0, -2)` | 6, 4, 2 | a negative step counts down; 0 is excluded |
| `range(3, 3)` | nothing | start == stop: zero passes |

`range(len(s))` gives every valid index of `s`: from 0 to `len(s) - 1`. Use it when you need the **position** as well as the character, such as "every character from index 1 up to the `*`": `range(1, star)`.

## Characters are numbers: `ord()`

Underneath, every character is stored as a number, its **ASCII code** (more generally, its Unicode code point). `ord(ch)` gives you that number. You've seen this table on every Arduino `Serial.write()` you've debugged:

| Character | `ord()` | Binary | Hex |
|---|---|---|---|
| `'$'` | 36 | `00100100` | `24` |
| `','` | 44 | `00101100` | `2C` |
| `'0'` | 48 | `00110000` | `30` |
| `'A'` | 65 | `01000001` | `41` |
| `'G'` | 71 | `01000111` | `47` |
| `'P'` | 80 | `01010000` | `50` |

Note that the digit `'0'` is the number 48, not 0. The checksum works on these codes, not on the meaning of the text.

## XOR: the `^` operator

You know XOR from digital logic: the output is 1 when the inputs **differ**.

| A | B | A XOR B |
|---|---|---|
| 0 | 0 | 0 |
| 0 | 1 | 1 |
| 1 | 0 | 1 |
| 1 | 1 | 0 |

In Python (and in C, C++, and Arduino), `^` applies XOR to two whole numbers **bit by bit**, like eight XOR gates side by side:

```
  'G'   01000111   (71)
^ 'P'   01010000   (80)
  ---------------
        00010111   (23 = 0x17)
```

**Warning:** `^` is **not** "to the power of". `5 ^ 3` is 6, not 125. Powers use `**`.

Three properties make XOR perfect for a checksum:

| Property | Example | Why it matters |
|---|---|---|
| `a ^ 0 == a` | `71 ^ 0 == 71` | Start the running checksum at 0: the first character passes through unchanged |
| `a ^ a == 0` | `71 ^ 71 == 0` | XOR twice cancels: the receiver can recompute and compare |
| order doesn't matter | `a ^ b == b ^ a` | the checksum depends on WHICH characters, not their order (that's also its weakness) |

### The parity analogy

A UART parity bit is the XOR of all the data bits in one byte: it's 1 if there's an odd number of 1s. Flip any single bit and the parity no longer matches.

The NMEA checksum does the same thing **sideways**. Stack every character of the body in a column and XOR them: bit 0 of the result is the parity of all the bit 0s, bit 1 is the parity of all the bit 1s, and so on. It's eight parity bits at once, one per bit column (sometimes called a longitudinal redundancy check). And it inherits parity's blind spot: two errors in the same bit column cancel out, and so does swapping two characters.

## Showing the result as hex

The checksum is a number from 0 to 255, but the sentence writes it as **exactly two uppercase hex digits**. You need to produce the same text to compare:

| Expression | Result | Use it? |
|---|---|---|
| `hex(23)` | `'0x17'` | no: has a `0x` prefix, lowercase, no padding (`hex(3)` is `'0x3'`) |
| `format(23, "02X")` | `'17'` | **yes** |
| `format(3, "02X")` | `'03'` | **yes**: `0` = pad with zeros, `2` = width 2, `X` = uppercase hex |
| `format(23, "08b")` | `'00010111'` | handy for printing bits while debugging |
| `int("7c", 16)` | `124` | hex text back to a number (base 16); works for upper or lower case |

## The algorithm

The checksum rule itself is part of the NMEA protocol. Here it is as a reference table. **You don't need to memorize it**: every question, challenge, and bug that depends on it shows it right next to it. Your job is the Python that carries it out.

{{ref:checksum}}

In Python, that becomes:

1. Strip the line (`\r\n` and spaces).
2. Find the `*`. If there's no `*`, or the line doesn't start with `$`, it's not a valid sentence.
3. XOR together every character **strictly between** the `$` and the `*`: indexes 1 up to (not including) the star. Start from 0.
4. Format the result with `"02X"` and compare it with the text after the `*`, uppercased.

> **Bridge to C.** In your Arduino firmware this exact loop is:
> `uint8_t cs = 0; for (int i = 1; i < star; i++) cs ^= line[i];`
> Same `^`, same start at 1, same stop before the star. When you write the C version in the C track, it'll look familiar.

## Worked examples

Predict each output line, then run. Then edit: change one character in a sentence and watch the checksum change.

**Example 1: `for` over characters and ranges.** Look closely at the stop values: they're never printed.

{{example:ex1}}

**Example 2: XOR, bits, and hex.** Check each line against the XOR truth table by hand. Then try your own pairs of characters.

{{example:ex2}}

**Example 3: the NMEA checksum, step by step.** This is the real algorithm on the classic GGA sentence. (The checksum happens to be 71, which is also `ord('G')`: a coincidence, not a rule.)

{{example:ex3}}

**Example 4: robotics-realistic: catching corruption, and what XOR misses.** A loop over received lines with the checksum loop inside it: a **nested** loop. The inner loop uses `range(1, star)` so it skips the `$` and the `*`. One line had a `'3'` corrupted into an `'8'` (3 bits flipped), and the checksum catches it. Another had two digits swapped, and the checksum **can't** see it. That's why some protocols use CRCs instead.

{{example:ex4}}

## Predict, then check

Commit to an answer before you run anything.

{{predict:p1}}

{{predict:p2}}

{{predict:p3}}

## See it: XOR one character at a time

Step through the checksum of a real `$GPVTG` sentence (course and speed over ground). Watch the bits of "checksum so far" flip as each character comes in.

{{viz:v1}}

Now trace the loop itself. Watch `i` and `total` in the variables table.

{{viz:v2}}

## Common beginner mistakes

1. **Including the `$` (or the `*`) in the checksum.** The checksum covers only the characters between them. Including `$` XORs in 0x24 and every valid sentence fails. Use `line[1:star]` or `range(1, star)`.
2. **Using `hex()` to format.** `hex(3)` is `'0x3'`: wrong prefix, wrong case, no padding. Use `format(total, "02X")`.
3. **Case-sensitive comparison.** Some receivers send `*7c`. Uppercase the received text before comparing.
4. **Crashing on a missing `*`.** `line.index("*")` raises `ValueError`, and `find` returns `-1`, which makes a slice like `line[1:-1]` silently wrong. Check for `-1` first and return `False`.
5. **Forgetting to strip.** The `\r\n` ends up after the checksum digits, so `"47\r\n"` never equals `"47"`.
6. **Treating `^` as a power.** `2 ^ 3` is 1, not 8. Powers are `**`.
7. **Starting the checksum at the wrong value.** Start at 0 (XOR's "do nothing" value), not at the first character AND then XORing it again (which cancels it out).
8. **Off-by-one ranges.** `range(1, star + 1)` includes the `*`; `range(0, star)` includes the `$`. Say the start and stop values out loud before you run.

## Challenge: validate the checksum

Write two functions. Fill in the body; functions are covered properly in 0.6.

- `xor_checksum(body)` returns the XOR of every character in `body` (the text between `$` and `*`) as exactly **two uppercase hex digits**, for example `"47"` or `"03"`. An empty body gives `"00"`.
- `checksum_ok(sentence)` returns `True` only if the sentence (after stripping) starts with `$`, contains a `*`, and the checksum of the characters between them equals the hex text after the `*` (compared in uppercase). For anything else it returns `False`, and it must **never crash**.

The hidden tests use real sentences, `\r\n` and spaces, lowercase hex, a corrupted character, a wrong or truncated checksum, a missing `*`, a missing `$`, and empty lines. The checksum rule table is shown next to the challenge. Use what you've learned: string methods, slicing, conditionals, and `for` loops with `ord()`, `^`, and `format()`.

{{challenge}}

## Find the bug

{{bug}}

## Explain it back

{{explain}}
