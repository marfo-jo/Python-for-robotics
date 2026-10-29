## Why this lesson matters

Up to now, every sentence came from a string you typed into the code. Real data doesn't arrive that way. In the EECE5554 GPS lab and in Lab 4 you **recorded** data (to a ROS bag, or to a text log) and analyzed it afterwards. A one-minute GPS log at 1 Hz is 60 lines; a one-hour drive with GGA and RMC at 10 Hz is 72,000. You need to read files.

And real log files are messy in exactly the ways that break naive code:

- **Blank lines**, from a logger that writes an extra newline or from someone editing the file.
- **Junk that isn't NMEA**, such as the receiver's boot banner (`u-blox NEO-M8N ROM 2.01`), comments, or binary noise from a loose connector.
- **Corrupted sentences** whose checksum doesn't match (electrical noise on the UART line).
- **A truncated last line.** The robot's battery died (or someone pulled the USB cable) halfway through writing a sentence, so the file ends with `$GPGGA,153015.00,4220.01` and no newline.

A good log reader does what a good technician does with a chart recorder roll: it reads everything, keeps the good data, skips the empty stretches, and **counts** the faults so you know how much to trust the run. That's this lesson.

## Opening a file: `with open(...)`

```python
with open("gps_log.txt", encoding="utf-8") as f:
    for line in f:
        print(line.strip())
```

Piece by piece:

- `open("gps_log.txt", ...)` asks the operating system for the file and gives you back a **file object**. The first argument is the **path** (more on paths below).
- `encoding="utf-8"` says how the bytes on disk turn into characters. Always pass it (see below).
- `as f` names the file object `f`.
- The indented block is where the file is open. **When the block ends, Python closes the file automatically**, even if an error happens inside the block.

That last point is why you always use `with`. A file that is never closed is like a breaker you forgot to reset, or a lockout tag nobody removed: on Windows, an open file can't be deleted or renamed by other programs, and data you *wrote* may still be sitting in a buffer instead of on disk. `with` is your guaranteed "release on exit", the same way a safety relay drops out no matter how the machine stopped.

### The mode: read, write, or append

The optional second argument is the **mode**:

| Mode | Meaning | If the file exists | If it doesn't |
|---|---|---|---|
| `"r"` (default) | read | read from the start | `FileNotFoundError` |
| `"w"` | write | **erased first!** | created |
| `"a"` | append | add to the end | created |

`"w"` destroys the old contents the moment you open the file, before you write anything. Never open your only copy of a field log with `"w"`.

### Always pass `encoding="utf-8"`

A text file is really a sequence of **bytes**. The encoding is the table that maps bytes to characters, like the character ROM in an old LCD module. NMEA itself is plain ASCII, so any encoding reads it the same way, but logs often pick up other characters (a `°` in a comment, a `µ` in a units label). If you leave the encoding out, Python uses your computer's default: in the browser that's UTF-8, but on Windows it's often `cp1252`, so the same script can read a file correctly in one place and produce garbage (or a `UnicodeDecodeError`) in another. Passing `encoding="utf-8"` makes your code behave the same everywhere.

## Reading: a file object is a one-way tape

The simplest and best way to read a text file is to **loop over the file object**. Each pass of the loop gives you **one line, including its `\n`**:

```python
for line in f:
    ...           # line is '$GPGGA,...*62\n'
```

