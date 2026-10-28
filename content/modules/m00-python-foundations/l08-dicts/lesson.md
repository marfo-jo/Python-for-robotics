## Why dictionaries?

Quick: in `['152305.00', 1, 9, 12.3]`, which number is the satellite count? You have to remember that it's slot 2. In `('152305.00', 42.33539, -71.0928)`, is slot 1 latitude or longitude? You saw in lesson 0.7 how easily that goes wrong.

A **dictionary** (a `dict`) solves this by labeling every value with a **name**:

```python
fix = {"time": "152305.00", "quality": 1, "satellites": 9, "altitude": 12.3}
fix["satellites"]      # 9: no position to remember
```

This is how real robot software passes data around. A ROS 2 `NavSatFix` message has named fields (`latitude`, `longitude`, `altitude`), a JSON config file is a dict, and a parameter server is a dict. In this lesson you'll turn a parsed sentence into a dict, handle missing fields safely, count sentence types in a log, and route each sentence to the right parser.

### The EE view: a dict is a tag database

If you've worked with PLCs, you already know this idea. A PLC program doesn't say "read memory word 40017"; it says "read `Tank1_Level`." The **tag database** maps each tag name to its value.

| Dict idea | PLC / hardware idea |
|---|---|
| `fix = {}` | An empty tag database |
| `fix["altitude"] = 12.3` | Create the tag `altitude` (or write to it if it exists) |
| `fix["altitude"]` | Read the tag by name |
| `fix["altitde"]` → `KeyError` | "Tag not found": a typo is not a tag |
| `fix.get("hdop", 0.0)` | Read the tag, or use a safe default if it isn't configured |
| `{"GGA": parse_gga, ...}` | A jump table: the opcode selects which routine runs |

## Dictionaries: the ideas you need

### 1. Keys and values

A dict holds **key: value** pairs inside curly braces. You look things up by key, not by position:

```python
fix = {"time": "152305.00", "quality": 1, "satellites": 9}
fix["satellites"]          # 9
fix["hdop"] = 1.1          # a new key: ADDS a pair
fix["satellites"] = 10     # an existing key: OVERWRITES the value
len(fix)                   # 4 pairs
```

Rules worth knowing:

- **Keys are unique.** Assigning to an existing key replaces the old value. A dict can never hold the same key twice.
- **Keys are usually strings** (field names, sentence types). They must be unchangeable things like strings, numbers, or tuples, never lists.
- **Values can be anything**: numbers, strings, lists, tuples, other dicts, even functions.
- **Order is kept.** A dict remembers the order keys were first added, and loops over them in that order.

### 2. Missing keys: `KeyError`, `in`, and `.get`

Square brackets on a key that doesn't exist raise **`KeyError`**:

```python
fix["altitude"]            # KeyError: there is no 'altitude' key
```

On a robot, missing data is normal. A receiver without a fix sends empty fields, so your dict won't have those keys. You have two safe tools:

```python
"altitude" in fix                  # False: `in` checks the KEYS
fix.get("altitude")                # None: no crash
fix.get("altitude", 0.0)           # 0.0: your default
```

`.get(key, default)` means "the value if the key is there, otherwise the default." If you leave out the default, you get `None`. Use square brackets when a missing key really is a bug (you *want* the loud crash), and `.get` when a missing key is expected.

Note that `in` checks **keys only**. `9 in fix` is `False` even if some value is 9.

### 3. Keys must match exactly

`"GGA"`, `"gga"`, and `"GGA "` (with a trailing space) are three different strings, so they are three different keys. A typo like `"satelites"` doesn't raise an error when you *store* it: Python just creates a new key with the misspelled name. The crash (or the silent default from `.get`) shows up later, somewhere else, when you look up the correct spelling. When a lookup mysteriously fails, **print the dict and the key you're using**, and compare them character by character.

### 4. Building a dict from a sentence

Start with an empty dict and add a key for each field you have:

```python
fields = line.strip().split(",")
fix = {}
if fields[7] != "":
    fix["satellites"] = int(fields[7])
```

Leaving a key **out** when its field is empty is honest: it says "the receiver didn't tell us," rather than inventing a 0 that looks like real data. (An altitude of 0.0 m is a real place, sea level! A missing altitude is not.) The caller can then choose a default with `.get`.

### 5. Looping over a dict

