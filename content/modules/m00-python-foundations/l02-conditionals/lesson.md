## Why this matters

In lesson 0.1 you sliced a sentence apart. But a real GPS driver can't just slice every line it receives and publish the result. The serial port delivers a stream of **mixed** sentences: `$GPGGA`, `$GNRMC`, `$GPGSV`, half-received garbage at startup, and fixes with quality `0` (no fix) where every position field is empty. A driver that blindly publishes `fields[2]` as a latitude would send `''` or the wrong data to the rest of the robot.

So before your driver uses a sentence, it has to **decide**:

- Is this a GGA sentence at all?
- Does the receiver actually have a fix? What kind (plain GPS, DGPS, RTK)?
- Are enough satellites in view to trust it?

Deciding is what **conditionals** do. If you've written PLC ladder logic, you already think this way: a rung is a condition (contacts in series = AND, in parallel = OR, a normally-closed contact = NOT), and the coil only energizes when the condition is true. Python's `if` is the same idea, written as text.

## Booleans: the result of a question

A comparison is a **question** that Python answers with one of two values: `True` or `False`. These are the **booleans** (type `bool`), the software version of a logic HIGH and LOW.

| Operator | Question | Example | Result |
|---|---|---|---|
| `==` | equal? | `8 == 8` | `True` |
| `!=` | not equal? | `"GGA" != "RMC"` | `True` |
| `<` `>` | less / greater? | `3 > 4` | `False` |
| `<=` `>=` | less or equal / greater or equal? | `4 >= 4` | `True` |

### `=` stores, `==` compares

This is the single most common typo in every language that uses it (C, C++, Arduino, Python):

- `quality = "1"` **stores** the text `"1"` in the variable `quality`. It's an instruction.
- `quality == "1"` **asks** whether `quality` holds `"1"`. It's a question with a `True`/`False` answer.

In C and Arduino, `if (x = 5)` compiles and silently assigns 5 (a classic firmware bug). Python is stricter: `if quality = "1":` is a `SyntaxError`, so the program won't even start. That's a gift: the error points straight at the line.

### Text is not a number

Every NMEA field is **text**, even when it looks like a number. The fix quality is the string `"1"`, not the integer `1`, and the satellite count is `"08"`, not `8`. Python never treats them as equal:

```python
"1" == 1        # False (and no error to warn you!)
"08" == "8"     # False: different text
int("08") == 8  # True: convert first, then compare
```

Two conversion functions turn text into numbers:

| Function | Example | Result |
|---|---|---|
| `int(text)` | `int("08")` | `8` (leading zeros are fine) |
| `float(text)` | `float("11.1")` | `11.1` |

Both raise `ValueError` if the text isn't a number, **including the empty string**: `int("")` crashes. Since empty fields are everywhere in NMEA, you must check a field is non-empty before converting it. You'll see how below.

So you have a choice: compare the text to text (`quality == "1"`), or convert and compare numbers (`int(sats) >= 4`). Use text for **codes** (fix quality, sentence type) and numbers for **quantities** you compare with `<` or `>` (satellites, voltage).

## `if`, `elif`, `else`

```python
if quality == "0":
    status = "no fix"
elif quality == "1":
    status = "GPS"
else:
    status = "other"
```

- The line ends with a **colon** `:`.
- The body is **indented** (4 spaces). Indentation isn't decoration in Python: it's how Python knows which lines belong to the branch. The first un-indented line after it is outside the `if`.
- `elif` means "else, if". You can have as many as you need.
- `else` catches everything that didn't match. It has no condition.

