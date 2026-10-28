## Why this matters

In lesson 0.2 your code made **one** decision about **one** sentence. A real GPS driver never stops: it reads a line, decides what to do with it, then reads the next, about once per second for as long as the robot is on. And at power-up, it has to **keep trying** until the receiver finally gets a fix, which can take 30 seconds or more on a cold start.

You've seen this shape before. A PLC runs a **scan cycle**: read inputs, solve the logic, write outputs, repeat, forever. An Arduino sketch has `loop()`, which runs again and again. Python's version is the `while` loop: repeat a block of code **while** a condition stays true.

Loops are also where beginners write their first bugs that make a program **hang**: an infinite loop that never ends. On a robot, a hung loop means a frozen driver, stale data, and a robot driving on its last known position. This lesson is as much about making loops **stop correctly** as about making them run.

## The `while` loop

```python
countdown = 3
while countdown > 0:
    print("T minus", countdown)
    countdown = countdown - 1
print("done")
```

How Python runs it:

1. **Check the condition.** If it's False, skip the whole body and continue after the loop.
2. If it's True, **run the body** (every indented line) from top to bottom.
3. **Go back to step 1.**

The condition is only checked at the **top**, once per pass. Changing a variable in the middle of the body doesn't stop the loop right away: the rest of the body still runs, and the check happens at the next pass. If the condition is False the very first time, the body runs **zero times**.

### The three parts every loop needs

Every loop that ends correctly has three parts. Learn to point at each one:

| Part | In the countdown | Job |
|---|---|---|
| **Initialize** | `countdown = 3` | Set up the variable the condition depends on, before the loop |
| **Condition** | `countdown > 0` | Checked before every pass: "keep going?" |
| **Progress** | `countdown = countdown - 1` | Changes the variable so the condition eventually becomes False |

If the progress step is missing, or it moves the variable the wrong way, the condition never changes and the loop never ends.

### `+=` and friends

Counters are so common that Python has shorthand:

| Shorthand | Means |
|---|---|
| `i += 1` | `i = i + 1` |
| `n -= 2` | `n = n - 2` |
| `total += x` | `total = total + x` |

## A list as a stand-in for the serial port

You haven't met lists properly yet (that's lesson 0.5), but you've already used one: `split(",")` returns a list. For this lesson you only need four facts:

```python
lines = ["$GPGGA,...", "", "$GNRMC,..."]   # square brackets, items separated by commas
len(lines)        # 3: number of items
lines[0]          # the first item (index 0, just like strings)
lines[3]          # IndexError: there is no item at index 3
```

We'll use a list of lines to **simulate** reading a serial port: `lines[i]` is the i-th line that arrived. Instead of "read the next line", the code says "look at `lines[i]`, then `i += 1`". The last valid index is `len(lines) - 1`, so a loop that reads `lines[i]` must keep `i < len(lines)`.

## Infinite loops: how they happen and how to stop them

An **infinite loop** is a loop whose condition never becomes False. The three classic causes:

1. **Forgetting the progress step.** `while i < len(lines):` with no `i += 1` in the body. `i` stays 0 forever.
2. **A condition that can skip past its target.** `n = 5`, then `while n != 0: n -= 2` goes 5, 3, 1, -1, -3, ... and never equals 0. Use `n > 0` instead: an inequality can't be skipped over.
3. **Waiting for something that never happens.** `while not has_fix:` when the receiver is indoors and will never get a fix. Always add a **limit**: a maximum number of tries, or a timeout.

If your code hangs on this site, the runner stops it after a few seconds and shows a `TimeoutError`. In VS Code or a terminal, press **Ctrl+C** to interrupt it.

The professional fix for cause 3 is the same thing a PLC does: a **watchdog**. Count the passes, and if the count exceeds a limit, give up and report it, instead of hanging.

### `break`: leave the loop now

`break` exits the innermost loop **immediately**. The rest of the body is skipped, and so is the condition check. Execution continues on the first line after the loop.

```python
while tries < max_tries:
    ...
    if line_is_good:
        break        # found it: stop reading
```

Use `break` when the loop has a "found it, I'm done" exit in the middle. Inside a function, `return` does the same job, and also hands back the answer.

### After the loop: success or timeout?

