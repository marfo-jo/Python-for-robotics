## Why functions?

Look back at the last few lessons. You've written `sentence.strip().split(",")` and `fields[0][3:6] == "GGA"` over and over. Copy-pasted code is like hand-wiring the same circuit on five different boards: when you find a mistake, you have to find and fix all five copies, and you'll miss one.

A **function** lets you build that logic **once**, give it a name, test it, and reuse it everywhere. Every real sensor driver is built this way. The ROS 2 GPS driver from your EECE5554 lab has a function that takes one NMEA line and returns the parsed values; the node just calls it once per line. In this lesson you'll write that function properly: `parse_gga(sentence)`.

### The EE view: a function is a reusable subcircuit

You've been treating functions as "circuit blocks" since lesson 0.1. Here's the full analogy:

| Function idea | Circuit idea |
|---|---|
| `def parse_gga(sentence):` | Design a subcircuit (an IC) once |
| Parameter `sentence` | An **input pin** on the block |
| Argument `"$GPGGA,..."` | The actual **signal** you connect to that pin |
| `return value` | The **output pin**: the only thing that leaves the block |
| Local variables inside | **Internal nodes**: you can't probe them from outside the package |
| Docstring | The **datasheet**: what goes in, what comes out |
| Calling `parse_gga(line)` | Dropping another instance of the IC onto the board |

Keep this table in mind. Almost every beginner function bug is a violation of one row of it.

## Functions: the ideas you need

### 1. Anatomy of a function

```python
def enough_satellites(count, minimum):
    """True if a fix used at least `minimum` satellites."""
    ok = count >= minimum
    return ok
```

- `def` starts the definition, then the **name**, then the **parameters** in parentheses, then a colon.
- The **body** is indented, exactly like the body of an `if` or a `for`.
- The first line of the body can be a **docstring**: a string in triple quotes that says what the function does. Python stores it, so tools (and you, six months from now) can read it.
- `return` sends a value back out and **ends the function immediately**.

Defining a function does **not** run it. It only builds the block. The body runs each time you **call** it: `enough_satellites(9, 4)`.

### 2. Parameters versus arguments

These two words get mixed up constantly, so be precise:

- A **parameter** is the name in the `def` line: `count`, `minimum`. It's the pin.
- An **argument** is the value you pass in when you call: `9`, `4`. It's the signal on the pin.

When you call `enough_satellites(9, 4)`, Python connects the arguments to the parameters **in order**: `count = 9`, `minimum = 4`. Then the body runs.

You can also connect them **by name**, which is clearer when there are several: `enough_satellites(count=9, minimum=4)`. These are called **keyword arguments**.

### 3. `return` versus `print`: the classic beginner bug

This is the most important idea in the lesson.

- `print(x)` puts `x` on the **screen**, for a human to read. The program can't use it afterward.
- `return x` hands `x` **back to the code that called the function**, so it can be stored, compared, or passed to another function.

If a function reaches its end without a `return`, it hands back a special value called **`None`**, Python's "nothing here" object. So this happens:

```python
def sats(sentence):
    print(int(sentence.split(",")[7]))   # shows 9 on the screen...

n = sats(line)       # ...but n is None
n >= 4               # TypeError: '>=' not supported between 'NoneType' and 'int'
```