The `\n` is part of the line, exactly like the `\r\n` from the serial port in lesson 0.1. So the first thing you do with every line is `line = line.strip()`. The **last** line of a file may have no `\n` at all (that's exactly what a truncated line looks like), which is another reason to strip instead of slicing off one character.

There are two other ways to read:

| Call | Gives you | Use it when |
|---|---|---|
| `for line in f:` | one line at a time | almost always: works on a 2 GB log without loading it all |
| `f.readlines()` | a list of all lines (each ends with `\n`) | you need to index lines or go through them twice |
| `f.read()` | the whole file as one string | the file is small and you want all the text at once |

A file object keeps a **position**, like the read head on a tape or the read pointer of a FIFO buffer. Every read moves it forward. Once you've read to the end, the head is parked at the end: a second `for line in f:` loop or a second `f.readlines()` gets **nothing**, with no error. If you need the lines twice, either do everything in one loop or save them in a list first.

### The standard log-reading loop

Almost every log reader you'll write has this shape:

```python
good = []
errors = 0
with open(path, encoding="utf-8") as f:
    for line in f:
        line = line.strip()          # 1. clean
        if line == "":               # 2. skip blanks (not an error)
            continue
        if checksum_ok(line):        # 3. validate
            good.append(line)        # 4. keep the good data
        else:
            errors += 1              # 5. count the faults
```

`continue` jumps straight to the next pass of the loop, skipping the rest of the body. It's the clean way to say "this line isn't interesting, move on".

Notice which test catches what. A blank line becomes `''` after stripping. Junk like a boot banner has no `$` and no `*`. A truncated last line starts with `$` but has no `*`. A corrupted sentence has everything, but the checksum doesn't match. A single `checksum_ok()` check (lesson 0.4) rejects all three non-blank kinds. The `$`-and-`*` shape check alone is **not** enough, because corrupted sentences pass it.

Here is the checksum rule again, as a reference (you don't need to memorize it; it's shown next to the challenge too):

{{ref:checksum}}

## Paths and the working directory

A **path** tells `open()` where the file is.

- An **absolute path** starts from the top of the drive: `C:/Users/you/robot_logs/run1.txt`.
- A **relative path** like `"run1.txt"` or `"logs/run1.txt"` is looked up starting from the **current working directory** (CWD): the folder your program was *started from*, which is **not necessarily the folder the script is in**.

This catches everyone. Suppose your script is `my-solutions/m00/read_log.py` and it opens `"run1.txt"`, and `run1.txt` sits next to the script. If you run it from the repo root:

```powershell
PS C:\...\Python-for-robotics> python my-solutions\m00\read_log.py
```

the working directory is the repo root, so Python looks for `C:\...\Python-for-robotics\run1.txt` and raises `FileNotFoundError`, even though the file is "right there". Two fixes: run the script from its own folder (`cd my-solutions\m00` first), or pass the path in as an argument instead of hard-coding it. To see where you are, `import os` and `print(os.getcwd())`.

Useful tools from the `os` module (part of the standard library):

| Call | What it does |
|---|---|
| `os.getcwd()` | the current working directory |
| `os.path.join("logs", "run1.txt")` | builds a path with the right separator for your system (`\` on Windows, `/` elsewhere) |
| `os.path.exists(path)` | `True` if something is at that path |
| `os.path.abspath(path)` | turns a relative path into an absolute one (glues the CWD on the front) |
| `os.makedirs("logs", exist_ok=True)` | creates a folder (and doesn't complain if it already exists) |

**Windows backslashes:** `"C:\new_logs\run1.txt"` is a trap, because `\n` inside a string is a newline character. Write `"C:/new_logs/run1.txt"` (Windows accepts forward slashes) or a raw string `r"C:\new_logs\run1.txt"`.

**Best practice:** write functions that take the path as a **parameter**, like `load_sentences(path)`. Then the caller decides where the file is, and the function works for any log in any folder. That's exactly how the hidden tests call your code.

## Writing, briefly

You've seen it at the top of every example: open with `"w"` (or `"a"`) and call `f.write(text)`. `write` does **not** add a newline for you, so put `\n` at the end of each line yourself. You'll write log files properly when you build data loggers later in the course.

## Worked examples

All of these examples first create a small log file, then read it back, so they run the same in the browser and on your laptop.

**Example 1: looping over a file.** Each line keeps its `\n` (except the last one here), and the file is closed after the `with` block.

{{example:ex1}}

**Example 2: read(), readlines(), and the standard strip-and-skip loop.** Watch what blank and whitespace-only lines look like before and after `strip()`.

{{example:ex2}}

**Example 3: robotics-realistic: a field log with a banner, a corrupted sentence, and a power-loss truncation.** This version only checks the *shape* of each line (`$` at the start, two characters after `*`). It rejects the banner and the truncated line, and the line counter tells you exactly where they are. But look at the last line of output: the corrupted sentence got through, because it looks perfect. Only the checksum (your `checksum_ok` from lesson 0.4) can catch it, and that's what the challenge requires.

{{example:ex3}}

**Example 4: relative paths, sub-folders, and checking that a file exists.**

{{example:ex4}}

## Predict, then check

{{predict:p1}}

{{predict:p2}}

{{predict:p3}}

## See it: step through a log loop

The tracer can't show a real file on disk, so this uses `io.StringIO`: a string that behaves exactly like an open text file (you can loop over it, and each line keeps its `\n`). Write down your prediction first.

{{viz:v1}}

## Common beginner mistakes

1. **Forgetting `strip()`.** Every line from a file ends in `\n` (except maybe the last one). Without stripping, blank lines aren't `''`, checksums don't match, and fields end with a newline.
2. **Writing `line.strip()` without `line = `.** Strings are immutable; the stripped copy is thrown away.
3. **Counting blank lines as errors.** A blank line is just empty space, not a fault. Skip it silently and count only real problems.
4. **Reading the file twice.** The second loop over the same file object gets nothing, with no error. Do it in one pass, or save the lines in a list.
5. **Trusting the shape of a line.** `$...*hh` can still be corrupted. Verify the checksum.
6. **Hard-coding a file name inside the function.** Take the path as a parameter.
7. **Relative paths from the wrong folder.** `FileNotFoundError` for a file you can see usually means your working directory isn't what you think. Print `os.getcwd()`.
8. **Opening with `"w"` when you meant to read.** `"w"` erases the file immediately.
9. **Leaving out `encoding="utf-8"`.** It works on your machine until it doesn't.

## Challenge: a robust log loader

Write `load_sentences(path)`. It opens the file at `path` (use `with` and `encoding="utf-8"`), and returns a tuple `(sentences, errors)`:

- `sentences` is a list of every **valid** NMEA sentence in the file, **stripped**, in file order. Valid means: starts with `$`, contains `*`, and the two hex digits after the `*` match the XOR checksum of everything between `$` and `*` (upper- or lowercase hex both count).
- `errors` is the number of **non-blank** lines that were rejected: junk, bad checksums, and truncated lines.
- Blank and whitespace-only lines are skipped and are **not** errors.

The starter includes an optional `checksum_ok(sentence)` helper. You wrote one in lesson 0.4; try writing it again without looking. The hidden tests build real files in a temporary folder (with pytest's `tmp_path`) and pass you the path: a banner line, blank lines, Windows `\r\n` line endings, a sentence cut off right after its `*`, a corrupted checksum, a non-ASCII comment, an empty file, and a power-loss truncated last line.

{{challenge}}

## Find the bug

{{bug}}

## Explain it back

{{explain}}
