**Read this first (15 minutes).** What you're building, how it's kept separate from your ME5245 coursework, the safety rules, and the five milestones.

## What you're building

A **DC motor test rig**: an encoder gear motor driven through the L298N, instrumented with an INA219 current sensor and a DS18B20 temperature probe, and run by **Python scripts that execute automated tests and analyze the results**.

```
Python test runner --commands--> Uno firmware --PWM--> L298N --> motor + encoder
       ^                           |  ^                              |
       |                           |  +---- encoder counts (ISR) ----+
       +------ CSV stream ---------+  +---- INA219 (I2C): bus V, current
          (speed, current, temp)      +---- DS18B20 (1-Wire): motor can temperature
```

Over five milestones you will:

1. Wire the rig and write firmware that counts encoder ticks in an interrupt, accepts PWM commands, and streams speed, current, voltage, and temperature.
2. Write a Python **step-test runner** that executes a test plan automatically, with safety limits, and logs everything.
3. **Derive the motor's equations of motion**, fit a first-order model to your step data with least squares (system identification), simulate it, and compare simulation against measurement.
4. **Design a PI speed controller from your identified model**, run it on the Uno, and compare the predicted response with the measured one.
5. Run an automated **endurance test** (hundreds of load cycles), plot drift over time, and write a **one-page test report** you can attach to applications as a work sample.

## Keep this separate from ME5245 Project 2

**Sprint 2 is speed control of a motor on your own rig, in your own repo. It is not your ME5245 Project 2** (the graded team project on position control), and nothing on this site helps with that project.

- Different problem: this rig controls **speed** (velocity) with a PI loop. Project 2 controls **position**. Don't port this code into Project 2, and don't bring Project 2 code, team members' work, or course-provided code into this repo.
- Different hardware and repo: your own motor, driver, and sensors; your own GitHub repo.
- **Check the ME5245 collaboration and academic-integrity policy** (the syllabus, or ask the instructor) before you make this repo public, and before showing it to classmates. If the policy restricts sharing related work until grades are final, keep the repo private until then. When in doubt, ask in writing and keep the answer.
- The site's AI tutor will decline questions about graded coursework and point you back to general lessons. That's by design.

The concepts overlap with your ME5245 lectures (DC motor modeling, feedback control), and that's fine: understanding transfers. Work products don't.

## Why this project, for interviews

Test and validation, hardware integration, and controls roles all ask some version of these:

| Interview question | Where your answer comes from |
|---|---|
| "How would you characterize an unknown motor?" | 2.2 and 2.3: automated step tests, a first-order fit, R² against held-out data |
| "Design a speed controller for it." | 2.4: PI from the model, with predicted vs measured rise time |
| "How do you make an automated test safe?" | 2.1 and 2.2: command watchdog, current and temperature limits, a guaranteed stop on exit |
| "Tell me about a test report you wrote." | 2.5: your one-page endurance report |
| "How do you read an encoder? What's quadrature?" | 2.1 |

This is where your maintenance background is the strongest asset you have. Trending a motor's current and temperature over hundreds of cycles is preventive maintenance with a data pipeline attached. Say it that way.

## The milestones and dates