```python
for key in fix:                    # loops over the KEYS
    print(key)

for key, value in fix.items():     # (key, value) tuples: unpack them (lesson 0.7)
    print(key, "=", value)

fix.keys()      # all the keys
fix.values()    # all the values, e.g. sum(counts.values())
```

### 6. Counting with a dict

Counting things by category is one of the most common jobs in log analysis: how many GGA sentences, how many RMC, how many bad checksums. The pattern is one line:

```python
counts[kind] = counts.get(kind, 0) + 1
```

The first time a `kind` appears, `.get` returns the default `0`, so the count becomes 1. After that, it finds the stored count and adds one. Compare this with the two classic mistakes:

- `counts[kind] = 1` overwrites every time, so every count stays 1.
- `counts[kind] += 1` raises `KeyError` the first time, because there's no old value to add to.

### 7. A dict of functions: dispatch

In Python, a function is a value, just like a number. Writing its name **without** parentheses refers to the function itself; adding `()` calls it. So you can store functions in a dict:

```python
HANDLERS = {"GGA": handle_gga, "RMC": handle_rmc}

handler = HANDLERS.get(kind)       # look up which function to use
if handler is not None:
    result = handler(fields)       # now call it
```

This is a **dispatch table**, like a jump table in firmware or a PLC that picks a routine by opcode. To support a new sentence type, you write one handler and add one entry, instead of growing a long `if`/`elif` chain. And `.get` makes unknown types fall through safely as `None`.

## Worked examples

Read each example, **predict what it prints**, then run it.

**Example 1: dict basics.** Read, add, overwrite, check keys, and handle a missing key with `.get`.

{{example:ex1}}

**Example 2: a dict of named fields from a sentence.** One dict maps names to field indexes; the function builds a second dict of name to text, skipping empty fields.

{{example:ex2}}

**Example 3: robotics-realistic: count sentence types in a log.** A real log mixes GGA, RMC, GSA, GSV, and VTG sentences, plus the odd blank line.

{{example:ex3}}

**Example 4: dispatch with a dict of functions.** Each sentence type goes to its own handler; unknown types are ignored.

{{example:ex4}}

## Predict, then check

{{predict:p1}}

{{predict:p2}}

{{predict:p3}}

## See it: dicts at work

Press **Trace it** and step through the counting loop. Watch the `counts` dict in the variables table: when does it gain a new key, and when does a value change?

{{viz:v1}}

And here is dispatch. Watch `handler` become a function, and watch the trace jump into it only when it's called.

{{viz:v2}}

## Common beginner mistakes

1. **Square brackets on a key that might be missing.** `fix["hdop"]` raises `KeyError`. Use `fix.get("hdop", default)` or check `"hdop" in fix` first.
2. **Case and typos in keys.** `"gga"` is not `"GGA"`, and `"satelites"` is not `"satellites"`. Python won't warn you when you store the wrong one.
3. **Counting by assignment.** `counts[k] = 1` overwrites. Use `counts[k] = counts.get(k, 0) + 1`.
4. **`+= 1` on a new key.** `counts[k] += 1` raises `KeyError` the first time `k` appears.
5. **Expecting `in` to search values.** `in` checks keys only.
6. **Inventing values for missing data.** Storing `0` for an empty altitude makes "no data" look like "sea level." Leave the key out and let the caller decide.
7. **Calling the function when you meant to store it.** `{"GGA": handle_gga(fields)}` stores the *result*. For dispatch, store `handle_gga` with no parentheses.

## Challenge: named fields and a sentence census

Write two functions. The docstrings in the starter are the full spec.

- `gga_to_dict(sentence)`: return a dict with keys `"time"` (str), `"quality"` (int), `"satellites"` (int), `"hdop"` (float), and `"altitude"` (float), from fields 1, 6, 7, 8, and 9. **Leave a key out** if its field is empty. Return `None` if the sentence isn't GGA (any talker) or has fewer than 15 fields.
- `count_types(sentences)`: return a dict mapping each sentence type to how many times it appears. The type is characters 3 to 6 of the stripped line, so `$GPGGA` and `$GNGGA` both count as `"GGA"`. Skip blank lines and lines that don't start with `$` (the partial line you get when you connect mid-sentence).

{{challenge}}

## Find the bug

{{bug}}

## Explain it back

{{explain}}
