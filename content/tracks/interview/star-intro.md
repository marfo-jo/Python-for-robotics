**About 25 minutes.** Behavioral questions ("Tell me about a time you...") are a big part of most co-op interviews, and for embedded, test, and controls roles they're where your maintenance experience counts most. A hiring manager for a test or validation role wants someone who has stood in front of broken equipment, under time pressure, and found the real cause. You've done that. This page teaches you to tell it in a way an engineering interviewer can score.

## What STAR is

STAR is a four-part structure for a story about something you actually did:

| Part | Question it answers | Rough share of the time |
|---|---|---|
| **S**ituation | Where were you, and what was going on? Just enough context to follow. | about 15% |
| **T**ask | What were *you* responsible for? What was at stake? | about 10% |
| **A**ction | What did *you* do, step by step, and *why* did you choose each step? | about 50 to 60% |
| **R**esult | What happened, ideally in numbers? What did you learn or change afterwards? | about 15 to 20% |

The Action is the heart of it. Most weak answers spend a minute on the Situation ("so the plant had three lines and the second shift was...") and then rush the part the interviewer is actually scoring.

**Length: 60 to 120 seconds spoken.** That's about 150 to 300 words. Shorter and you sound vague; longer and you lose them. The interviewer will ask follow-ups if they want more depth, and follow-ups are good: they mean the story landed.

## What interviewers listen for

An interviewer is usually filling in a scorecard with a few competencies. For the roles you're applying to, those are typically:

- **Structured problem solving.** Did you form hypotheses and test them, or swap parts until something worked? "I measured X, which ruled out Y, so I checked Z" is gold.
- **Ownership.** What did *you* do? Did you follow through after the immediate fix?
- **Technical depth.** Can you name the tools, signals, and measurements? (Then can you explain them simply when asked?)
- **Communication.** Did you tell the right people, document it, hand it over?
- **Learning and improvement.** Did you change something so it wouldn't happen again: a checklist, a PM interval, a spare-parts stock, a test?
- **Honesty.** Can you say what went wrong and what you'd do differently without blaming anyone?

### Quantify the result

Engineers trust numbers. A result with a number is believable and memorable. Maintenance work gives you plenty of honest ones:

| Metric | What it means | Example phrasing |
|---|---|---|
| Downtime | time the equipment couldn't run | "brought the line back after 40 minutes instead of a full shift" |
| MTTR (mean time to repair) | average time from failure to fixed | "cut our average repair time on that fault from about 2 hours to 30 minutes" |
| MTBF (mean time between failures) | average run time between failures | "the fault went from weekly to not recurring in the 3 months I was there" |
| Defect or reject rate | bad parts out of total | "rejects dropped from about 4% to under 1%" |
| Recurrence | did it come back? | "it didn't recur for the rest of my contract" |
| Time or cost saved | hours, dollars, spares | "saved buying a $2,000 replacement drive" |
| Adoption | did other people use what you made? | "the checklist became part of the night shift's handover" |

**Only use numbers you can defend.** If you don't remember exactly, say "about" or "roughly", or use a range: "about 30 to 45 minutes". If you never measured it, describe the result qualitatively and honestly ("the operators stopped calling us for that fault"). An interviewer who catches one inflated number stops believing the rest.

### Keep "I" and "we" straight

Interviewers hire *you*, not your team. But claiming the team's work as yours is dishonest, and it falls apart under follow-up questions.

- Use **"we"** for context and shared outcomes: "We had a recurring jam on the packaging line."
- Use **"I"** for what you personally did: "I pulled the fault history from the HMI and noticed it only happened after a cold start."
- Credit others precisely: "My supervisor approved the part order; I did the replacement and the testing."
- A good self-test: for every "I" sentence, could you answer "how exactly did you do that?" in detail?

## How maintenance stories map to robotics roles

Your stories don't need to be about robots. They need to show the skills robotics teams hire for. Here's how the overlap looks:

| What you did in maintenance | The robotics skill it proves | Roles that care most |
|---|---|---|
| Traced an intermittent fault with a meter, the PLC's I/O status, and the fault log | systematic debugging, measurement, root cause | test and validation, hardware integration |
| Followed and improved preventive maintenance schedules | reliability thinking, failure modes, data over time | reliability, test, field robotics |
| Wrote or improved a troubleshooting checklist or procedure | test procedures, documentation, repeatability | test and validation, QA |
| Brought a machine back up fast under production pressure | working under pressure, prioritizing, safe recovery | field robotics, deployment, support engineering |
| Replaced a sensor, motor, or drive and verified it | hardware integration, verification after change | hardware integration, embedded |
| Caught a safety or compliance issue | attention to detail, standards | QA, test, safety-critical robotics |

