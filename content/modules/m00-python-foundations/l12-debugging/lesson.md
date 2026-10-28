## Why this lesson matters

You will spend more of your engineering career **debugging** than writing new code. That's true in robotics more than anywhere: the code talks to sensors, motors, and networks, and any of them can be the problem. The good news is that you already have the most important skill. You've troubleshot PLC systems and electromechanical equipment. Software debugging is the same discipline with different test equipment.

The bad debugging habit is the one every beginner falls into: stare at the code, change something that looks suspicious, run it, change something else, run it again. That's swapping parts until the machine starts. Sometimes it works, but you never learn what was wrong, and you often add a second fault while "fixing" the first.

This lesson gives you a **method**, and three tools to carry it out: print probes (`repr()` and `f"{x=}"`), bisecting a pipeline, and a real debugger (the tracer in the browser, and VS Code on your laptop).

## The method: troubleshoot it like a machine

Here is the procedure, next to how you'd troubleshoot a conveyor that keeps stopping.

| Step | On the plant floor | In code |
|---|---|---|
| **1. Reproduce** | Make the fault happen on demand. Note exactly when and how. | Find an input that shows the bug **every time**. Make it as small as you can: one sentence, not a 72,000-line log. |
| **2. Isolate** | Half-split the circuit: measure in the middle, then in the middle of the bad half. | Probe the output of each stage of the pipeline. The bug lives between the last stage that's right and the first that's wrong. |
| **3. Hypothesize** | "The prox sensor is dropping out when the belt vibrates." | One specific, testable cause: "`fields[6]` is a string, so `== 0` is never True." |
| **4. Test** | Put a meter on it. Watch the I/O status bit. | Run one small experiment that would prove the hypothesis **wrong** if it's wrong: a print, a one-line script, a breakpoint. |
| **5. Fix** | Replace the sensor, re-route the cable. | Change the **cause**, not the symptom. One change at a time. |
| **6. Verify** | Run the line and watch it. Check you didn't break anything else. | Re-run the original reproduction **and** all your tests. |

Two rules hold this together:

- **Expected vs actual.** At every probe, write down what you *expect* before you look. A measurement is only useful if you know what it should be. "The 24 V rail reads 24 V" tells you something; "the voltage is 11.8" tells you nothing until you know it should be 24.
- **Change one thing at a time.** If you change three things and it works, you don't know which one fixed it, or whether the other two broke something you haven't noticed yet.

## Tool 1: print probes that tell the truth

`print()` is your multimeter. But a plain `print()` can lie to you, because it hides exactly the differences that cause the most bugs:

```python
print("8", 8)          # 8 8          -- a string and an int look identical
print("66\r\n")        # 66           -- the \r\n is invisible
print("", " ")         #              -- empty and a space both look like nothing
```

### repr(): show what's really there

`repr(x)` gives the **developer's view** of a value: strings get quotes, and invisible characters are shown as escapes:

```python
print(repr("8"), repr(8))    # '8' 8
print(repr("66\r\n"))        # '66\r\n'
print(repr(""), repr(" "))   # '' ' '
```

When a comparison fails and you can't see why, print `repr()` of both sides. Nine times out of ten you'll see quotes on one side (a string vs a number) or a `\r\n` you forgot to strip. `type(x).__name__` is the other half of the check: it prints `str`, `int`, `float`, `list`, or `NoneType`.

### f"{x=}": labelled probes for free

Put an `=` after the expression in an f-string and Python prints the expression's text, an `=`, and the `repr()` of its value:

```python
sats = "09"
print(f"{sats=}")              # sats='09'
print(f"{len(fields)=}")       # len(fields)=15
print(f"{sats == 9=}")         # sats == 9=False
print(f"{alt * 3.28084=:.1f}") # alt * 3.28084=33.5   (format spec after the =)
```

This is the fastest probe you can write: it labels itself, it uses `repr()` automatically, and it works on any expression, including comparisons, which show you *why* an `if` went the way it did. Add a stage label when you have several: `print(f"stage 2: {sats=} {alt=}")`.

**Clean up afterwards.** Debug prints are temporary test leads. Remove them (or turn them into real tests) once the bug is fixed, or your output fills with noise and the next real problem hides in it.

## Tool 2: bisect the pipeline

