## Why this lesson matters

So far, when bad input reached your code, one of two things happened: you guarded against it with an `if`, or the program **crashed** with a red block of text. On a robot, both matter. A GPS driver that crashes on the first corrupted sentence takes the whole navigation stack down with it. A driver that silently ignores every problem hides faults you need to know about.

Python's answer is **exceptions**. When something goes wrong, the code that detects the problem **raises** an exception, and code further up that knows what to do about it **catches** it. In this lesson you'll learn to:

1. **Read a traceback** quickly and correctly, bottom-up, so a crash tells you exactly where to look.
2. **Catch** the specific errors you expect (`ValueError`, `IndexError`) and keep going.
3. **Raise** your own `ValueError` with a clear message when *your* function gets bad input.
4. Use `else` and `finally` for the "it worked" and "always do this" paths.

### The PLC view: faults and fault handlers

You already know this pattern. A PLC drive reports a fault code (overcurrent, encoder loss) instead of quietly producing wrong output. The fault propagates up to whoever is responsible: a fault routine may clear a known, harmless fault and continue, but an unknown fault stops the machine and shows the code on the HMI so a technician can look at it. Exceptions are the same idea:

| PLC | Python |
|---|---|
| Fault detected in a module | `raise ValueError("checksum mismatch")` |
| Fault code and description | exception **type** and **message** |
| Fault routine for a known fault | `try: ... except ValueError: ...` |
| Unknown fault halts the machine and shows on the HMI | an uncaught exception stops the program and prints a **traceback** |
| Fault history: which rung, called from where | the traceback's list of frames |

The rule that keeps both systems safe is the same: **handle only the faults you understand, and let everything else stop the machine loudly.**

## Reading a traceback, bottom-up

Here is a small program that converts the latitude of two sentences. The first works. The second is a no-fix sentence with empty fields:

```python
def to_degrees(text):
    return int(text[:2]) + float(text[2:]) / 60


def parse_lat(sentence):
    fields = sentence.split(",")
    return to_degrees(fields[2])


print(parse_lat("$GPGGA,123519,4807.038,N,01131.000,E,1,08,0.9,545.4,M,46.9,M,,*47"))
print(parse_lat("$GPGGA,,,,,,0,00,,,M,,M,,*66"))
```

It prints `48.1173`, then the site shows this:

```
Traceback (most recent call last):
  File "solution.py", line 11, in <module>
    print(parse_lat("$GPGGA,,,,,,0,00,,,M,,M,,*66"))
  File "solution.py", line 7, in parse_lat
    return to_degrees(fields[2])
  File "solution.py", line 2, in to_degrees
    return int(text[:2]) + float(text[2:]) / 60
ValueError: invalid literal for int() with base 10: ''
```

"Most recent call last" is the key phrase: the newest information is at the **bottom**. So read it bottom-up, in three steps.

**Step 1: the last line is the type and the message.** `ValueError` is the kind of fault; `invalid literal for int() with base 10: ''` is the description. The `''` at the end is gold: `int()` was handed an **empty string**. Before you even look at the code, you know the story: some field was empty.

**Step 2: the last `File "solution.py"` line is where it happened.** `line 2, in to_degrees`, and the line itself is printed under it: `return int(text[:2]) + ...`. That's the line that was running when the fault occurred. In the editor, the site highlights this line for you.

**Step 3: the frames above are how it got there.** Each `File ... line N, in name` entry is one function call that was still in progress. Read upward: `to_degrees` was called by `parse_lat` at line 7, which was called by the main program (`<module>`) at line 11, with the no-fix sentence. That's the **call stack**: the chain of calls, like tracing a signal back through each stage of a circuit to its source.

**Step 4: find the real cause, which is often earlier.** The crash is reported in `to_degrees`, but `to_degrees` isn't wrong: it was given bad input. The real decision ("what should happen when there is no fix?") belongs in `parse_lat`, or whoever reads the sentence. A traceback tells you where the fault was *detected*; you still have to think about where it was *caused*.

### The same traceback on your laptop

When you run code locally in VS Code or PowerShell, the traceback has the same structure with three differences:

- File names are **full paths**, like `C:\Users\you\...\my-solutions\m00\gps.py`, instead of `solution.py`.
- Python 3.11 and newer add **`^^^^^` markers** under the exact part of the line that failed (here, under `int(text[:2])`). Very helpful when one line does several things.
- You may see frames from **other files** (Python's own libraries, or pytest). Skip past them to the last frame from *your* file. The site hides them for you.

And one more you'll meet: if an exception is raised **inside an `except` block**, Python prints *both* tracebacks, joined by `During handling of the above exception, another exception occurred:`. Read the bottom one first (that's what stopped the program); the top one is the original cause, shown as context. It's not a second bug.

### The usual suspects

| Type | Means | Typical robotics cause |
|---|---|---|
| `ValueError` | right type, wrong content | `int('')` on an empty field, `float('x9')` on garbled text |
| `IndexError` | that position doesn't exist | `fields[7]` on a truncated sentence with only 3 fields |
| `KeyError` | that key isn't in the dict | `fix["altitude"]` when the key is `"alt"` |
| `TypeError` | wrong type for the operation | `"10.2" + 1`: a field you forgot to convert |
| `ZeroDivisionError` | divided by zero | `dt == 0` on the first loop pass, or averaging zero samples |
| `FileNotFoundError` | no file at that path | the working-directory problem from lesson 0.10 |

## Catching exceptions: `try` / `except`

```python
try:
    sats = int(fields[7])        # the code that might fail
except ValueError:
    sats = 0                     # what to do if it raises ValueError
```

Python runs the `try` block. If a line in it raises `ValueError`, Python **immediately jumps** to the `except ValueError:` block; the rest of the `try` block is skipped. If nothing is raised, the `except` block is skipped. Either way, the program then carries on after the whole statement.

### Catch specific types, never everything

An `except` clause only catches the types it names. `except ValueError:` does **not** catch an `IndexError`, which keeps going up and stops the program. That's a feature: you list exactly the faults you expect and know how to handle.

You can handle different faults differently, or several the same way:

```python
try:
    sats = int(fields[7])
except ValueError:               # field 7 exists but isn't a number
    ...
except IndexError:               # field 7 doesn't exist at all
    ...

try:
    sats = int(fields[7])
except (ValueError, IndexError) as err:    # either one; err is the exception object
    print(type(err).__name__, err)
```

**Never write a bare `except:`** (or `except Exception:` to mean "anything"). It catches *everything*, including your own bugs: a typo in a variable name (`NameError`), a `None` where a string should be (`AttributeError`), even the stop button (`KeyboardInterrupt`). It's like wiring a fault relay to auto-reset on every fault, including the ones that mean "the motor is on fire". Your program keeps running and produces wrong answers, and you never find out why.

### Keep the `try` block small

Put only the lines that can raise the expected error inside `try`. Everything you put in there is "protected", so a mistake in an unrelated line gets caught and silently treated as bad input. And watch out for lines that **change state** before the risky line: if `count += 1` runs and then `int()` fails, the count has already gone up. (That is exactly the bug at the end of this lesson.)

## Raising your own exceptions

When your function receives input it can't handle, don't return a strange value like `None`, `-1`, or `0`: the caller may not check it, and the bad value flows on into the rest of the system. **Raise** an exception with a message that says what was wrong:

```python
def parse_quality(text):
    if text == "":
        raise ValueError("fix quality field is empty")
    quality = int(text)
    if quality < 0 or quality > 8:
        raise ValueError(f"fix quality must be 0 to 8, got {quality}")
    return quality
```

`raise` stops the function right there, like `return`, but instead of handing back a value, it sends the exception up to the caller. `ValueError` is the right type for "the argument had the right type but a bad value". Write the message for the person reading the error log at 2 a.m.: say what was expected and what you got.

The caller reads your message with `except ValueError as err:`, and `str(err)` (or just putting `err` in an f-string) gives the message text.

**Converting one exception into another.** Sometimes the error Python raises isn't the one you want your caller to deal with. A truncated sentence causes an `IndexError` deep inside your parser, but to the caller it's just "bad input". Catch it and raise your own:

```python
try:
    alt = float(fields[9])
except IndexError:
    raise ValueError("too few fields")
```

Now the caller only has to catch `ValueError` for every kind of bad sentence.

## `else` and `finally`, briefly

A `try` statement can have two more optional parts:

