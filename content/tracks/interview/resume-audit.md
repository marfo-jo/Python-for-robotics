**About 40 minutes.** Recruiters for embedded, test, and controls co-ops spend well under a minute on a first pass through a resume. If your bullets read like a maintenance technician's job description ("Responsible for preventive maintenance..."), they file you as a technician, even though the skills underneath are the ones they want. This exercise rewrites your bullets so the engineering is visible, **without claiming anything you didn't do**.

## The one rule

> **Every bullet must be something you did or built yourself, and can defend for five minutes of follow-up questions.**

Before a bullet goes on the resume, ask yourself: "If the interviewer says *walk me through that*, can I explain how it worked, what I measured, what went wrong, and what I'd do differently?" If not, the bullet comes off, or gets rewritten to the part you *can* defend.

This rule protects you. Interviewers pick a bullet and dig. A bullet you can't defend costs more than a missing bullet.

That includes AI help. Coursework or projects where an AI wrote most of the code don't go on the resume as "built" until you can rebuild them yourself. That's what this course and the Sprint Projects are for.

## The bullet formula

**Action verb + what you did + tools/methods + measurable result**

| Part | Weak | Strong |
|---|---|---|
| Action verb | "Responsible for", "Helped with", "Worked on" | Diagnosed, Built, Designed, Automated, Reduced, Validated, Implemented, Wrote, Characterized |
| What | "machines" | "intermittent overload trips on a packaging conveyor" |
| Tools / methods | (none) | "using motor current logging, PLC I/O diagnostics, and the fault history" |
| Result | (none) | "eliminating the fault for 3+ months and recovering about 2 hours of production per week" |

Good engineering verbs by category:

- **Debugging**: diagnosed, isolated, traced, root-caused, resolved
- **Building**: built, designed, implemented, wrote, wired, integrated
- **Testing**: validated, verified, characterized, tested, measured, benchmarked
- **Improving**: reduced, automated, standardized, streamlined, documented

Tools are where your EE background shows. Name them: multimeter, oscilloscope, clamp meter, megger, PLC software and online diagnostics, HMI fault logs, VFD parameters, thermal camera, schematics and wiring diagrams. Later, from this course: C, Python, pyserial, pytest, NumPy, Matplotlib, Git, GitHub Actions, I2C, UART, ROS 2.

## Before → after examples (generic scenarios, not your resume)

These are invented to show the transformation. Use them to learn the pattern, then write your own from your real work.

**1. Preventive maintenance**

- Before: "Performed preventive maintenance on production equipment."
- After: "Executed and revised monthly PM routines for 12 packaging machines; added bearing-temperature checks that caught 2 failing bearings before breakdown."

**2. Troubleshooting**

- Before: "Troubleshot electrical and mechanical problems."
- After: "Diagnosed intermittent PLC input faults on a conveyor line by tracing 24 V sensor circuits and monitoring I/O status online, cutting average repair time on that fault from about 2 hours to 30 minutes."

**3. Documentation**

- Before: "Helped with documentation."
- After: "Wrote a 15-step troubleshooting guide for recurring VFD faults, ordered by likelihood with expected readings at each step; the night shift used it to clear the fault without a callout."

**4. Installation**

- Before: "Installed new equipment."
- After: "Wired and commissioned 3 replacement proximity sensors and a motor starter from schematics; verified I/O mapping point-to-point before handover."

**5. Data**

- Before: "Kept maintenance records."
- After: "Logged failure and repair data for 40 machines in the CMMS and identified the top 3 repeat-failure assets, which became the focus of the next quarter's PM changes."

Notice what changed every time: a specific object, a method, a tool, and an honest outcome. Notice also what *didn't* happen: nobody became a "lead engineer" or "architected a predictive maintenance system". Inflation is easy to spot and hard to defend.

## The audit exercise (30 minutes)

Do this in your own notes or a copy of your resume, not in the course files.

**Step 1: inventory (10 minutes).** For each job, list everything you actually did, as plain notes. Don't filter yet. Prompts:

