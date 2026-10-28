# Content authoring guide

How to write lessons, track pages, and graded exercises for Python for Robotics.
Read it together with `PROMPT.md` (the spec) and `docs/PLAN.md` (approved plan).
**Lesson 0.1** (`content/modules/m00-python-foundations/l01-strings-nmea/`) is the
reference example. Match its depth and tone.

## Hard rules

- **Never create, edit, or read-and-complete anything in `my-solutions/`.** That
  folder is the learner's own work. Local exercises tell the learner to create
  their own files there.
- **No solution code for the learner's graded work**: hidden-test exercises, Sprint
  Project deliverables (firmware or Python), or the No Hands checkpoint. Reference
  solutions go ONLY in `verification/` (the private answer-key repo, gitignored in
  the public repo). Hints come in tiers: nudge → approach → pseudocode (never Python).
- Every lesson must pass `python tools/verify.py <lesson-id>` (conda env
  `robotics-course`, Python 3.11) **and** `python tools/browser_selftest.py <lesson-id>`
  (Pyodide 314.0.7, Python 3.14) before it counts as done.
- Use only standard library + numpy/matplotlib in browser lessons unless the lesson
  says otherwise. Avoid version-specific features: the code must behave the same
  on Python 3.11 (local) and 3.14 (browser).
- Never assert on Python's own exception *messages* (they differ between versions).
  Assert on exception *types*, or on your own messages.
- Refer to the learner as "you". If a third person is ever needed, use they/them.
- No MATLAB comparisons. Use electrical-engineering, embedded, PLC, and
  maintenance analogies (signals, frames, registers, scan cycles, diagnostics).

## Teaching style

- Explain **why**, not just how. Detailed explanations with many examples. Never
  trade understanding for brevity.
- **Name beginner mistakes explicitly** (a "Common beginner mistakes" section).
- Encouraging but demanding. Celebrate progress, never lower the bar.
- Recurring dataset in Module 0: GPS NMEA 0183 sentences ($GPGGA, $GNRMC, ...).
  Use real-looking sentences with **correct XOR checksums** (compute them; see the
  checksum snippet at the bottom).
- Robotics-realistic bugs for find-the-bug: unwrapped angle, wrong dt, frame mix-up,
  degrees vs radians, integer division, mutable default argument, off-by-one in a
  buffer, sign error in feedback, unit mix-ups, empty-field crashes, missing strip().

## Lesson folder

```
lNN-short-name/
  lesson.json      # structure (schema below)
  lesson.md        # prose with embeds on their own lines
  examples/ex1.py ex2.py ex3.py     # 3+ worked examples, simple → robotics-realistic
  challenge/starter.py              # what the editor opens with (must FAIL the tests)
  challenge/test_challenge.py       # hidden tests: real pytest, `from solution import ...`
  bug/buggy.py  bug/test_bug.py     # find-the-bug (buggy must FAIL; fixed must PASS)
```

Answer key (private repo, `verification/<lesson-id>/`):

```
challenge.py               # reference solution: must PASS
wrong_<mistake>.py         # 2+ (aim for 3 to 4) common beginner mistakes: each must FAIL
bug_fixed.py               # the fixed bug file: must PASS
```

### lesson.md embeds (each on its own line)

`{{example:ex1}}` `{{predict:p1}}` `{{viz:v1}}` `{{challenge}}` `{{bug}}` `{{explain}}`.
Every item in lesson.json must be embedded exactly once. No unknown embeds.

Math: use `$$...$$` (display) or `\( ... \)` (inline). **Never use single `$`**,
because NMEA sentences start with `$`.

### lesson.json schema

```json
{
  "id": "m00.l04",
  "title": "0.4 for loops and the NMEA checksum",
  "minutes": 75,
  "objectives": ["..."],
  "skills": {"python": 3},
  "whereYouSawThis": {"course": "EECE5554 Robot Sensing and Navigation", "topic": "..."},
  "examples": [{"id": "ex1", "title": "...", "file": "examples/ex1.py", "expectedOutput": "exact stdout"}],
  "predict": [{"id": "p1", "question": "...", "code": "...", "choices": ["...", "..."], "answer": 0, "why": "..."}],
  "visualizations": [{"id": "v1", "component": "tracer", "title": "...", "props": {"code": "..."},
                      "notice": "What to notice...", "predictFirst": {"question": "...", "reveal": "..."}}],
  "challenge": {"task": "one-line task summary for the tutor", "starter": "challenge/starter.py", "tests": "challenge/test_challenge.py", "timeLimitMs": 8000},
  "bug": {"file": "bug/buggy.py", "tests": "bug/test_bug.py", "bugType": "off-by-one", "report": "A realistic bug report..."},
  "explainBack": {"prompt": "...", "rubric": ["...", "...", "..."], "minWords": 40},
  "hints": {"challenge": ["nudge", "approach", "pseudocode"], "bug": ["nudge", "approach"]}
}
```

