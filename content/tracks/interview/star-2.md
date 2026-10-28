**About 30 minutes.** STAR 1 showed you can fix a problem. This story shows something rarer and more valuable to an engineering team: you can turn what you learned into a **process other people can repeat**. That's the core of test and validation work. A test procedure is a troubleshooting checklist run *before* the failure instead of after it.

Questions this story answers:

- "Tell me about a time you improved a process."
- "Describe a time you created documentation or a procedure that others used."
- "How have you helped your team avoid repeating the same problem?"
- "Tell me about a time you took initiative beyond your assigned job."

## Step 1: find the checklist in your history (5 minutes)

It may not have been called a checklist. Any of these count, **if you made or substantially improved it**:

- A troubleshooting flowchart or a "check these first" sheet for a recurring fault
- A start-up, shutdown, or changeover procedure
- A preventive maintenance task list, or changes to one (new checks, new intervals)
- A handover sheet between shifts
- A labeled wiring or I/O reference you made because the official one was wrong or missing
- A spare-parts list or a kit you put together for a common failure
- Training notes you wrote for a newer technician

Pick the one where:

- [ ] **You built it, or you led the change.** Following someone else's checklist is a different story.
- [ ] **There was a real reason for it**: a recurring fault, a slow repair, mistakes during handovers, a near miss
- [ ] **Other people used it**, or it changed how the work was done
- [ ] **You know something about the effect**: faster repairs, fewer repeats, fewer callouts, easier training

If you honestly don't have one, this story can be about a personal method you developed and then shared, or you can save this page for later and build the story around a bring-up checklist you write yourself while getting the IMU talking in Sprint 1 milestone 1.1 (wiring, I2C scan, `WHO_AM_I`). Don't stretch an experience into something it wasn't.

## Step 2: pull out the details (10 minutes)

Answer in your own notes.

**Situation and Task**

1. What problem made a checklist necessary? Be specific: which fault, which machine, which handover.
2. How was it handled *before* your checklist? What went wrong with that? (For example: every tech started from scratch, the same wrong part got swapped, the night shift couldn't fix it alone.)
3. What did that cost? (Repeat callouts, repair time, scrap, frustration, a safety concern.)
4. Was it assigned to you, or did you decide to do it? Who did you need to convince?

**Action**

5. Where did the content come from? (Your own repair notes, fault logs, manuals, asking experienced technicians, operator interviews.)
6. How did you decide the **order** of the steps? (Most likely cause first? Quickest check first? Safest first? Splitting the system in half?)
7. What did the format look like? (A laminated sheet on the cabinet, a flowchart, a page in the CMMS, a binder section.)
8. Did you include measurements with expected values? ("24 V ±10% at terminal 4", "motor current under 6 A at idle".)
9. How did you test it? Did someone else try it while you watched? What did you change after that?
10. How did you get people to actually use it?

**Result**

11. Did repair time, repeat faults, or callouts change? By roughly how much?
12. Who used it? Is it still in use, as far as you know?
13. What would you improve now?
14. How is this like writing a test procedure, a README, or a debug guide for a robot?

## Step 3: write it in STAR form (10 minutes)

```
S: At [place], [fault / process] kept [problem]. Each time, [how it was handled],
   which cost [impact].

T: I [was asked to / decided to] [make the fix repeatable / cut repair time],
   so that [who] could [handle it without me / avoid the same mistake].

A: I started by [collecting data: logs, notes, interviews] and found [pattern].
   I ordered the checks [quickest / most likely / safest first] because [reason].
   For each step I wrote [the expected reading / a pass-fail criterion].
   I had [a colleague] try it on [the next occurrence], watched where they got stuck,
   and revised [what].
   I [posted it / added it to the PM system / trained the shift].

R: [Repair time / repeats / callouts] went from [before] to [after, honest estimate].
   [Who] used it, and [still in use / adopted elsewhere].
   It showed me that [lesson], which is how I approach [test procedures / robot debugging] now.
```

Say it out loud twice with a timer. Target 60 to 120 seconds.

## The engineering bridge

This story is your best answer to "Why would a maintenance background make you good at test and validation?" Make the connection explicit:

| Your checklist had... | A test procedure has... |
|---|---|
| steps in a deliberate order | test steps in a deliberate order |
| an expected reading for each check | a pass/fail criterion for each test |
| a "if this fails, go to step N" branch | a failure-handling path and a defect report |
| a revision after someone else used it | a review and a dry run before release |
| a place on the cabinet where people find it | version control and a README |

And in this course: your Sprint 1 IMU pipeline will have a pytest suite, which is a troubleshooting checklist the computer runs for you every time you push code.

## Self-review rubric

| Check | Yes / no |
|---|---|
| The problem that motivated the checklist is specific | |
| The "before" state and its cost are clear | |
| I explain *how* I built it: sources, ordering logic, expected values | |
| I tested it with someone else and revised it | |
| It's clear what I did vs what others contributed | |
| The result is concrete (time, repeats, adoption), and honest | |
| There's a lesson, and a bridge to test procedures or robotics | |
| No jargon wall; a software interviewer could follow | |
| 60 to 120 seconds spoken | |

## Common pitfalls

- **Too vague**: "I made a lot of checklists." Pick one. Describe what was on it.
- **No result**: the story ends when the checklist was printed. What changed after people used it?
- **Too much jargon**: list two or three example steps in plain words, not all twenty with tag names.
- **Blaming others**: "Nobody else bothered to document anything." Say what was missing, neutrally, and what you did about it.
- **Claiming a team document as yours.** If you contributed a section, say "I wrote the section on..." That's still a good story.
- **Skipping the "how"**: the ordering logic and the expected values are what make you sound like an engineer. Don't leave them out.

Checklist:

- [ ] I picked a real checklist, procedure, or reference I built or led
- [ ] I answered the 14 questions in my own notes
- [ ] I wrote a 150 to 300 word STAR draft
- [ ] I said it out loud with a timer
- [ ] I can explain in two sentences how this makes me good at test and validation
- [ ] I answered the interview questions below (out loud first)
