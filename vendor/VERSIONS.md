# Pinned third-party versions

Everything loads from a CDN at an exact version. There's no build step. Change a
version only deliberately, then re-run `python tools/browser_selftest.py`.

| Library | Version | Loaded from | Used for |
|---|---|---|---|
| Pyodide | 314.0.7 (Python 3.14) | cdn.jsdelivr.net/pyodide/v314.0.7/full/ | Python in the browser (Web Worker) |
| ↳ numpy | 2.4.6 | Pyodide package | arrays |
| ↳ matplotlib | 3.10.8 | Pyodide package | plots (Agg backend → PNG) |
| ↳ opencv-python | 4.11.0.86 | Pyodide package | computer vision lessons (verified loading 2026-10-28) |
| ↳ scipy | 1.18.0 | Pyodide package | MPC / optimization lessons |
| ↳ pytest | 9.0.2 | Pyodide package | hidden tests (same files as local verification) |
| CodeMirror | 5.65.16 | cdnjs | editor (python + clike modes, matchbrackets) |
| marked | 12.0.2 | cdnjs | Markdown rendering |
| DOMPurify | 3.1.6 | cdnjs | HTML sanitizing |
| KaTeX | 0.16.11 | cdnjs | math (`$$…$$` and `\( … \)` only) |
| @anthropic-ai/sdk | 0.133.0 | cdn.jsdelivr.net/npm/…/+esm | optional AI tutor (loaded only when enabled) |

Local verification environment (conda `robotics-course`, checked 2026-10-28):
Python 3.11.18, numpy 2.4.6, matplotlib 3.11.2, opencv-python 4.14.0, pytest 9.1.1,
pyserial 3.5.

**Why CodeMirror 5, not 6:** version 6 is distributed as many ES modules that must
share one instance of `@codemirror/state`. That's fragile without a bundler. 5.65.16
is a single script, which fits the no-build rule.
