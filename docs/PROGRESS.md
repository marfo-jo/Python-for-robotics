# Build Progress

The source of truth for the plan is [PLAN.md](PLAN.md). Update this file at the end of every build session.

## Phase status

| Phase | Scope | Status | Date |
|---|---|---|---|
| 1 | Research, curriculum, roadmap, projects, shopping list, architecture | ✅ Approved and committed | 2026-10-28 |
| 2 | Site shell + Module 0 + Sprint milestone guides + first week of C and Interview tracks | ⏳ Next | |
| 3+ | One complete module per session, just ahead of the learner | ⏸ Not started | |

## Environment log

| Date | Change | Approved by learner |
|---|---|---|
| 2026-10-28 | `pyserial 3.5` installed in conda env `robotics-course` | Yes |

Baseline `robotics-course` env (2026-10-28): Python 3.11.18, numpy 2.4.6, matplotlib 3.11.2, opencv-python 4.14.0, pytest 9.1.1, pyserial 3.5.
Browser runtime target: Pyodide 314.0.7 (numpy 2.4.6, matplotlib 3.10.8, opencv-python 4.11.0.86, scipy 1.18.0, pytest 9.0.2).

## Phase 2 checklist (from PLAN.md)

- [ ] Add GitHub remote (public repo), rename `master` to `main`
- [ ] Create the private answer-key repo `python-for-robotics-answer-key` and clone it into gitignored `verification/`
- [ ] Site shell: layout, router, theme, sidebar map, progress store (export/import), streak, radar
- [ ] Editor (CodeMirror 6) + Pyodide worker runner + pytest harness + error explainer
- [ ] 2D simulator core + first visualization components (code tracer first)
- [ ] Optional AI tutor module (`config.local.example.json`; `config.local.json` gitignored)
- [ ] `tools/verify.py` and `tools/new_lesson.py`
- [ ] Module 0 complete (lessons 0.1 to 0.12, quiz, project, bridges), each lesson verified locally
- [ ] Sprint 1 and Sprint 2 milestone guides (wiring, hints, test files; no solution code)
- [ ] C for Embedded W0 (C1, C2) and Interview Refreshers W0 (STAR 1 and 2, A1)
- [ ] GitHub Pages deploy workflow (site folders only)

## Lesson verification log

Each lesson is marked done only after `tools/verify.py` passes locally. Record it here.

| Lesson | Examples | Reference passes | Wrong solutions fail | Bug exercise | Date |
|---|---|---|---|---|---|
| (none yet) | | | | | |

## Learner action items

- [ ] **Place parts Order 1 now** (PLAN.md Section 6), including the dedicated 12V 2A+ supply for the motor rig
- [ ] Identify the Raspberry Pi model (`cat /proc/device-tree/model`)
- [ ] Winter break (Dec 21 to Jan 10): build a fresh Ubuntu 24.04 + Jazzy VM (PLAN.md Section 4)