(Index 7 is the satellite count of a GGA sentence. Field positions are reference material, not something to memorize: this lesson's GGA examples and the challenge use this table, and the challenge shows it again.)

{{ref:gga}}

The screen shows the right number, so the function *looks* like it works. Then a completely different line crashes. In hardware terms, you wired the result to a debug LED instead of to the output pin: you can see it, but nothing downstream receives it.

To check for `None`, use `is None` (or `is not None`): `if result is None:`. You'll use this a lot, because returning `None` is the standard way for a parser to say "this input was not usable."

### 4. `return` ends the function

As soon as a `return` runs, the function stops. That makes **early returns** a clean way to reject bad input:

```python
def rmc_status(sentence):
    if sentence.strip()[3:6] != "RMC":
        return None            # not our sentence: stop here
    fields = sentence.strip().split(",")
    return fields[2]           # RMC status letter (see the RMC table in Example 4)
```

Read it top to bottom like a checklist: "if this is wrong, give up; if that is wrong, give up; otherwise, here's the answer." This is exactly how you'll write `parse_gga`.

### 5. Local scope: what happens inside stays inside

Names created inside a function (its parameters and any variable you assign in the body) are **local**. They are created fresh when the call starts and thrown away when it ends:

```python
def sentence_type(sentence):
    clean = sentence.strip()
    return clean[3:6]

kind = sentence_type(line)
print(clean)          # NameError: clean only existed during the call
```

And assigning to a name inside a function makes a **new local**, even if a global with the same spelling exists. The global is untouched. This is a feature, not a limitation: it means a function can't accidentally clobber some other part of your program, the same way an IC's internal nodes can't short to the rest of your board. **The only way out of a function is `return`.**

### 6. Default arguments

A parameter can have a **default value**, used when the caller doesn't pass that argument:

```python
def enough_satellites(count, minimum=4):    # 4 satellites is the minimum for a 3D fix
    return count >= minimum

enough_satellites(9)        # uses minimum=4
enough_satellites(9, 10)    # overrides it: minimum=10
```

Defaults are great for "usually this, sometimes something else" settings, like a threshold. Parameters with defaults must come **after** the ones without. (There is one famous trap with defaults that are lists; you'll meet it in a later lesson. For now, use numbers and strings as defaults.)

### 7. Small functions that compose

The real power comes from **chaining** small functions, each doing one job:

```
raw line ──► is_gga() ──► parse_gga() ──► [time, quality, sats, altitude]
             (validate)    (extract and convert)
```

Why not one big function? For the same reason you bench-test a subcircuit before soldering it into the system: a small function with one job is easy to test on its own. When `parse_gga` misbehaves, you can check `is_gga` separately and know immediately which block is at fault.

## Worked examples

Read each example, **predict what it prints**, then run it. Change things and re-run.

**Example 1: define, call, and document a function.** Notice which word is the parameter and which value is the argument.

{{example:ex1}}

**Example 2: `print` versus `return`.** Both functions "work" in the sense that you see a 9. Only one of them is useful.

{{example:ex2}}

**Example 3: default arguments, keyword arguments, and local scope.** Watch the two different names called `minimum`.

{{example:ex3}}

**Example 4: robotics-realistic: small functions that compose.** An RMC sentence carries a status letter at index 2: `A` (active, the fix is valid) or `V` (void, ignore it). You don't need to memorize that; it's in the RMC reference table:

{{ref:rmc}}

Three tiny functions, each built on the one before, decide whether a line is usable, and they survive a cut-off line.

{{example:ex4}}

## Predict, then check

{{predict:p1}}

{{predict:p2}}

{{predict:p3}}

## See it: inside a function call

Press **Trace it** and step through. When the trace enters `sentence_type`, the variables table switches to that call's local names. Watch what's left when it returns.

{{viz:v1}}

And here is `print` versus `return` side by side. Look at the **returned** value at the end of each call.

{{viz:v2}}

## Common beginner mistakes

1. **Printing instead of returning.** The value shows on the screen, but the caller gets `None`. If you see `NoneType` in an error message, check this first.
2. **Forgetting to store the result.** `parse_gga(line)` on its own line computes the answer and throws it away. Write `fix = parse_gga(line)`.
3. **Expecting a local to exist outside.** Variables made inside a function vanish when it returns. Return what you need.
4. **Hard-coding a value that should be a parameter.** If the function has a `min_sats` parameter, compare with `min_sats`, not with `4`. Otherwise passing a different value silently does nothing.
5. **Converting before checking.** A no-fix sentence has empty fields, and `float("")` raises `ValueError`. Reject bad input (early `return None`) *before* converting.
6. **Defining but never calling.** A `def` only builds the block. Nothing runs until you call it.
7. **Code after `return`.** It never runs. `return` ends the function.

## Challenge: write `parse_gga` properly

Write two functions that compose. The docstrings in the starter are the full spec.

- `is_gga(sentence)` returns `True` or `False`. After stripping, a GGA sentence starts with `$`, its type (characters 3 to 6) is `GGA` for **any** talker, and it splits into **at least 15** fields (a cut-off line has fewer).
- `parse_gga(sentence, min_sats=4)` uses `is_gga`, then **returns** a list `[utc_time, fix_quality, satellites, altitude_m]`: a `str`, an `int`, an `int`, and a `float` (fields 1, 6, 7, and 9). It returns `None` if the sentence isn't GGA, if the fix quality is `0`, or if there are fewer than `min_sats` satellites.

(A list of four different kinds of value works, but it's not the best container for a fixed record like this. In lesson 0.7 you'll meet a better one.)

{{challenge}}

## Find the bug

{{bug}}

## Explain it back

{{explain}}
