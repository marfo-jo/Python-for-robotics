**About 30 minutes.** This is your most important behavioral story for test, validation, hardware-integration, and embedded roles. Versions of it get asked in almost every interview:

- "Tell me about a time you diagnosed a difficult equipment failure."
- "Describe the hardest technical problem you've debugged."
- "Walk me through how you troubleshoot something you've never seen before."
- "Tell me about a time you found the root cause, not just the symptom."

One well-built story can answer all four. Read [How to build a STAR story](#/t/interview/star-intro) first if you haven't.

## Step 1: pick the incident (5 minutes)

Write down two or three real failures you diagnosed. Then pick the one that scores best on these:

- [ ] **You did the diagnosis yourself** (or led it), not just watched or swapped the part someone else picked
- [ ] **It wasn't obvious.** The first guess was wrong, or the fault was intermittent, or several causes were possible
- [ ] **You used measurements or data**: a meter, a scope, the PLC's I/O status or online view, fault logs, trend data, a thermal camera, vibration readings
- [ ] **There's a clear result**, ideally with a number (downtime, recurrence, cost)
- [ ] **You can still remember the details** well enough to answer three follow-up questions

A short, clean story about a sensor with a broken wire, where you methodically ruled things out, beats a dramatic story where you can't remember what you actually measured.

## Step 2: pull out the details (10 minutes)

Answer these in your own notes. Short phrases are fine. Don't polish yet; the goal is to recover facts.

**Situation**

1. Where were you working, and what was your role? (Job title, type of facility.)
2. What equipment was it? Describe it the way you'd explain it to a software engineer in one sentence.
3. What was the symptom? What did operators see or report?
4. How often did it happen? How long had it been going on?
5. What did it cost when it happened? (Minutes of downtime, scrap, overtime, a safety risk, a missed shipment.)

**Task**

6. Why was it *your* job? Were you assigned it, on call, or did you volunteer?
7. What constraints did you have? (Production pressure, no spare parts, night shift alone, no documentation.)

**Action** (this is the part to get right)

8. What did you check *first*, and why that first?
9. What did that tell you? What did it rule out?
10. What was your next hypothesis, and how did you test it?
11. Which tools did you use, and what exactly did each one show? (For example: "the multimeter showed 24 V at the terminal block but 0 V at the sensor connector".)
12. Was there a wrong turn? What did you try that *didn't* work, and what did you learn from it? (Interviewers like an honest dead end that you recovered from.)
13. What was the root cause in the end?
14. How did you fix it, and how did you **verify** the fix? (Ran it for a shift? Logged it? Watched it through the conditions that used to trigger it?)
15. Who did you involve, and what did each person do? (Keep "I" and "we" straight.)

**Result**

16. What happened right afterwards?
17. What happened over the following weeks? Did it recur?
18. Any numbers you can honestly stand behind? ("About", ranges, and "roughly" are fine.)
19. What did you change so it wouldn't happen again: a PM task, a checklist, a spare part kept in stock, a note in the manual, training for the operators?
20. What did you learn, and how does that show up in how you debug robots or firmware now?

<details><summary>Stuck on the numbers? (prompts)</summary>

You may not have measured anything formally, but you probably know roughly:

- How long a stop lasted before you got there, and how long the fix took
- How many times a week or a shift it used to happen
- Whether it happened again in the time you stayed on the job
- What a new part would have cost, if you repaired instead of replaced
- How many machines or lines had the same issue, if your fix was applied to others

If none of these apply, use a qualitative result honestly: "the operators stopped calling us about it", "it became a 10-minute fix instead of a callout".

</details>

## Step 3: write it in STAR form (10 minutes)

Use this template. Aim for 150 to 300 words, which is 60 to 120 seconds spoken.

```
S: At [place], I was a [role]. [Equipment] kept [symptom], about [frequency],
   costing [impact].

T: I was [assigned / on call / asked] to [find the root cause / get it running],
   with [constraint].

A: First I [checked X] because [reason]. That showed [finding], which ruled out [Y].
   Next I [measured/tested Z with tool], and found [finding].
   [Optional: I first suspected W, but when I tested it, ... so I moved on.]
   The root cause was [cause]. I [fix], and verified it by [verification].
   I [told / documented / handed over to] [who].

R: [Immediate result]. Over the next [period], [recurrence / downtime / number].
   I also [prevention step] so it wouldn't happen again.
   The lesson I took was [lesson], and I use it now when [robotics / embedded example].
```

Then **say it out loud** with a timer. Twice. Writing and speaking are different skills, and the interview is spoken.

## Step 4: self-review (5 minutes)

Score your draft against this rubric. It's the same one the mock interviewer uses on the quiz below.

| Check | Yes / no |
|---|---|
| Situation and Task together take under 30 seconds | |
| At least 3 distinct actions, each with a *reason* | |
| At least one real measurement or piece of data, and what it told you | |
| Hypotheses were tested, not just guessed (something was *ruled out*) | |
| A clear root cause (not only "I replaced the part") | |
| The fix was verified | |
| The result has a number or a concrete, honest outcome | |
| There's a prevention or follow-up step | |
| "I" for my actions, "we" only for shared context, others credited | |
| A software interviewer could follow it (jargon explained or cut) | |
| 60 to 120 seconds spoken | |
| Ends with a lesson or a bridge to robotics | |

## Common pitfalls (and fixes)

- **Too vague.** "There was a problem with a machine and I troubleshot it and fixed it." Fix: name the equipment, the symptom, and the specific measurement that cracked it.
- **No result.** The story ends at "and I replaced the sensor." Fix: add what happened next, ideally with a number, and how you knew it was fixed.
- **Too much jargon.** "I forced I:3/5 in RSLogix, checked the 1756-IB16, then the PNP prox on the M12..." Fix: "I used the PLC's online view to force the input and see whether the controller saw the sensor. It didn't, so the problem was between the sensor and the input card." Then go deeper if they ask.
- **Blaming others.** "The day shift never documented anything." Fix: state the fact neutrally ("there was no record of the last change, so I started from the wiring diagram") and, ideally, mention what you did about it.
- **Parts cannon.** Swapping parts until it worked isn't diagnosis. If that's honestly what happened, pick a different story, or tell it as a lesson: "I learned to measure before swapping."
- **Hero story.** You did everything alone, at 3 a.m., and saved the plant. Even when it's mostly true, it can sound inflated. Credit the people who helped.
- **Inventing details.** Don't. Every follow-up question becomes a risk. Use "about" and "roughly" for things you don't remember precisely.

## Bridge to robotics (one or two sentences to end on)

Pick the one that's true for you, or write your own:

- "It's the same process I use when an I2C sensor stops responding: power, then wiring, then the bus, then the data."
- "It taught me to log before I guess, which is exactly how I approach intermittent bugs in my robot now."
- "Since then I've treated 'it only happens sometimes' as data, not bad luck: it tells you which conditions to test."

Checklist:

- [ ] I picked one real incident that meets the Step 1 criteria
- [ ] I answered the 20 questions in my own notes
- [ ] I wrote a 150 to 300 word STAR draft
- [ ] I said it out loud with a timer and it was 60 to 120 seconds
- [ ] It passes at least 10 of the 12 self-review checks
- [ ] I answered the interview questions below in the text boxes (out loud first)
