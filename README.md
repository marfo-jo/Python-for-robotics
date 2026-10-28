# Python for Robotics

An interactive, test-graded course for learning Python and robotics software by doing,
in the style of freeCodeCamp: short lessons, an in-browser editor running **real Python**
(Pyodide), instant hidden-test feedback, a 2D robot simulator, and hardware projects
that become a GitHub portfolio.

## Run it locally

```powershell
conda activate robotics-course
python -m http.server 8000
```

Then open <http://localhost:8000>. There's no build step. Progress is saved in your
browser, and you can export it as JSON from **Settings**.

## What's inside

| Area | Where |
|---|---|
| App code (ES modules, no build) | `app/` |
| Python runtime support (test harness, tracer, simulator) | `app/py/` |
| Lessons, quizzes, projects, tracks (data, not code) | `content/` |
| Local exercises (C, hardware, pytest files you run yourself) | `local/` |
| Content verification (local Python + headless browser) | `tools/` |
| Plan, progress, and authoring guide | `docs/` |

Every lesson has worked examples, an interactive visual, predict-the-output questions,
a coding challenge graded by hidden pytest tests, a find-the-bug exercise, and an
explain-it-back step. Modules end with a mastery quiz (80% to unlock the next), a No
Hands checkpoint, a project, and "Bridge to Real Robots" (ROS 2) and "Bridge to C++"
boxes.

## Optional AI tutor

The site works fully without it. To enable the Socratic tutor locally, copy
`config.local.example.json` to `config.local.json` and add an Anthropic API key. That
file is gitignored and never deployed, and the tutor only runs on `localhost`. The
tutor gives tiered hints and won't hand over a solution until you've made three real
attempts and explicitly ask for one.

## Verifying content

```powershell
python tools/verify.py            # local CPython: examples, predictions, hidden tests
python tools/browser_selftest.py  # headless Chrome + Pyodide: same checks in the browser
python tools/browser_selftest.py --ui
```

Reference solutions live in a separate private repository and are never published.
The site ships only the tests.

## Deployment

Pushing to `main` deploys `index.html`, `app/`, `content/`, and `local/` to GitHub
Pages (`.github/workflows/pages.yml`).