| Milestone | Target | What you deliver |
|---|---|---|
| [2.1 Wiring, encoder ISR, PWM commands](#/t/sprints/s2-m1) | Nov 26 | the rig wired safely; firmware with counts, PWM commands, a watchdog, and a 100 Hz stream |
| [2.2 Automated step tests and logging](#/t/sprints/s2-m2) | Dec 1 | a Python runner that executes a test plan with safety limits |
| [2.3 Equations of motion, first-order fit, simulation](#/t/sprints/s2-m3) | Dec 5 | `motor_model.py` passing the site tests; simulation vs measurement plots |
| [2.4 PI speed controller from the model](#/t/sprints/s2-m4) | Dec 10 | a PI speed loop on the Uno; predicted vs measured response |
| [2.5 Endurance test and the one-page report](#/t/sprints/s2-m5) | Dec 13 | drift plots and the test report |

The realistic finish is Dec 13, with a stated risk of slipping to Dec 18: Sprint 2 overlaps Sprint 1's final milestone. If something has to slip, keep the 2.3 model and the 2.5 report: they're the parts a reviewer reads.

## The rules

1. **Your own firmware and Python.** The site gives register maps, timing math, equations, function signatures, and tests; never the solution.
2. **Libraries:** the DS18B20's `OneWire` and `DallasTemperature` libraries **are allowed** (the 1-Wire protocol isn't the point of this project). The **INA219** is read with your own register code over `Wire`, exactly like the MPU-6050 in Sprint 1. No encoder, motor, or PID libraries: those are the point.
3. **Safety rules below are requirements**, not suggestions. Every test script must leave the motor stopped no matter how it exits.

## Safety

You're now working with a 12 V supply that can deliver more than 2 A into a motor that can stall. That can't electrocute you, but it can burn out the driver, overheat a motor, melt a breadboard wire, catch a shirt sleeve or a hair tie in a spinning coupler, and reset your laptop's USB port.

- **Dedicated bench supply.** Use the 12 V, 2 A+ supply for the motor, never the Uno's 5V pin and never USB power. Constant supply voltage is also what makes your system identification repeatable (you'll log the INA219 bus voltage in every test so any sag is visible).
- **Fuse the 12 V line.** The 2 A blade fuse goes right at the supply's positive terminal, before anything else.
- **Power sequencing.** USB first, 12 V last. Switch 12 V off first. Never rewire with the 12 V supply on.
- **Common ground, one star point.** The supply's negative terminal is the star point: a heavy wire to the L298N GND, and a separate thin logic-ground wire to the Uno and the sensors. Motor current must never return through the Uno or the sensor wires.
- **Mechanical.** Clamp the motor bracket to the bench. Nothing loose on the shaft. Keep fingers, sleeves, and hair away from the coupler. Never stop the shaft with your hand.
- **Stall and heat.** A stalled JGA25-370 can draw more than 1 A. Your firmware and test scripts must stop the motor on overcurrent and over-temperature, and the L298N's heatsink gets hot: don't touch it during tests.
- **A software stop that always works.** The firmware stops the motor if it hasn't received a command for 500 ms (a watchdog). Your Python always sends `STOP` in a `finally:` block. Keep the 12 V supply's power switch within reach as the hardware emergency stop.
- **Supervise.** Don't leave an endurance test running unattended.

## Your project repo

Its own GitHub repo, for example `motor-test-rig`:

```
motor-test-rig/
  firmware/
    rig_openloop/rig_openloop.ino     2.1
    rig_pi/rig_pi.ino                 2.4
  host/
    rig.py               serial link, commands, parsing (2.1 and 2.2)
    step_test.py         the test runner (2.2)
    motor_model.py       + test_motor_model.py from this site (2.3)
    compare_model.py     simulation vs measurement (2.3)
    pi_design.py         gains and predicted response (2.4)
    endurance.py         2.5
  plans/                 test plans as JSON
  data/                  logs (big ones in .gitignore)
  docs/img/  docs/report.pdf
  tests/
  .github/workflows/tests.yml
  README.md
```

Reuse what you built in Sprint 1: the same logger structure, CSV conventions, pytest layout, and CI workflow. Copying your **own** Sprint 1 code is exactly what professionals do.

## Parts for Sprint 2

| Part | Notes |
|---|---|
| Arduino Uno R3 + USB cable | external interrupts are only on **D2 and D3**: the encoder uses both |
| L298N dual H-bridge module | one channel used; about a 2 V drop at 1 A |
| JGA25-370 12 V gear motor with **Hall** quadrature encoder, bracket, coupler | check the label for the encoder's pin names |
| INA219 breakout (0.1 Ω shunt, I2C 0x40) | high side, 26 V and ±3.2 A maximum |
| DS18B20 waterproof probe + 4.7 kΩ resistor | taped to the motor can with Kapton or electrical tape |
| 12 V DC supply, 2 A minimum (3 A preferred) + barrel-to-screw-terminal adapter | dedicated to the rig |
| Inline blade fuse holder + 2 A fuse | on the 12 V positive lead |
| 0.1 µF ceramic capacitor | across the motor terminals (noise) |
| 18 to 20 AWG wire for the 12 V and motor leads; jumpers for logic | breadboard jumpers are too thin for motor current |

## Resume and interview note

The honest bullet, filled in with your measured numbers only after the tests pass and you pass the defense quiz:

> Designed an automated DC motor test rig (encoder, INA219, DS18B20); identified a first-order model (τ = X ms, R² = Y) and tuned a PI speed loop that met the predicted rise time within Z%; ran an N-cycle endurance test with drift analysis and a one-page test report.