**Python checks the conditions from top to bottom and runs only the first branch whose condition is True. Then it skips the rest of the chain.** Exactly one branch runs (or none, if there's no `else`). That's why the **order** of the branches matters, and getting it wrong is a classic bug (you'll fix one at the end of this lesson).

Think of it like a priority encoder: several inputs may be active, but only the highest-priority one wins.

## `and`, `or`, `not`: logic gates

You know these from digital logic. Python spells them as words:

| A | B | `A and B` | `A or B` | `not A` |
|---|---|---|---|---|
| False | False | False | False | True |
| False | True | False | True | True |
| True | False | False | True | False |
| True | True | True | True | False |

```python
line[3:6] == "GGA" and quality != "0"    # both must hold (series contacts)
quality == "4" or quality == "5"         # either one is enough (parallel contacts)
not line.startswith("$")                 # flips the result (NC contact)
```

`not` binds tighter than `and`, which binds tighter than `or`. When in doubt, add parentheses: `(a or b) and c`.

### Short-circuiting: stop as soon as the answer is known

Python evaluates `and` and `or` **left to right and stops early**:

- `A and B`: if `A` is False, the result is already False, so **`B` is never evaluated**.
- `A or B`: if `A` is True, the result is already True, so `B` is never evaluated.

This isn't just a speed trick. It's a safety feature you'll use constantly:

```python
if sats and int(sats) >= 4:      # safe: int() only runs if sats is non-empty
if int(sats) >= 4 and sats:      # crashes on an empty field: int("") runs first
```

Put the **guard** on the left and the risky operation on the right.

## Comparison chains

To check that a voltage is inside a band, you could write `10.5 <= volts and volts < 11.1`. Python lets you write it the way you'd write it in math:

```python
10.5 <= volts < 11.1
```

A chain `a <= x < b` means exactly `a <= x and x < b`. Watch the boundaries: at exactly `11.1`, `volts < 11.1` is False. Decide on purpose which band each boundary value belongs to, and use `<=` on one side and `<` on the other so there's no gap and no overlap (the same half-open idea as slicing in 0.1).

## Truthiness: empty fields are False

An `if` doesn't strictly need a boolean. Python can judge any value as "truthy" or "falsy":

| Value | Truthy or falsy? |
|---|---|
| `""` (empty string) | **falsy** |
| `"0"`, `" "`, `"GGA"` (any non-empty string) | truthy |
| `0`, `0.0` | falsy |
| any other number | truthy |
| `True` / `False` | themselves |

`bool(x)` shows you the judgment: `bool("")` is `False`.

This is perfect for NMEA, where an empty field means "no data":

```python
if sats:                 # same as: if sats != ""
    print(int(sats))
```

**But there's a trap.** The fix-quality field for "no fix" is the text `"0"`, which is **not empty**, so it's truthy. `if quality:` means "the field has something in it", NOT "the receiver has a fix". To test for a fix, compare: `quality != "0"`.

## `return` inside a branch

In lesson 0.1, each function was a single `return` line. Now your function body will have several lines. Two facts you need for the challenge (functions get a full lesson in 0.6):

- The body is everything indented under the `def` line.
- When Python reaches a `return`, the function **stops immediately** and hands back that value. So you can put a `return` inside each branch: the first branch that runs decides the answer.

```python
def describe(quality):
    if quality == "0":
        return "no fix"      # stops here when quality is "0"
    return "something else"
```

## Reference: GGA fields and fix quality codes (not something to memorize)

The examples, the trace, and the challenge read two fields of a GGA sentence: the fix quality and the satellite count. You met the field layout in 0.1. Here it is again, followed by what each fix quality code means:

{{ref:gga}}

{{ref:fixquality}}

**You don't need to memorize either table.** They're reference material, like a datasheet you keep open next to the code. Every question, challenge, and bug in this course that depends on a field position or a code shows the table right next to it. What you *do* need is the Python skill: `fields[6]` is **text** like `"1"`, so you compare it with text, and you branch on it with an `if`/`elif` chain.

For context only (no question depends on it): a plain GPS fix is good to a few meters, DGPS to about 1 m, RTK fixed to about 2 cm, and RTK float to decimeters. Rarer codes (`3`, `7`, `8`) exist too, which is why a robust classifier ends with an `else` that catches any code it doesn't recognize.

## Worked examples

Predict each output line before you run it. Then change a value and re-run.

**Example 1: comparisons, booleans, and comparison chains.** Note that comparing `"8"` with `8` gives no error, just a quiet `False`. That silence is what makes it dangerous.

{{example:ex1}}

**Example 2: truthiness and empty NMEA fields.** A receiver with no fix sends mostly empty fields. Watch which fields are truthy, and notice that `"0"` is truthy.

{{example:ex2}}

**Example 3: robotics-realistic: validate, then classify.** This is the decision logic of a real GPS driver: reject anything that isn't GGA, then branch on the quality code, then check the satellite count with a short-circuit guard. The talker is `GN` (multi-constellation), so we check `line[3:6]` rather than the whole `$GPGGA` prefix.

{{example:ex3}}

**Example 4: battery bands and hysteresis.** Battery monitoring is the same if/elif pattern with numbers. The band checks go from the top down, so the `elif volts >= 10.5` branch only ever sees voltages below 11.1. The second half adds **hysteresis**. You know it from a Schmitt trigger: separate thresholds for switching on and off, so a noisy signal near one threshold doesn't make the output chatter. A battery's voltage rises when the load drops (the motors stop while docking), so a single threshold would toggle "go dock" on and off. With two thresholds (start below 10.5 V, stop above 11.4 V), the decision depends on the current **state** as well as the voltage.

{{example:ex4}}

## Predict, then check

Commit to an answer before you run anything.

{{predict:p1}}

{{predict:p2}}

{{predict:p3}}

## See it: trace the decision

Press **Trace it**, then step line by line. Watch which lines get highlighted and which get skipped.

{{viz:v1}}

And here's the no-fix sentence from Example 2. Look at how many fields are empty, and at the one that isn't.

{{viz:v2}}

## Common beginner mistakes

1. **`=` instead of `==`.** `if quality = "1":` is a `SyntaxError`. One `=` stores, two compare.
2. **Comparing text to a number.** `quality == 1` is always `False`, because the field is the string `"1"`. Compare text to text (`quality == "1"`), or convert with `int()` first.
3. **`x == "1" or "2"`.** The right side `"2"` is a whole condition by itself, and it's always truthy. Write `x == "1" or x == "2"`.
4. **Treating `"0"` as false.** `if quality:` is True for `"0"`. Truthiness only tells you whether the field is empty.
5. **Converting before checking.** `int(sats)` crashes on an empty field. Guard it: `if sats and int(sats) >= 4:`.
6. **Wrong branch order.** An `if`/`elif` chain stops at the first True condition. If a wide condition (`volts < 11.1`) comes before a narrow one (`volts < 10.5`), the narrow branch can never run.
7. **Off-by-one at boundaries.** "At least 4 satellites" is `>= 4`, not `> 4`. Test the exact boundary value every time.

## Challenge: is this fix usable?

Write two functions. Fill in the body; functions are covered properly in 0.6.

- `fix_status(sentence)` returns one of `"not GGA"`, `"no data"` (quality field empty), `"no fix"`, `"GPS"`, `"DGPS"`, `"RTK fixed"`, `"RTK float"`, or `"other"` (any other code).
- `is_usable(sentence, min_sats)` returns `True` only when the sentence is GGA, the quality is a real fix (`"1"`, `"2"`, `"4"`, or `"5"`), the satellite field is not empty, and there are **at least** `min_sats` satellites. Otherwise it returns `False`, and it must never crash.

A sentence counts as GGA if, after stripping, it starts with `$` and characters `[3:6]` are `GGA` (so `$GPGGA` and `$GNGGA` both count). The GGA field table and the fix quality table are shown next to the challenge: look up the field positions there. The hidden tests use whitespace, `\r\n`, empty fields, a missing `$`, non-GGA sentences, and exact boundary values. Use only what you've learned so far: string methods, slicing, `split`, `int()`, and conditionals.

{{challenge}}

## Find the bug

{{bug}}

## Explain it back

{{explain}}
