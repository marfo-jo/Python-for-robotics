**Read this first (15 minutes).** It explains what you're building, why a hiring manager cares, how the seven milestones fit together, and the rules of the game.

## What you're building

An **IMU data pipeline**, end to end, on hardware you own:

```
MPU-6050 --I2C--> Arduino Uno --USB serial--> Python on the laptop --> CSV log --> plots, filter, Allan variance
 (sensor)        (your C firmware)            (your pyserial driver)
```

Every stage is yours:

1. **Firmware in C** on the Uno that talks to the MPU-6050 by reading and writing its **registers directly** over I2C, then streams the samples over the USB serial link.
2. **A Python host driver** (pyserial) that reads the stream, checks every packet, survives dropped and corrupted bytes, and logs to CSV.
3. **Data processing**: unit conversion, gyro bias calibration, a complementary filter for tilt angle, and an **Allan variance** noise analysis of *your* IMU.
4. **pytest tests** for the parser and the filters, run automatically on every push by **GitHub Actions**.
5. **A README** with plots, a wiring diagram, and how to run it.

This is the same pipeline you met in EECE5554 Lab 3 (IMU noise characterization). The difference is that this time you write every line yourself and you can defend every line in an interview.

## Why this project, for interviews

Your strongest lane for Spring 2027 co-ops is **embedded systems, sensors, test and validation, hardware integration, and controls**. This one project gives you a real answer to the questions those interviews actually ask:

| Interview question | Where your answer comes from |
|---|---|
| "Walk me through how you'd bring up a new I2C sensor." | 1.1 and 1.2: scan, `WHO_AM_I`, wake the chip, burst read |
| "What's two's complement? Big-endian?" | 1.2 (combining the high and low registers) and 1.4 (packing a frame) |
| "How do you design a serial protocol? What if bytes get lost?" | 1.4: sync bytes, sequence numbers, checksum, resyncing parser |
| "How would you test this parser?" | 1.4 and 1.5: normal, edge, bad-input, and fault-injection tests in CI |
| "How do you fuse a gyro and an accelerometer?" | 1.6: bias calibration and a complementary filter |
| "How do you characterize sensor noise?" | 1.7: Allan deviation, angle random walk, bias instability from your own data |

Your PLC and maintenance background is an asset here. Bringing up a sensor is commissioning; a checksum is the same idea as a fieldbus CRC; a resyncing parser is what every Modbus master does after a noisy line. Say that in interviews.

## The milestones and dates