Robotics code is almost always a **pipeline**: raw bytes → sentence → fields → numbers → units → frame transform → controller. When the final answer is wrong, the bug can be in any stage. Don't read every line hoping to spot it. **Half-split it**, exactly like a long run of wiring:

1. Probe the output of the stage in the **middle** of the pipeline. Compare with what you expect.
2. If it's right, the bug is in the second half. If it's wrong, it's in the first half (or right at that stage).
3. Repeat on the bad half.

Each probe cuts the search space in half. A 16-stage pipeline needs at most 4 probes. You need a known input with a known correct answer to do this, which is why step 1 (reproduce with a small input) comes first. Example 3 does this on a speed pipeline.

Good functions make bisecting easy: when each stage is its own small function with a clear input and output, you can call it alone with a test value. That's why the challenge pipeline is split into stage functions, and why the hidden tests probe each stage separately: **the test names tell you which stage is broken.** Read the failing test names as your measurements.

## Tool 3: a debugger

Print probes show values at the points you chose in advance. A **debugger** lets you pause the running program at any line and look at **everything**: every variable, the call stack, and the result of any expression you type. It's the difference between a multimeter and a logic analyzer with a trigger.

The core controls (same names in every debugger):

| Control | What it does | VS Code key |
|---|---|---|
| **Breakpoint** | "Pause here when you get to this line" | click left of the line number (red dot), or F9 |
| **Continue** | Run until the next breakpoint | F5 |
| **Step over** | Run this line (including any function it calls) and stop at the next line | F10 |
| **Step into** | If this line calls one of your functions, go inside it and stop at its first line | F11 |
| **Step out** | Finish the current function and stop back in the caller | Shift+F11 |
| **Watch** | Expressions that are re-evaluated at every pause, like `len(points)` or `total` | Watch panel, + |
| **Call stack** | Which function called which to get here (the same list as a traceback, but live) | Call Stack panel |
| **Stop** | End the debugging session | Shift+F5 |

**In the browser, the tracer is your debugger.** Stepping forward is "step", the highlighted line is where the program is paused, the variables table is the Variables panel (with `repr()`-style values, so `'1'` and `1` look different), and the stack shown for function calls is the call stack. Use it on any code you paste in.

### Local exercise: the VS Code debugger (Windows)

Do this on your laptop. It takes about 15 minutes, and you will use it for the rest of the course. **Create the file yourself, in your own `my-solutions/m00/` folder.**

**1. Open the course folder and pick the interpreter.**

- In VS Code: **File → Open Folder...** and open your `Python-for-robotics` folder.
- If you don't have it yet, install the **Python** extension by Microsoft (Extensions panel, `Ctrl+Shift+X`, search "Python"). It includes the Python Debugger.
- Press `Ctrl+Shift+P`, type **Python: Select Interpreter**, and choose the one that says **robotics-course** (it lives at `C:\Users\<you>\anaconda3\envs\robotics-course\python.exe`). The interpreter name shows in the bottom-right status bar.

**2. Create the script.** In the Explorer, make the folder `my-solutions/m00/` if it doesn't exist, and create `my-solutions/m00/debug_distance.py` with this code. It has a bug: it should print 2.02 m.

```python
def total_distance(steps):
    for step in steps:
        total = 0
        total = total + step
    return total


steps = [0.52, 0.49, 0.51, 0.50]   # meters per odometry tick
print(f"distance: {total_distance(steps):.2f} m")   # expect 2.02 m
```