- What failures did you diagnose? Which were hard?
- Which tools did you use weekly?
- What did you build, wire, program, modify, or install?
- What did you write: procedures, checklists, reports, training notes?
- What did you measure or log?
- What got better because of you? Do you know roughly how much?
- What did you do that wasn't in your job description?

**Step 2: rewrite (15 minutes).** For each of your current bullets:

- [ ] Replace "responsible for", "helped", "worked on", and "duties included" with a specific action verb
- [ ] Name the specific equipment or system
- [ ] Add the tools or methods you used
- [ ] Add a result (number if honest; concrete outcome otherwise)
- [ ] Keep it to one or two lines
- [ ] Apply the rule: can I defend this for five minutes?

**Step 3: rank (5 minutes).** For an embedded, test, or controls posting, put the bullets that show **diagnosis, measurement, documentation of procedures, and wiring/integration** first. Pure mechanical tasks (lubrication, cleaning, part replacement with no diagnosis) go last or get merged.

### Self-check for each bullet

| Question | Pass? |
|---|---|
| Starts with a strong verb (not "responsible for") | |
| Says what, specifically | |
| Names at least one tool or method | |
| Has a result, and any number is honest | |
| I did this myself (or my part is stated precisely) | |
| I can talk about it for five minutes | |
| A robotics hiring manager would see a transferable skill | |

## Common mistakes

- **Listing duties instead of accomplishments.** A job description says what anyone in the role would do. A bullet says what *you* did and what changed.
- **Inflated titles or scope.** "Led" when you helped; "designed" when you followed a drawing. It falls apart in the first follow-up.
- **Numbers with no basis.** "Improved efficiency by 37%." Compared with what, measured how? Use honest estimates ("about", "roughly") or none.
- **Buzzword stuffing.** "Leveraged synergistic predictive analytics." Say what you did.
- **Hiding the maintenance experience.** Don't delete it. Reframe it. Systematic diagnosis, reliability data, and procedures are exactly what test and validation teams want.
- **Listing tools you can't use.** If "Python" is on your resume, expect a Python coding question. List it once you can pass one. (Soon.)

## What this course will add (resume-ready skills)

The plan's rule: a skill appears in your dashboard's "resume-ready skills" list only after you pass its module's mastery quiz and its No Hands checkpoint. Each project's bullet is filled in with **your measured numbers** after its tests pass, and you must pass a 5-question "defend this bullet" quiz before it goes on the resume.

The planned bullets (shapes only; the numbers come from your own results):

| Project | When | Bullet shape |
|---|---|---|
| **Sprint 1: IMU data pipeline** | minimal ~Nov 10, full ~early Dec | "Built an MPU-6050 IMU pipeline: register-level I2C firmware in C, checksummed binary serial protocol, Python driver with N pytest tests in CI; characterized noise with Allan variance (ARW = X °/√h)." |
| **Sprint 2: DC motor test rig** | ~mid Dec | "Designed an automated DC motor test rig (encoder, INA219, DS18B20); identified a first-order model (τ = X ms, R² = Y) and tuned a PI speed loop that met predicted rise time within Z%; ran an N-cycle endurance test with drift analysis." |
| **WALL-E ROS 2 driver rewrite** | spring | "Rewrote the WALL-E robot's ROS 2 stack from scratch: Arduino serial bridge, Raspberry Pi rclpy node, teleop, systemd/udev deployment." |
| **Your maintenance experience, reframed** | now | "Applied PLC troubleshooting and preventive maintenance methods to robot test and validation (root-cause analysis, reliability data)." |

Until a project's milestone is done, it can go on the resume only honestly: as "in progress", with just the parts you've finished. For example, after Sprint 1 milestone 1.3 you could write "Building an IMU data pipeline (Arduino C firmware, Python serial logger, CSV logging and plotting); in progress", and you must be able to defend every word of it.

Checklist:

- [ ] I inventoried what I actually did in each job
- [ ] Every bullet starts with a strong action verb
- [ ] Every bullet names a tool or method
- [ ] Every bullet has an honest result
- [ ] I removed or rewrote every bullet I couldn't defend for five minutes
- [ ] I ordered bullets for an embedded/test/controls posting
- [ ] I noted which course projects will add bullets, and when