```python
try:
    alt = parse_alt(line)
except ValueError as err:
    print("skipped:", err)
else:
    alts.append(alt)      # runs ONLY if the try block raised nothing
finally:
    checked += 1          # runs ALWAYS: after success, after a caught error, even after an uncaught one
```

`else` keeps the `try` block small: the "it worked, now use the result" code goes in `else`, so it isn't accidentally protected by the `except`. `finally` is for cleanup that must happen no matter what, like closing a serial port or releasing a motor driver. (The `with` statement from lesson 0.10 is a tidy built-in `finally` for files.)

## Worked examples

**Example 1: catching ValueError on real fields.** Empty, garbled, padded, and decimal text. Note that `int()` ignores surrounding spaces but refuses `'7.0'`.

{{example:ex1}}

**Example 2: ValueError vs IndexError.** A field that exists but isn't a number is a different fault from a field that doesn't exist at all.

{{example:ex2}}

**Example 3: raising your own ValueError, with `else`.** The messages printed are the ones *you* wrote.

{{example:ex3}}

**Example 4: robotics-realistic: a robust altitude parser over a messy log.** Junk, a no-fix sentence, and a truncated sentence are each rejected with a clear reason, and the good data still gets through.

{{example:ex4}}

## Predict, then check

{{predict:p1}}

{{predict:p2}}

{{predict:p3}}

## See it: a crash, frame by frame

Before you trace, write your prediction: on the second call, which function will be running when it fails, what will the call stack look like, and what is the error type? Then step through and watch the **call stack** grow as each function is called. The last step shows the traceback.

{{viz:v1}}

And here is the normal flow of `try` / `except` / `else` / `finally` over three inputs. Watch which blocks run for each one.

{{viz:v2}}

## Common beginner mistakes

1. **Reading the traceback top-down.** The top is the oldest call. Start at the bottom: type and message, then the last line from your file.
2. **Bare `except:`.** It hides real bugs. Name the types you expect.
3. **Catching the wrong type.** `except ValueError` doesn't catch `IndexError`. Check the last line of the traceback for the real type.
4. **A huge `try` block.** Protect only the risky lines. Use `else` for the rest.
5. **Changing state before the risky line in a `try`.** If the conversion fails, the earlier `count += 1` already happened.
6. **Returning `None` (or -1, or 0) instead of raising.** The caller can't tell *why* it failed and may not even notice.
7. **Vague messages.** `ValueError("bad")` helps nobody. Say what was wrong: `"checksum mismatch"`, `"no fix"`.
8. **Catching an exception and doing nothing (`pass`) without counting or logging it.** Skipping bad data is fine; skipping it *silently* is how you lose a fault you needed to see.

## Challenge: a robust GGA parser

Write two functions.

`parse_gga(sentence)` strips the sentence, checks it, and returns a dict `{"time": str, "quality": int, "sats": int, "hdop": float, "alt": float}` from fields 1, 6, 7, 8, and 9. For bad input it must **raise `ValueError`** with your own message, checked in this order:

| Problem | Message |
|---|---|
| doesn't start with `$`, or has no `*` | `"not an NMEA sentence"` |
| checksum doesn't match (upper- or lowercase hex is fine) | `"checksum mismatch"` |
| a valid sentence of another type (check characters 3 to 5) | `"not a GGA sentence"` |
| a field you need doesn't exist | `"too few fields"` (catch the `IndexError` and raise this instead) |
| fix quality is 0 | `"no fix"` |

Check the fix quality **before** converting the satellites, HDOP, and altitude: a no-fix sentence has empty fields there, and you want the clear `"no fix"` message, not a conversion error. If a number won't convert (like a satellites field of `'x9'`), Python's own `ValueError` is fine: let it go up.

`parse_fixes(lines)` takes a list of lines and returns `(fixes, errors)`: the list of dicts for the good lines, and a list of `(line_number, message)` tuples for the bad ones. Line numbers start at **1**. Blank lines are skipped (not errors), but they still count when numbering. Catch **only** `ValueError`: if the list contains something that isn't a string at all, that's a bug in the caller, and it must crash.

The tests check exception **types**, and the **messages you wrote**, never Python's own messages.

{{challenge}}

## Find the bug

{{bug}}

## Explain it back

{{explain}}