**3. Reproduce it from the terminal first.** Open the terminal (`` Ctrl+` ``) and run:

```powershell
conda activate robotics-course
python my-solutions\m00\debug_distance.py
```

You should see `distance: 0.50 m`. (If `conda activate` fails in PowerShell, run `conda init powershell` once, close the terminal, and open a new one.)

**4. Set a breakpoint.** Click in the gutter just left of the line number of `total = total + step`. A red dot appears.

**5. Start debugging.** With `debug_distance.py` open, press **F5** and choose **Python Debugger → Python File** if asked. The program runs and pauses on your breakpoint; the line is highlighted in yellow.

**6. Look around.**

- **Variables** panel (left): you'll see `step` and `total` under *Locals*.
- **Watch** panel: click **+** and add `total`, then add `step`.
- **Call Stack** panel: you're in `total_distance`, called from `<module>`. Same as a traceback, but live.

**7. Step and watch.** Press **F10** (step over) a few times. Watch `total` in the Watch panel on every pass of the loop. Write down what you *expect* it to be on each pass (0.52, 1.01, 1.52, 2.02), and compare. You'll see `total` drop back to 0 at the start of every pass. That's your measurement: now form the hypothesis and fix it.

**8. Try the other controls.** Move the breakpoint to the `print(...)` line, restart (`Ctrl+Shift+F5`), and press **F11** (step into) to enter `total_distance` from the call. Press **Shift+F11** to step out. In the **Debug Console** tab, type `sum(steps)` and press Enter: you can evaluate any expression while paused. Right-click a breakpoint, choose **Edit Breakpoint**, and enter the condition `step == 0.51` to pause only on that pass (a *conditional* breakpoint: your trigger condition).

**9. Fix and verify.** Fix the bug, then run it again (from the terminal and with F5) and confirm `distance: 2.02 m`.

## Worked examples

**Example 1: print() vs repr().** Values that look identical when printed, but aren't.

{{example:ex1}}

**Example 2: f"{x=}" probes.** Self-labelling debug prints for a GGA sentence, including one that reveals a hidden `\r\n` and one that shows why a comparison is False.

{{example:ex2}}

**Example 3: robotics-realistic: bisecting a speed pipeline.** A robot with a top speed of 3 m/s reports 9.63 m/s. Probes on each stage, compared with expected values, find the bad stage; a test with a known value confirms the hypothesis; the same probes verify the fix.

{{example:ex3}}

## Predict, then check

{{predict:p1}}

{{predict:p2}}

{{predict:p3}}

## See it: the tracer as a debugger

This code reports "no fix" for a sentence that clearly has a GPS fix. Predict first, then step through it like a debugger: step *into* `has_fix`, then into `fix_quality`, and watch the call stack and the variables table.

{{viz:v1}}

## Common beginner mistakes

1. **Changing code before reproducing the bug.** If you can't make it fail on demand, you can't tell whether your change fixed it.
2. **Reproducing with a huge input.** Shrink it to the smallest input that still fails: one sentence, two samples.
3. **Probing without an expected value.** Write down what each value *should* be before you look.
4. **Plain `print()` for strings.** It hides quotes, spaces, and `\r\n`. Use `repr()` or `f"{x=}"`.
5. **Reading every line instead of bisecting.** Probe the middle stage first and halve the search.
6. **Changing several things at once.** One change, then re-test.
7. **Fixing the symptom.** Multiplying the answer by a fudge factor until it "looks right" leaves the real bug in place, and it will be wrong again on different data.
8. **Not verifying.** Re-run the original failing case *and* all the tests. A fix that breaks something else isn't a fix.
9. **Leaving debug prints in.** Remove them once the bug is fixed (or turn them into tests).

## Challenge: debug a GPS track pipeline

The editor opens with a complete pipeline for the Lab 4 report: it takes a GPS log and computes how far the robot drove, in meters.

1. **Stage 1** `gga_fixes(lines)`: keep stripped GGA sentences that have a fix (quality not `'0'`).
2. **Stage 2** `parse_latlon(sentence)`: signed decimal degrees.
3. **Stage 3** `to_local_xy(lat, lon, lat0, lon0)`: meters east and north of the first fix, using
$$x = \mathrm{radians}(\Delta \text{lon}) \cdot R \cdot \cos(\text{lat}_0), \qquad y = \mathrm{radians}(\Delta \text{lat}) \cdot R$$
where \( R \) = 6,371,000 m is the Earth's radius. (East-west distances shrink by \( \cos(\text{lat}_0) \) because meridians converge, as you saw in lesson 0.9. `math.cos` expects **radians**.)
4. **Stage 4** `path_length(points)`: the sum of the straight-line distances between consecutive points, using `math.sqrt` (square root) on \( \Delta x^2 + \Delta y^2 \).

**There are three planted bugs, in three different stages.** None of them crashes on the demo log. Your job is to find and fix all three with the method from this lesson, not to rewrite the pipeline. Submit early: the hidden test names say which stage each test probes (`stage 1: ...`, `stage 3: ...`), so the pattern of failing tests is your first measurement. Then reproduce each failure with a small input, probe with `f"{x=}"` or the tracer, and fix one bug at a time.

{{challenge}}

## Find the bug

{{bug}}

## Explain it back

{{explain}}