- `expectedOutput` is the exact stdout. Run the file and copy it; `verify.py` diffs it.
- **Predict choices**: the correct choice must equal the real stdout exactly (multi-line
  choices use `\n`). If the code raises, the choice is the exception type name, e.g.
  `"TypeError"`; if it prints and then raises, `"printed text\nTypeError"`. No other
  choice may equal the real output. Choices must be distinct. Give 3 to 4 plausible
  choices built from real misconceptions. `why` explains the misconception.
- Skills axes: python, math, controls, estimation, planning, perception, learning,
  ros2, softeng. Module 0 lessons: `{"python": 3}` (add `"softeng": 1` for
  debugging/testing-flavored lessons).
- `predictFirst` gates the visual behind a written prediction. Use it on at least one visual.
- Visual components available now: `tracer` (props: `code`, optional `expectError: true`
  when the traced code is meant to raise), `nmea-fields` (props: `sentence`),
  `xor-checksum` (props: `sentence`). Every Module 0 lesson should have a tracer.
  Don't add new components without the lead's approval (`app/viz/index.js` is shared).

### Hidden tests

- Real pytest. The learner's code is saved as `solution.py`: `from solution import f`.
- **Every test function has a one-line docstring.** The UI shows it as the test
  name, so write it for the learner: `"""ignores a trailing \\r\\n (edge case)"""`.
- Cover normal cases, edge cases (empty fields, whitespace, boundaries, zero), and bad
  input where the lesson teaches it. Aim for 6 to 12 tests.
- Tests must not depend on network or wall-clock time. Files: create them with
  pytest's `tmp_path` fixture.
- The starter must fail at least one test (usually by returning a placeholder).
- Functions before lesson 0.6: give the `def` line and `return` in the starter and
  say "fill in the body; functions are covered properly in 0.6" (as in lesson 0.1).
- Use only concepts taught up to and including the current lesson.
- Each test file must pass under both Python 3.11 and 3.14.

### Local-only exercises

When a step must run on the learner's machine (VS Code debugger, pyserial, Arduino):
give exact commands for Windows PowerShell + the conda env `robotics-course`, or the
Ubuntu 22.04 VM (ROS 2 Humble; note Jazzy differences). Tell the learner to create
files in **their own** `my-solutions/...` folder. Never create those files yourself.

## Track pages (sprints, C, interview)

- Markdown files under `content/tracks/<dir>/`, already registered in
  `content/curriculum.json` (don't edit that file without the lead's approval).
- Task lists `- [ ] item` become saved checkboxes.
- Tiered hints: `<details><summary>Hint 1 (nudge)</summary> ... </details>`.
- Images/diagrams: SVG files under `content/tracks/<dir>/img/`, referenced from
  markdown as `![alt text](content/tracks/<dir>/img/name.svg)` (paths are relative
  to the site root). Diagrams must be readable in light AND dark mode (use a white
  or transparent background with dark strokes inside a rounded white card, or
  `currentColor`), and they must label every pin.
- Optional quiz file (`*-quiz.json`):
  `{"title": "...", "items": [{"id","q","code"?,"choices","answer","why"}], "interview": [{"q","rubric":[...]}]}`.
- Sprint test files the learner runs locally live in `local/sprint1/...` and
  `local/sprint2/...`. They import the learner's module by name (for example
  `from imu_convert import raw_to_g`). The milestone page specifies the exact
  function signatures. Reference implementations go in
  `verification/tracks/<page-id>/<module>.py`, with 2+ `<module>_wrong_*.py`.
  `python tools/verify.py tracks` checks them.
- Arduino sketches you provide (diagnostic tools only, never the milestone
  deliverable) must compile:
  `"C:\Program Files\Arduino IDE\resources\app\lib\backend\resources\arduino-cli.exe" compile --fqbn arduino:avr:uno <sketch_dir>`

## Checksum snippet (for authoring only)

```python
from functools import reduce
def nmea_checksum(body):  # body = text between '$' and '*'
    return format(reduce(lambda a, c: a ^ ord(c), body, 0), "02X")
```