A loop with a limit can end two ways: it **found** what it wanted, or it **ran out** of tries. The code after the loop must tell them apart. The usual pattern: start with a "nothing found yet" value (`found = ""`), set it when you succeed, and check it after the loop.

## Worked examples

Predict each output, then run it. Then **break** each example on purpose: delete the progress line in Example 2's fixed version and watch the site stop it with a `TimeoutError`.

**Example 1: countdowns, counters, and a loop that runs zero times.** Notice the value of `countdown` after the loop: it's the first value that **failed** the condition.

{{example:ex1}}

**Example 2: an infinite loop, caught and fixed.** This is the "wait until the wheel speed settles below 1.0" loop. The buggy version forgot `i += 1`, so it checks `readings[0]` forever. A pass counter acts as a watchdog, so it gives up after 10 extra passes and tells you `i` never changed. That's a real debugging technique: when a loop hangs, print the loop variable and see if it moves.

{{example:ex2}}

**Example 3: robotics-realistic: retry until a valid fix arrives.** This is the core of a GPS driver's startup. Lines come in one at a time; garbage and non-GGA sentences are skipped; the loop stops on the first real fix (`break`) or after `max_tries` reads. Note the **two** limits in the condition: the try limit, and the end of the data.

{{example:ex3}}

**Example 4: how many scans until the wheel stops?** When you know the stopping condition but not the number of passes, a `while` loop counts them for you. This is the same as measuring settling time on a scope: how long until the signal drops below a threshold. The second half adds a safety limit and reports a timeout, which is what real control code must do. (`round(x, 1)` rounds to 1 decimal place for printing.)

{{example:ex4}}

## Predict, then check

Commit to an answer before you run anything.

{{predict:p1}}

{{predict:p2}}

{{predict:p3}}

## See it: a watchdog scan by scan

A safety watchdog on a motor controller cuts power if the main controller stops sending heartbeats. The timer counts down on every scan without a heartbeat and reloads on every heartbeat. Press **Trace it** and step through the scans.

{{viz:v1}}

## Common beginner mistakes

1. **No progress step.** The variable in the condition never changes, so the loop never ends. Point at the line that makes the condition eventually False. If there isn't one, it's an infinite loop.
2. **Off-by-one in the condition.** `i <= len(lines)` reads `lines[len(lines)]`, which doesn't exist: `IndexError`. `i < max_tries` with `i` starting at 0 runs exactly `max_tries` times; `<=` runs one extra time.
3. **Counting from 1.** Lists and strings start at index 0. A loop that starts `i = 1` silently skips the first item.
4. **Using `!=` for the stop condition.** If the variable can jump past the target, it runs forever. Prefer `<`, `>`, `<=`, `>=`.
5. **No limit on a "wait until" loop.** A receiver indoors may never get a fix. Every wait needs a maximum number of tries or a timeout.
6. **Forgetting to reset a counter.** When you need N readings **in a row**, a bad reading must set the count back to 0. Otherwise you're counting all low readings, not consecutive ones.
7. **Not telling success from timeout.** After a loop with a limit, check which way it ended before using the result.

## Challenge: wait for the fix

Write two functions, each with a `while` loop. Fill in the body; functions are covered properly in 0.6.

- `first_fix(lines, max_tries)` reads `lines` in order, starting at index 0, **at most** `max_tries` reads and never past the end of the list. It returns the first line (stripped) that is a GGA sentence (starts with `$`, characters `[3:6]` are `GGA`) with a real fix: at least 7 fields, and the quality field (index 6) is not empty and not `"0"`. If no such line arrives in time, it returns `""`.
- `settled_index(readings, threshold, needed)` returns the index of the reading at which the sensor has been **strictly below** `threshold` for `needed` readings **in a row** (`needed` is 1 or more). A reading at or above the threshold resets the run. If it never settles, return `-1`.

Inside a function, `return` exits the loop and the function at once, so you can use it instead of `break`. The hidden tests include blank lines, a truncated sentence from power-up, a fix on exactly the last allowed read, an empty list, `max_tries = 0`, a run that gets interrupted, and a reading exactly at the threshold.

{{challenge}}

## Find the bug

{{bug}}

## Explain it back

{{explain}}
