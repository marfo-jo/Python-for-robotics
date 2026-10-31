# Build Progress

The source of truth for the plan is [PLAN.md](PLAN.md). Authoring rules are in
[CONTENT_GUIDE.md](CONTENT_GUIDE.md). Update this file at the end of every build session.

## Phase status

| Phase | Scope | Status | Date |
|---|---|---|---|
| 1 | Research, curriculum, roadmap, projects, shopping list, architecture | ✅ Approved and committed | 2026-10-28 |
| 2 | Site shell + Module 0 + Sprint milestone guides + first week of C and Interview tracks | ✅ Built, verified, deployed | 2026-10-28 |
| 3+ | One complete module per session, just ahead of the learner | ⏳ Next: see "Next session" | |

Live site: https://marfo-jo.github.io/Python-for-robotics/ (public repo `marfo-jo/Python-for-robotics`).
Answer key: private repo `marfo-jo/Python-for-robotics-answer-key`, cloned into gitignored `verification/`.

## Environment log

| Date | Change | Approved by learner |
|---|---|---|
| 2026-10-28 | `pyserial 3.5` installed in conda env `robotics-course` | Yes |
| 2026-10-28 | GitHub CLI 2.103.3 installed (winget); logged in as marfo-jo | Yes |

Baseline `robotics-course` env: Python 3.11.18, numpy 2.4.6, matplotlib 3.11.2, opencv-python 4.14.0, pytest 9.1.1, pyserial 3.5.
Browser runtime: Pyodide 314.0.7 (Python 3.14). Full pin list in `vendor/VERSIONS.md`.

## What Phase 2 delivered

- **Shell:**
  - **Pages:** hash router, curriculum sidebar (locked/unlocked/mastered), dashboard (streak, this-week roadmap, skills radar, resume-ready skills), light/dark/auto theme, responsive layout, keyboard shortcuts (`?` for help).
  - **Editor:** CodeMirror 5, with Run/Submit and a paste guard for No Hands checkpoints.
  - **Pyodide runner:** runs in a Web Worker. Runaway code is stopped by a timeout and the worker restarts. Package downloads are timed separately from code execution.
  - **Hidden tests:** real pytest, with test docstrings shown as test names.
  - **Error explainer:** about 30 rules, plus a "how to read a traceback" guide.
  - **Tracer:** step-through code tracer.
  - **Visuals:** NMEA field explorer and XOR checksum stepper.
  - **2D simulator:** pure Python (`app/py/pfr_sim.py`) running in the browser and locally, with a canvas renderer, 4 worlds, and noisy range/IMU/encoder/GPS/line-camera sensors.
  - **Progress:** stored in localStorage (guarded with try/catch), with JSON export/import.
  - **Review queue and tired-day mode:** Leitner boxes at 1/3/7/14/30 days. Tired-day mode is the review queue plus one drill.
  - **Mastery, project and No Hands pages:** mastery quiz (80%, reshuffled retakes), project page with .py + README export, No Hands checkpoint with a timer.
  - **Optional tutor:** loaded only on localhost when `config.local.json` exists. It supports hints, explaining errors, grill mode, explain-back grading, mock interviews, and full solutions only after 3 real attempts (enforced by the app).
- **Module 0:** 12 lessons, quiz (pool 48, draw 15), NMEA log analyzer project, No Hands RMC checkpoint, ROS 2 and C++ bridge boxes.
- **Sprint guides:** Sprint 1 (overview + 1.1 to 1.7), Sprint 2 (overview + 2.1 to 2.5), and 3 just-in-time background pages. Includes 3 wiring/frame SVGs, 5 learner pytest files (`local/sprint1`, `local/sprint2`), and an I2C scanner diagnostic sketch.
- **C for Embedded:** C1 and C2 pages and quizzes; starters in `local/c-embedded/` plus `check.sh`, which runs in the VM.
- **Interview Refreshers:** STAR intro, STAR 1, STAR 2, resume audit, A1 (dividers and pull-ups) with quizzes and rubric'd interview questions.
- **Tooling:**
  - `tools/verify.py`: local CPython checks.
  - `tools/browser_selftest.py`: headless Chrome + Pyodide, plus `--ui` page rendering.
  - `tools/new_lesson.py`: scaffolds a new lesson.
  - `.github/workflows/pages.yml`: deploys only the site folders.

## Verification log (2026-10-28)

| Scope | Local (`tools/verify.py`, Python 3.11) | Browser (`tools/browser_selftest.py`, Pyodide 3.14) |
|---|---|---|
| Module 0, lessons 0.1 to 0.12 + quiz + project + No Hands + bridges | 472/472 PASS | 159/159 PASS (examples, predicts, tracers, starter fails, reference passes, bug fixed, project, No Hands, 38 runnable quiz items) |
| Tracks (sprints, C, interview) | 115/115 PASS | every track page renders, no broken images |
| Simulator | 5/5 PASS | runs in Pyodide |
| UI (all 12 lessons, quiz, project, No Hands, module, dashboard, review, sim, settings) | | PASS, no uncaught errors |
| Deploy | | Pages live. `verification/`, `tools/`, `docs/` return 404 on the site |

Per-lesson local checks: 0.1: 29 · 0.2: 30 · 0.3: 30 · 0.4: 30 · 0.5: 31 · 0.6: 31 · 0.7: 31 · 0.8: 31 · 0.9: 30 · 0.10: 30 · 0.11: 31 · 0.12: 29.
Each challenge has 4 known-wrong solutions that fail, and the reference passes.