When you tell the story, **name the bridge** in the last sentence or two: "That's the same process I use now when my IMU reads garbage: check power, then the bus, then the data." It shows the interviewer you see the connection, so they don't have to make it for you.

## Worked example (a generic scenario, not your story)

> This example is made up to show the structure. It is **not** your experience. Your stories must come from things you actually did. The STAR 1 and STAR 2 pages walk you through building yours.

**Question:** "Tell me about a time you diagnosed a difficult equipment failure."

**Situation.** "I was a maintenance technician at a bottling plant. One conveyor kept stopping on a motor overload fault two or three times a shift, and each stop cost about 15 minutes of production."

**Task.** "I was assigned to find the root cause, because resetting the overload was only buying time and the operators were losing trust in the line."

**Action.** "First I checked the fault log on the HMI. The trips weren't random: they clustered in the first hour after start-up. That pointed away from an electrical fault and toward something mechanical that changed with temperature. I measured the motor current with a clamp meter during start-up: it was running about 20% above nameplate for the first 30 minutes, then settling. I ruled out the motor by uncoupling it: it ran at normal current unloaded. So the extra load was in the drive train. I found a gearbox running on oil that was too thick for the cold mornings. I checked the manual, confirmed the right grade with my supervisor, drained and refilled it, and then logged the current for the next three cold starts."

**Result.** "Start-up current dropped to nameplate, and the overload trips stopped completely for the next two months I tracked it. I added the gearbox oil grade to the PM sheet so it wouldn't get topped up with the wrong oil again. It taught me to look at *when* a fault happens before I look at *what* failed. I use the same habit debugging sensors now: I log first, then form a hypothesis."

Notice:

- The Situation is two sentences. The Action is more than half the answer.
- Every step has a **reason** ("that pointed away from...", "I ruled out...").
- There's a **measurement** (clamp meter, current vs nameplate) and a **test** of the hypothesis (uncoupling the motor).
- The Result has a number, a prevention step, and a bridge to robotics.
- "I" is used for actions and the supervisor is credited for the approval.
- It takes about 90 seconds spoken.

## Fill-in template

Copy this into your own notes (not into the course files) and fill it in for each story.

```
QUESTION(S) THIS STORY ANSWERS:
  e.g. "diagnosed a failure", "worked under pressure", "a time you were wrong"

SITUATION (1 to 2 sentences): where, what equipment, what was going wrong
  ...

TASK (1 sentence): what YOU were responsible for, and what was at stake
  ...

ACTION (4 to 6 steps, each with a "because"):
  1. I ... because ...
  2. I measured/checked ... which showed ...
  3. That ruled out ... so I ...
  4. I fixed/changed ...
  5. I verified it by ...
  6. I told/documented ...

RESULT (numbers if you have them, honest estimates marked "about"):
  - immediate outcome:
  - measured improvement (downtime, MTTR, recurrence, defects):
  - what I changed so it wouldn't happen again:
  - what I learned / the bridge to robotics:

FOLLOW-UPS I SHOULD BE READY FOR:
  - "What would you do differently?"
  - "How did you know it was fixed?"
  - "What did your team/supervisor do?"
  - "What was the hardest part?"
```

## Common beginner mistakes

- **Too vague**: "I fixed a lot of machines and was good at troubleshooting." That's a claim, not a story. Pick *one* incident.
- **No result**, or a result of "and then it worked." Say what changed, by how much, and what you did to stop it recurring.
- **Too much jargon**: a wall of part numbers and PLC addresses loses a software interviewer. Name the tool, then say what it told you in plain words.
- **Blaming others**: "The previous tech had wired it wrong." Even if true, say what you found and fixed, factually and without judgment.
- **"We" all the way through**, so the interviewer can't tell what you did.
- **Memorizing a script word for word.** Know your beats (S, T, the 4 to 6 action steps, R) and tell it naturally. Scripts sound recited and break when you're interrupted.

## Your stories for this season

The plan calls for six STAR stories. Start with the two that map most directly to test and embedded roles:

1. **Diagnosing a failure**: STAR 1 page.
2. **Building a troubleshooting checklist**: STAR 2 page.
3. Reducing downtime
4. A QA or compliance catch
5. A WALL-E integration problem you solved
6. A team conflict or deadline from the ME5245 project

Checklist:

- [ ] I can say what each STAR letter means and how long each part should be
- [ ] I've listed 3 to 5 real incidents from my maintenance work that I could tell
- [ ] For each, I've noted any honest numbers I remember (downtime, frequency, cost)
- [ ] I've told the worked example out loud once, timing it, to feel what 90 seconds is