| Milestone | Target | What you deliver |
|---|---|---|
| [1.1 Wiring, I2C scan, WHO_AM_I](#/t/sprints/s1-m1) | Nov 2 | the GY-521 wired, found at 0x68, `WHO_AM_I` read by your own register code |
| [1.2 Wake, burst-read, stream CSV at 100 Hz](#/t/sprints/s1-m2) | Nov 6 | firmware that streams raw samples as CSV text at a steady 100 Hz |
| [1.3 Python logger, unit conversion, first plot](#/t/sprints/s1-m3) | **Nov 10: MINIMAL VERSION** | `imu_convert.py` passing the site tests, a CSV log, a plot, README v0 |
| [1.4 Binary packets and a resyncing parser](#/t/sprints/s1-m4) | Nov 18 | binary frames with a checksum, `imu_packet.py` passing the site tests |
| [1.5 A real pytest suite and GitHub Actions CI](#/t/sprints/s1-m5) | Nov 24 | your own test suite, green CI badge |
| [1.6 Live plot, gyro bias, complementary filter](#/t/sprints/s1-m6) | Nov 30 | `imu_filter.py` passing the site tests, a live tilt plot |
| [1.7 Allan variance and the final README](#/t/sprints/s1-m7) | **Dec 4: FULL VERSION** | `allan.py` passing the site tests, a 1 to 3 hour static log analyzed, final README |

**About the Nov 10 date.** Nov 10 is the target for the minimal version (1.1 to 1.3). Nov 13 to 14 is an acceptable fallback, **but** Nov 13 is also the EECE7150 SfM homework deadline and an application deadline. Slipping stacks three deadlines on one day. Protect Nov 10: the minimal version deliberately uses plain CSV text, not binary packets, so it is small enough to finish.

## The rules

1. **No IMU library.** "No library" means no MPU-6050 library (no `MPU6050.h`, no Adafruit or Jeff Rowberg drivers). The Arduino **`Wire`** library is allowed: it is the I2C *bus driver*, like a UART driver. **Every MPU-6050 register read and write is your own code.** Talking to the TWI hardware registers directly (no `Wire`) is an optional stretch goal after C17 in the C track.
2. **This site never writes your solution.** Pages give you register maps, bit meanings, timing math, data formats, function signatures, and tests. Hints come in three tiers: a nudge, an approach, and pseudocode. Open them in order, and only after you've been stuck for 15 minutes.
3. **No AI-written code in this project.** Ask the tutor to explain a concept or a datasheet table, never to write the function. The point is that you can defend every line.
4. **Commit at every checkpoint.** Small commits with clear messages are part of the deliverable. A hiring manager will read your history.

## Your project repo

This is a portfolio piece, so it lives in **its own GitHub repo** (not inside the course repo). Suggested name: `imu-pipeline`. Clone it next to the course folder, for example `...\MS Robotics\imu-pipeline`. You'll grow it to this layout over the seven milestones:

```
imu-pipeline/
  firmware/
    who_am_i/who_am_i.ino        1.1   (Arduino needs folder name = sketch name)
    imu_csv/imu_csv.ino          1.2
    imu_binary/imu_binary.ino    1.4
  host/
    imu_convert.py               1.3   + test_imu_convert.py from this site
    log_serial.py, plot_log.py   1.3
    imu_packet.py                1.4   + test_imu_packet.py
    imu_filter.py, live_plot.py  1.6   + test_imu_filter.py
    allan.py                     1.7   + test_allan.py
  tests/                         1.5   your own tests
  data/                          small sample logs only (big logs go in .gitignore)
  docs/img/                      plots and the wiring diagram
  .github/workflows/ci.yml       1.5
  requirements.txt
  README.md
```

Create it on day one:

```powershell
# in PowerShell, from the folder that holds the course repo
git init imu-pipeline
cd imu-pipeline
mkdir firmware, host, data, docs
git add -A
git commit --allow-empty -m "Start IMU pipeline project"
# then create an empty repo named imu-pipeline on github.com and:
git remote add origin https://github.com/<your-user>/imu-pipeline.git
git branch -M main
git push -u origin main
```

## How the site's test files work

Milestones 1.3, 1.4, 1.6, and 1.7 each come with a pytest file in the course repo under `local/sprint1/`. Each one imports **your** module by name (for example `from imu_convert import raw_to_g`) and checks it against the spec on the milestone page. You write the module; the test file tells you whether it meets the spec.

**Option A (recommended): copy the test file next to your module.** Then it also runs in your CI later.

```powershell
conda activate robotics-course
copy "<course repo>\local\sprint1\m13\test_imu_convert.py" host\
cd host
python -m pytest test_imu_convert.py -q
```

**Option B: run it in place from the course repo**, pointing Python at your code folder:

```powershell
conda activate robotics-course
cd "<course repo>"
$env:PYTHONPATH = "C:\path\to\imu-pipeline\host"
python -m pytest local/sprint1/m13 -q
```

If `conda activate` does nothing in PowerShell, run `conda init powershell` once and open a new terminal, or use the "Anaconda PowerShell Prompt" from the Start menu.

Passing the site tests means "meets the spec". It does not mean "done": each milestone's checklist also has hardware results, plots, and a commit.

## Parts for Sprint 1

| Part | Notes |
|---|---|
| Arduino Uno R3 + USB cable | 5 V logic. I2C is on A4 (SDA) and A5 (SCL). |
| GY-521 MPU-6050 module | You have a 3-pack: keep two as spares. Onboard 3.3 V regulator, so it runs from the Uno's 5V pin. |
| 4 jumper wires (under 20 cm) + breadboard | Short I2C wires matter; see 1.1. |
| Something to hold the IMU still | Double-sided tape on a heavy book or a desk. Allan variance (1.7) needs it absolutely still for hours. |

## Background, just in time

You don't need all of Module S before you start. Read these short pages when a milestone points to them:

- [Background: pyserial in 20 minutes](#/t/sprints/bg-pyserial) (before 1.3)
- [Background: writing a CSV log](#/t/sprints/bg-csv) (before 1.3)
- [Background: plotting a CSV log with Matplotlib](#/t/sprints/bg-plot) (before 1.3)
- C track [C1 Toolchains](#/t/c/c01) and [C2 Types, stdint.h, sizes, and overflow](#/t/c/c02) (before 1.2: `int16_t` matters)

## Resume and interview note

When the full version is done, the honest bullet looks like this (you fill in your measured numbers, and only after you pass the defense quiz):

> Built an MPU-6050 IMU pipeline: register-level I2C firmware in C, a checksummed binary serial protocol, and a Python driver with N pytest tests running in GitHub Actions CI; characterized sensor noise with Allan variance (angle random walk = X °/√h).

Every word of that bullet maps to a milestone. If you can't explain a word, you haven't earned it yet.