### Content fix (2026-10-29): no untaught protocol knowledge

Learner-reported bug: a lesson 0.1 question asked for the index of the GGA fix-quality field, but the field layout hadn't been shown anywhere.

- **New rule:** questions test the Python skill, never memorized protocol details (CONTENT_GUIDE.md).
- **Shared reference tables** in `content/reference/nmea.json`: anatomy, checksum, gga, rmc, gsa, vtg, gsv, fixquality (codes 0 to 8), ddmm, utctime. They appear next to any item that declares `refs`, and in prose and briefs via `{{ref:id}}`.
- **The GGA table** is now in lesson 0.1, where fields are first used.
- **Audit:** every Module 0 lesson item, all 48 quiz items, the project, and the No Hands checkpoint. About 60 items were fixed with a reference, made self-contained, or rewritten to test a Python skill (fs-lon-width and f-xor-range were pure recall).
- **`verify.py` enforces the rule:**
  - Challenges, bugs, the project, and the No Hands checkpoint must declare `refs`.
  - Every ref id must exist.
  - A heuristic flags field or index questions that have no reference.
- **Re-verified:** 672/672 local checks; the Pyodide self-test and the UI self-test pass, including checks that the reference tables render.

### UI fix (2026-10-29): no code-font ligatures

Learner-reported bug: the code font (Cascadia Code) rendered `!=` as ≠, `<=` as ≤, and so on. Ligatures are now off (`font-variant-ligatures: none; font-feature-settings: "liga" 0, "calt" 0`) on every code surface: inline code, pre blocks, the tracer, and the CodeMirror editor lines, which `codemirror.css` had set to `contextual`. The UI self-test checks the computed style in both light and dark themes. The track-page image check now waits for images to load, which fixed an intermittent false failure.

### UI fix (2026-10-31): predict-first shows the code

Learner-reported bug: a "Predict first" gate hid the whole visual, including the traced code and the input sentence, so questions like "which branch runs?" couldn't be answered.

- **Now:** the code (tracer) or the sentence (NMEA field explorer, XOR stepper; shown read-only) is always visible, with the prediction box right below it. Only the interactive part waits for the prediction: the step-through controls, variables, and output for the tracer, and the split table or XOR stepper for the NMEA visuals. Your prediction and the Check then appear in the same spot.
- **How:** components are now `render(el, props, gate)`. They place the gate after their inputs and return `unlock()` (`app/viz/index.js` documents this). The rule is in CONTENT_GUIDE.md: a predict-first question must be answerable from the code or sentence alone.
- **Audit:** all 13 predict-first visuals in Module 0 (11 tracers in 0.2 to 0.12, the field explorer in 0.1, and the XOR stepper in 0.4). Each one is answerable from the code or sentence now shown, so no content changes were needed. The 8 visuals without a gate already showed everything.
- **Re-verified:** the UI self-test now checks every gated visual: inputs are visible before the gate, the interactive part is hidden, and it opens after you predict. 13/13 pass, the full UI self-test passes, and `verify.py` passes 672/672. Checked by hand in the browser on lesson 0.2.

### Not yet verified (needs the learner's VM or hardware)

- [ ] C1/C2: run `bash local/c-embedded/check.sh` in the Ubuntu VM on the answer-key files. They pass the avr-gcc syntax check, but no output has been checked yet. Two outputs assume gcc 11 behavior: int16 wraparound and `__STDC_VERSION__ = 201112`.
- [ ] C2 sketch on a real Uno: compare the Serial output with `sizes_uno.expected.txt`.
- [ ] `bridge-cpp.md` (Module 0): compile once with `g++ -std=c++17 -Wall -Wextra` in the VM. There's no C++ compiler on Windows.
- [ ] `bridge-ros.md`: confirm the `nmea_navsat_driver` topic names in Humble and that the Jazzy package exists.
- [ ] AI tutor: the code path is written against `@anthropic-ai/sdk@0.133.0` but hasn't been exercised with a real key. Test it once `config.local.json` exists.
- [ ] a01 page: confirm the ATmega328P TWI V_IH figure in the datasheet.

## Next session (in priority order, by date needed)

1. **SfM concept primer, lessons CS.1 to CS.3** (coursework track). It's needed in W1, before the EECE7150 homework is due **Nov 13**.
2. **C3 to C7** (W1, from Nov 2) and **Interview W1** (STAR 3 and 4; A5 BJT and A6 MOSFET, which double as review for the Nov 19 ME5245 midterm).
3. **Weekly Boss Fight** (first one on Sunday Nov 15), **Interview Mode** (timed coding questions), and **Code Reading Drills**. These site-wide features from the spec aren't built yet.
4. **Module S: Sensor Data Toolkit** (W3, from Nov 16).
5. Minor: the browser self-test doesn't run the known-wrong solutions under Pyodide (only `verify.py` does, on 3.11).

## Learner action items

- [ ] **Order parts Order 1 now** (PLAN.md Section 6), including the dedicated 12V 2A+ supply for the motor rig.
- [ ] Start Sprint 1, milestone 1.1 as soon as the IMU arrives (target Nov 2).
- [ ] Identify the Raspberry Pi model (`cat /proc/device-tree/model`).
- [ ] When convenient: run the VM checks listed above.
- [ ] Winter break (Dec 21 to Jan 10): build a fresh Ubuntu 24.04 + Jazzy VM (PLAN.md Section 4).
