# Python for Robotics: Phase 1 Plan

Status: **APPROVED 2026-10-28.** This is the source of truth for the build. Changes go through the learner and are recorded here.

Decisions already made (from clarifying questions):

| Topic | Decision |
|---|---|
| Firmware board | Arduino Uno R3 (5V logic, external interrupts on D2/D3 only, I2C on A4/A5) |
| Firmware tool | Arduino IDE (already installed) |
| Desktop C | `gcc` in the Ubuntu 22.04 VM |
| Site stack | Plain HTML/CSS/JS ES modules, no build step, pinned CDN libraries |
| Local run | `python -m http.server` from the `robotics-course` conda env |
| Conda env | No changes without approval (currently Python 3.11.18, numpy 2.4.6, matplotlib 3.11.2, opencv 4.14.0, pytest 9.1.1). **pyserial 3.5 installed 2026-10-28 (approved).** |
| Hosting | This repo, **public** (portfolio), GitHub Pages under the learner's account; rename `master` to `main` when the remote is added |
| Answer key | Reference and known-wrong solutions live in a **separate private repo**, never in the public repo or the deployed site. The site ships only tests. See 7.8. |
| IMU firmware rule | Arduino `Wire` is allowed as the I2C bus driver. Every MPU-6050 register read/write is the learner's own code. No IMU libraries. |
| Raspberry Pi / VM | Pi model unknown; identify it first (see 7.10). The VM stays on Humble until winter break, then moves to a fresh Ubuntu 24.04 + Jazzy VM. |
| Co-op | Not confirmed. The roadmap has two versions: A (no co-op) and B (co-op from mid-January). See Section 4. |
| Owned parts | Breadboard and jumpers; the WALL-E chassis and battery will be reused |
| Light day | Sunday |
| Start date | Thursday 2026-10-29 |
| Parts | Nothing ordered yet, so Order 1 must go out now (see Section 6) |

---

## 1. Research findings

### 1.1 Coding patterns that recur in robotics code, interviews, and postings (ranked)

How the ranking was made: I combined (a) patterns that appear in nearly every ROS 2 / Nav2 / ros2_control / OpenCV codebase, (b) common robotics co-op and junior interview question banks, and (c) posting analysis. The only hard numbers are from a 2026 analysis of 257 robotics/mechatronics postings: Python in 50%, C++ in 44%, ROS in 14%, "robotics fundamentals" in 39% [Huntr]. Co-op postings also repeatedly list ROS/ROS 2, deploying to embedded hardware, and "test and validate in simulation and on real hardware" [Magna, AEVEX, Beko, KansasWorks]. The rest of the ranking is my judgment of relative frequency, not a measured count.

| Rank | Pattern | Why it ranks here | Where it's taught |
|---|---|---|---|
| 1 | **Fixed-rate sense, compute, act loop with dt** | Every controller, ROS timer, and firmware `loop()` uses it. Interviewers ask about wrong dt and jitter. It's a PLC scan cycle in software. | M0, M4, C14 |
| 2 | **Parsing and serializing sensor data** (text/NMEA, binary packets, checksums, endianness) | This is the core of every driver and the center of your embedded/test lane. It shows up as "parse this packet" interview questions. | M0, S, C9, C16, Sprint 1 |
| 3 | **Signal filtering and buffers** (ring buffer, moving average, low-pass, complementary) | First processing step for any sensor. "Implement a moving average in O(1)" is a classic question. | M1, S, M6 |
| 4 | **PID with saturation and anti-windup** | The most-asked controls coding question. Every motor and mechatronics role uses it. | M4, Sprint 2, IR-B2 |
| 5 | **Coordinate frames, rotations, homogeneous transforms, angle wrapping** | Used everywhere through tf2. Frame mix-ups and unwrapped angles are the most common real bugs. | M3, M7, M13 |
| 6 | **Unit testing numeric/hardware code** (tolerances, fakes, edge cases, CI) | Test/validation roles list it directly, and "how would you test this function" is a standard question. | S, M11, M18 |
| 7 | **Bit manipulation and register access (C)** | Embedded interviews almost always include set/clear/toggle bits, `volatile`, and ISR rules. | C10 to C13 |
| 8 | **Publisher/subscriber and callbacks** | The basic structure of ROS 2 and most robot software. | M12, M13 |
| 9 | **Finite state machines** | Firmware, behaviors, test sequencers, and PLC sequences all use them. | M5, C21 |
| 10 | **Vectorized NumPy array math** | All perception, estimation, and data analysis code depends on it. | S, M3, everywhere |
| 11 | **Predict/update estimation** (KF/EKF/PF) | A frequent "explain and sketch" interview question. Also needed for GPS/IMU fusion. | M6 |
| 12 | **Grid graph search** (BFS/Dijkstra/A*) | A common coding interview question in robotics form. | M1 preview, M8 |
| 13 | **Concurrency for I/O** (reader thread + queue, locks, timeouts) | Every serial or network driver needs it, and race-condition bugs are common debugging stories. | M12 |
| 14 | **Config, logging, and error handling** | Production code standards. Reviewers notice when they're missing. | M11 |
| 15 | **Image pipelines** (threshold, mask, contours, features, homography) | Perception roles and your EECE7150 work. | M10 |
| 16 | **Training loops and data splits** | ML/perception roles. Leakage is a classic interview trap. | M14 |

Non-coding topics that interviews in your lane ask about: pull-up resistors, voltage dividers, RC cutoff, op-amp gain, flyback diodes, MOSFET low-side switch, H-bridge/PWM, I2C vs SPI vs UART, ADC resolution/aliasing, step response specs, and "this robot drifts left / this sensor reads garbage, how do you debug it?" These are covered by the Interview Refreshers track and the debug scenario bank.

### 1.2 Industry trends and the curriculum changes they lead to

| Trend | Change to the curriculum |
|---|---|
| **ROS 2 Humble reaches end-of-life in May 2027**, the same month you graduate. Jazzy (Ubuntu 24.04) is the current LTS. | Every "Bridge to Real Robots" box gets a Humble vs Jazzy note. M13 ends with a lesson on moving to Jazzy. Your Pi model decides whether the Pi runs Humble or Jazzy (see 7.10). |
| **ros2_control** is the standard hardware interface in industry, and job posts mention it. | Added lesson 13.13 (ros2_control concepts and controller manager). |
| **MCAP** is the default rosbag format, with Foxglove for viewing. | Covered in 13.12 and 16.6. |
| **Test, validation, HIL/SIL, and reliability** appear in many co-op posts in your lane, and your maintenance background is real evidence for them. | **New Module 18: Test, Validation and Reliability.** It's on the interview-critical path. |
| **Signal processing** (FFT, aliasing, filters) is covered by ME5245 right now and needed for IMU work. | Lessons 6.1 to 6.3 are added at the start of M6, and FFT is previewed in Sprint 1. |
| **3D vision / SfM** is your current EECE7150 homework (due Nov 13). | Added 10.15 (epipolar geometry and triangulation), plus a 3-lesson SfM concept primer in Week 1 (Section 3.4). |
| **Gazebo Classic is end-of-life.** Gazebo (Harmonic), MuJoCo, and Isaac Lab are where simulation work happens now. | M17 uses Gazebo Harmonic, not Classic. |
| **Robot learning** (imitation learning, LeRobot, vision-language-action models) is growing fast but is a research lane, which is weak for you this season. | Stays late in M17 as an overview plus one hands-on LeRobot exercise. |
| **C++ is in about 44% of postings.** | "Bridge to C++" boxes in every module plus the C for Embedded track. A full C++ module is deferred and can be added after the core curriculum if you want it. |
| **Embedded Linux on the Pi** (systemd services, udev rules for stable serial port names) comes up in hardware integration roles. | Covered in 12.6 and the H4 WALL-E project. |

---

## 2. Curriculum

Every lesson follows the rigor rules from the spec: 3+ worked examples, an interactive visual, predict-the-output questions, a hidden-test challenge, find-the-bug, explain-it-back, and a "Where you saw this" note. Every module ends with a mastery quiz (80% to pass), a project, a Bridge to Real Robots box, and a Bridge to C++ box. Course tags: **5250** = ME5250, **MR** = Mobile Robotics, **5180** = CS5180, **5554** = EECE5554, **7150** = EECE7150, **5245** = ME5245.

Module order is **not** numeric. See the roadmap (Section 3). Numbering follows the spec so references stay stable. Two new modules are added: **S** (Sensor Data Toolkit, pulled forward) and **18** (Test, Validation and Reliability).

### Module 0: Python Foundations (recurring dataset: GPS NMEA sentences)

| # | Lesson | Objective (you can...) |
|---|---|---|
| 0.1 | Strings review: anatomy of a `$GPGGA` sentence | index, slice, `split(',')`, and `strip()` a real NMEA sentence; explain why strings are immutable |
| 0.2 | Conditionals and booleans | validate sentence type and fix quality with `if/elif/else`, `and/or/not`, and comparison chains |
| 0.3 | `while` loops | write loops that end correctly; spot and fix infinite loops; retry-until-valid patterns |
| 0.4 | `for` loops and `range` | iterate characters and compute the NMEA XOR checksum with `ord`, `^`, and `hex` (a preview of C bitwise ops) |
| 0.5 | Lists | build, index, slice, and append field lists; handle `IndexError`; avoid off-by-one errors |
| 0.6 | Functions | write `parse_gga(sentence)`; know return vs print, parameters, and local scope |
| 0.7 | Tuples and unpacking | return `(lat, lon)` pairs; unpack in loops; know when immutability helps |
| 0.8 | Dictionaries | map field names to values; dispatch on sentence type with a dict of functions |
| 0.9 | f-strings and number formatting | convert ddmm.mmmm to decimal degrees; format with fixed precision and units |
| 0.10 | Reading files | `with open(...)`, iterate lines, skip blank or garbled lines, count errors |
| 0.11 | Exceptions and reading tracebacks | read a traceback bottom-up; use `try/except ValueError`; raise your own errors |
| 0.12 | Debugging with print and the VS Code debugger | set breakpoints, step through code, watch variables; debug systematically (a PLC troubleshooting analogy) |

**Project:** NMEA log analyzer. Read a real GPS log, validate checksums, count bad sentences, compute fix-quality statistics, and write a summary file (in browser, plus a local `.py` export). **Bridge:** subscribing to `sensor_msgs/NavSatFix` in rclpy. **C++:** `std::string` and `std::stringstream` parsing of the same sentence. Every lesson in this module includes the step-through code tracer.

### Module S: Sensor Data Toolkit (pulled forward for the Sprint Projects)

pyserial can't run in Pyodide, so in-browser lessons use a `FakeSerial` class with the same API driven by a simulated device. Each of these lessons also has a local exercise that uses your real Arduino.

| # | Lesson | Objective |
|---|---|---|
| S.1 | Writing files and CSV logging | log timestamped rows with `csv`; headers, flushing, and why logs get corrupted on crash |
| S.2 | Serial communication with pyserial | open a COM port, set baud and timeout, `readline()`, decode bytes; diagnose "no data" and garbage-at-wrong-baud |
| S.3 | Bytes, bits and hex in Python | `bytes`, `int.from_bytes`, endianness, two's complement (how the MPU-6050 high/low registers combine) |
| S.4 | Binary packets with `struct` | design a frame (header, sequence number, payload, checksum); `pack`/`unpack`; text vs binary trade-offs |
| S.5 | Robust stream parsing | write a byte-by-byte state machine parser that resyncs after corruption and counts drops (sequence gaps) |
| S.6 | NumPy for sensor data I | arrays, dtypes, slicing, `mean`/`std`, loading CSV logs |
| S.7 | NumPy for sensor data II | vectorized unit conversion, `np.diff` for timing jitter, boolean masks for outliers, FFT preview |
| S.8 | Matplotlib for sensor plots | time series, subplots, labels and units, saved figures; live plotting (local) |
| S.9 | pytest basics | write normal, edge, and bad-input tests; use `pytest.raises` and `pytest.approx` |
| S.10 | pytest for parsers | fixtures, `parametrize`, recorded data as fixtures, fault-injection tests; preview of running in CI |

**Project:** serial logger toolkit. A packet parser, CSV logger, plotter, and test suite against a simulated device, then reused unchanged on real hardware. **Bridge:** a serial reader feeding a ROS 2 topic. **C++:** a `struct`-based packet with `memcpy` and a checksum.

### Module 1: Data Structures Robots Use

| # | Lesson | Objective |
|---|---|---|
| 1.1 | Big-O by measurement | time operations, read O(1)/O(n)/O(n²), and pick structures by cost |
| 1.2 | `deque` as a sensor ring buffer | use fixed-size history (`maxlen`) for an O(1) moving average |
| 1.3 | Queues (FIFO) | producer/consumer command queues; BFS preview |
| 1.4 | Stacks | undo stacks, DFS, bracket checking in config files |
| 1.5 | Heaps and `heapq` | priority task schedulers and k-smallest problems; Dijkstra preview |
| 1.6 | Sets | visited sets, deduplication, set algebra on sensor IDs |
| 1.7 | Dicts as lookup tables | calibration tables with interpolation, `defaultdict`, `Counter` for fault codes |
| 1.8 | Comprehensions | list/dict/set comprehensions, and when a loop is clearer |
| 1.9 | Sorting and `bisect` | sort with `key`, stable sort; align two sensor streams by timestamp |
| 1.10 | Interview drill set | sliding-window max/median and two-pointer on sensor data, timed |

**Project:** sensor buffer library (ring buffer, median filter, two-stream timestamp sync) with tests.

### Module 2: Object-Oriented Robots

| # | Lesson | Objective |
|---|---|---|
| 2.1 | Classes and objects | write a `Motor` class; understand `__init__`, `self`, instance vs class attributes |
| 2.2 | Methods and state | an `Encoder` that counts ticks and reports speed |
| 2.3 | Dunder methods | `__repr__`, `__eq__`, `__add__` on a `Vector2` |
| 2.4 | Composition | a `Robot` that has motors and sensors; why "has-a" usually beats "is-a" |
| 2.5 | Inheritance and abstract base classes | a `Sensor` base class with `Imu`/`RangeFinder` subclasses; when inheritance hurts |
| 2.6 | Dataclasses | `Pose`, `ImuSample`; immutability with `frozen=True` |
| 2.7 | Enums | `RobotMode` and fault codes instead of magic strings |
| 2.8 | Type hints | annotate functions and classes; read hints in library code |
| 2.9 | Properties and validation | clamp a PWM duty cycle; read-only computed values |
| 2.10 | Aliasing and mutable defaults | find and fix the shared-list bug and the mutable default argument bug |

**Project:** virtual robot driver. A class hierarchy that drives the in-browser simulator, with tests.

### Module 3: Practical Linear Algebra with NumPy

| # | Lesson | Objective |
|---|---|---|
| 3.1 | Vectors and the dot product | projection, angle between headings, "is the obstacle ahead?" |
| 3.2 | Norms, distances, unit vectors | distance-to-goal, normalizing; division-by-zero edge cases |
| 3.3 | Matrices as transformations | see a matrix as "what it does to the axes" (interactive) |
| 3.4 | Matrix multiplication and shapes | predict result shapes; order matters; `@` vs `*` |
| 3.5 | Broadcasting and vectorization | transform 10,000 lidar points without a loop; avoid shape bugs |
| 3.6 | Solving linear systems | `np.linalg.solve` vs inverse; conditioning |
| 3.7 | Least squares | accelerometer bias/scale calibration and line fitting with `lstsq` |
| 3.8 | SVD | rank, plane fitting, the best rotation between point sets (preview of Kabsch) |
| 3.9 | 2D rotations and angle wrapping | build R(θ), wrap to (-π, π], and see the bugs unwrapped angles cause |
| 3.10 | Homogeneous transforms in SE(2) | compose and invert frames (robot, sensor, world) with live sliders |
| 3.11 | 3D rotations | axis-angle, Euler angles and gimbal lock, rotation matrix properties |
| 3.12 | Quaternions in code | convert, multiply, normalize, and interpolate (slerp); see why ROS uses them |
| 3.13 | SE(3) and transform trees | chain and invert 4×4 transforms; tf-style lookups |
| 3.14 | GPS coordinates | lat/lon to UTM and local ENU; RTK vs standalone accuracy (5554) |

**Project:** frames toolkit (SE(2)/SE(3) library with tests, plus a GPS track plotted in UTM).

### Module 4: The Control Loop (ties to 5245 lectures 16 to 19)

| # | Lesson | Objective |
|---|---|---|
| 4.1 | Sense, compute, act | structure a fixed-rate loop (PLC scan cycle analogy) |
| 4.2 | dt and timing jitter | measure loop timing and handle late cycles |
| 4.3 | Numerical integration | Euler vs RK4; see instability as dt grows |
| 4.4 | DC motor model | derive the electrical and mechanical ODEs and the first-order approximation (5245 L16 to 18) |
| 4.5 | Simulating the motor | step response, torque-speed curve, comparison to the transfer function |
| 4.6 | Open loop vs closed loop, P control | steady-state error and gain trade-offs |
| 4.7 | PI and PID | implement each term and know what it fixes |
| 4.8 | Saturation and anti-windup | PWM limits; clamping vs back-calculation |
| 4.9 | Derivative kick and filtering | derivative on measurement; low-pass filtering of D |
| 4.10 | Tuning | manual, Ziegler-Nichols, and model-based PI design in the simulator |
| 4.11 | Discrete implementation details | units, rate limits, integer timing on microcontrollers |

**Project:** PID library plus a simulated motor tuning report. Hardware version: H2.

### Module 5: State Machines and Behaviors

| # | Lesson | Objective |
|---|---|---|
| 5.1 | Finite state machines | enum states plus a transition table (PLC sequencer analogy) |
| 5.2 | Events, guards and timeouts | event-driven FSMs, watchdog timeouts |
| 5.3 | Reactive obstacle avoidance | range thresholds with hysteresis |
| 5.4 | Wall following | PD on lateral distance |
| 5.5 | Behavior trees | sequence, fallback, ticks; what Nav2 uses them for |
| 5.6 | Testing state machines | table-driven transition tests |

**Project:** simulator explore-and-avoid. Hardware version: H3.

### Module 6: Probabilistic State Estimation

| # | Lesson | Objective |
|---|---|---|
| 6.1 | Sampling and aliasing | Nyquist; see aliasing happen (5245 L14 to 15) |
| 6.2 | FFT and power spectrum | find the motor vibration frequency in IMU data (5245 L12 to 13) |
| 6.3 | Moving average, low-pass and high-pass filters | the RC filter in code; cutoff vs lag |
| 6.4 | Sensor noise models | bias, white noise, random walk |
| 6.5 | Allan variance | compute overlapping AVAR; read ARW and bias instability (5554 Lab 3) |
| 6.6 | Complementary filter | fuse gyro and accelerometer for tilt |
| 6.7 | Dead reckoning | IMU plus encoders plus GPS fusion (5554 Lab 4) |
| 6.8 | Probability in code | Gaussians, sampling, histograms |
| 6.9 | Markov chains | transition matrices and stationary distributions (7150) |
| 6.10 | Discrete Bayes filter | histogram localization in a corridor (7150, Thrun ch. 2) |
| 6.11 | 1D Kalman filter | predict/update and gain intuition |
| 6.12 | Multivariate Kalman filter | constant-velocity 2D tracking, covariance ellipses |
| 6.13 | EKF | differential drive plus landmark/GPS updates; Jacobians (5554) |
| 6.14 | Particle filter | sample, weight, resample; degeneracy (5554) |

**Project:** Lab 4 rebuild (dead reckoning with sensor fusion) plus EKF localization in the simulator.

### Module 7: Kinematics (5250)

| # | Lesson | Objective |
|---|---|---|
| 7.1 | Differential drive kinematics | wheel speeds to (v, ω) and back (MR) |
| 7.2 | Encoder odometry | integrate poses; watch error grow |
| 7.3 | 2-link planar forward kinematics | geometric FK with draggable joints |
| 7.4 | DH parameters | build DH tables and avoid convention pitfalls |
| 7.5 | Screws and the matrix exponential | twists and exponential coordinates |
| 7.6 | Product of exponentials FK | space and body forms, checked against DH |
| 7.7 | Jacobians | space and body, numerical vs analytic |
| 7.8 | Singularities and manipulability | ellipsoid visual; near-singular behavior |
| 7.9 | Newton-Raphson IK | iterate, convergence, multiple solutions |
| 7.10 | 3D visualization | three.js arm viewer driven by your FK |

**Project:** ME5250 3D arm FK/IK visualizer, rebuilt from scratch. Hardware version: H5.

### Module 8: Planning

| # | Lesson | Objective |
|---|---|---|
| 8.1 | Occupancy grids | world to grid conversion, obstacle inflation |
| 8.2 | BFS | animated open and closed sets |
| 8.3 | Dijkstra | weighted grids with heapq |
| 8.4 | A* | heuristics and admissibility; tie-breaking (5554) |
| 8.5 | PRM | sampling, connecting, querying (5554) |
| 8.6 | Path smoothing | shortcutting and splines |
| 8.7 | Pure pursuit | lookahead geometry and tuning |
| 8.8 | Planning interview drills | timed grid-search questions |

**Project:** plan and follow in the simulator.

### Module 9: MPC (intro; MR)

| # | Lesson | Objective |
|---|---|---|
| 9.1 | The receding-horizon idea | predict, optimize, apply the first input, repeat (interactive) |
| 9.2 | Prediction models | discretize the unicycle model |
| 9.3 | Cost design | tracking vs effort weights |
| 9.4 | Solving with `scipy.optimize` | `minimize` with bounds for input limits |
| 9.5 | Path tracking | MPC following a reference path |
| 9.6 | MPC vs PID | performance and compute-time comparison |

**Project:** Mobile Robotics rebuild (MPC vs PID path tracking).

### Module 10: Computer Vision with OpenCV (7150)

| # | Lesson | Objective |
|---|---|---|
| 10.1 | Images as arrays | shape, dtype, channels, BGR vs RGB |
| 10.2 | Color spaces and thresholding | HSV color masks |
| 10.3 | Masks and morphology | open, close, noise cleanup |
| 10.4 | Contours and moments | find a colored target's centroid |
| 10.5 | Edges and Hough | Canny, line detection |
| 10.6 | Line following | camera view to steering command in the simulator |
| 10.7 | Pinhole camera model | intrinsics and projection |
| 10.8 | Camera calibration | checkerboard calibration; reading reprojection error (5554) |
| 10.9 | Features | ORB and SIFT detection and matching, ratio test |
| 10.10 | Homography and DLT | build the DLT and normalize; draggable-corner warp |
| 10.11 | RANSAC | robust fitting and inlier thresholds |
| 10.12 | Warping and mosaicing | stitch an image sequence |
| 10.13 | Pyramids and blending | Laplacian pyramid blending vs simple blending |
| 10.14 | Classical optical flow | Lucas-Kanade and Farneback; color-wheel visualization |
| 10.15 | Epipolar geometry and triangulation | E/F matrices, recovering pose, triangulating points (SfM) |
| 10.16 | ArUco/AprilTag pose estimation | `solvePnP` and frame conventions (5554) |

**Projects:** HW2 mosaic extension, framed as mapping (ORB/SIFT, RANSAC, pyramid blending). Hardware version: H6.

### Module 11: Software Engineering for Robots

| # | Lesson | Objective |
|---|---|---|
| 11.1 | Modules and packages | imports, `__init__`, project layout |
| 11.2 | Environments | conda/venv, pinned requirements |
| 11.3 | Logging | levels, handlers, structured logs |
| 11.4 | Exception design | custom exceptions; fail loud vs recover |
| 11.5 | Configuration | YAML and argparse; no magic numbers |
| 11.6 | Advanced pytest | mocks and fake hardware, coverage |
| 11.7 | Git workflow | branches, pull requests, good commits, reviews |
| 11.8 | GitHub Actions CI | test matrix, badges |
| 11.9 | READMEs and docs | a README that gets you interviews |

**Project:** package the Sprint 1 code as an installable package with CI.

### Module 12: Concurrency and Communication

| # | Lesson | Objective |
|---|---|---|
| 12.1 | Callbacks and event-driven code | register handlers; inversion of control |
| 12.2 | Threads, the GIL, races and locks | reproduce a race, then fix it |
| 12.3 | Reader thread plus queue | a non-blocking serial reader |
| 12.4 | asyncio basics | when to choose async over threads |
| 12.5 | Publish/subscribe | an in-browser message bus that mirrors ROS 2 |
| 12.6 | Microcontroller protocols | command/response, framing, reconnects, udev rules, and systemd on the Pi |
| 12.7 | Real-time limits | why Python isn't real-time; where the line goes between MCU and PC |

**Project:** threaded serial bridge for WALL-E (H4, part 1).

### Module 13: ROS 2 with rclpy (in-browser mock API plus VM exercises)

| # | Lesson | Objective |
|---|---|---|
| 13.1 | The ROS 2 graph and CLI | nodes, topics, `ros2` CLI tour |
| 13.2 | Nodes | rclpy node lifecycle, spinning |
| 13.3 | Topics | publishers, subscribers, QoS basics |
| 13.4 | Interfaces | custom msg/srv packages |
| 13.5 | Timers and executors | callback groups; avoiding blocked callbacks |
| 13.6 | Parameters | declare, YAML files, dynamic changes |
| 13.7 | Services | request/response, timeouts |
| 13.8 | Actions | goals, feedback, cancel |
| 13.9 | Launch files | Python launch, arguments, remapping |
| 13.10 | tf2 | broadcasters, listeners, static transforms |
| 13.11 | Sensor driver node | serial IMU to `sensor_msgs/Imu` (5554 Lab 3) |
| 13.12 | Bags and RViz2 | MCAP recording/playback, RViz2 displays |
| 13.13 | ros2_control and Jazzy | controller manager concepts; moving from Humble to Jazzy |

**Project:** WALL-E ROS 2 driver rewrite (H4: Arduino serial bridge, Pi node, teleop).

### Module 14: PyTorch and Deep Learning for Perception (local, RTX 4080)

| # | Lesson | Objective |
|---|---|---|
| 14.1 | Tensors and shapes | create, reshape, broadcast; GPU device moves |
| 14.2 | Autograd | gradients by hand vs `backward()` |
| 14.3 | Datasets and DataLoaders | custom datasets, batching |
| 14.4 | `nn.Module` | building models |
| 14.5 | Losses and optimizers | MSE/CE, SGD/Adam |
| 14.6 | The training loop | train/eval modes, checkpoints |
| 14.7 | Splits and leakage | train/val/test done right |
| 14.8 | Overfitting and learning rate schedules | regularization, early stopping, schedulers |
| 14.9 | CNNs for perception | convolution intuition, a small classifier |
| 14.10 | Attention basics | dot-product attention, implemented from scratch |
| 14.11 | Deep optical flow | HW3 rebuild with a proper split, compared to Farneback |

### Module 15: Reinforcement Learning (5180)

| # | Lesson | Objective |
|---|---|---|
| 15.1 | MDPs | states, actions, rewards, returns |
| 15.2 | Dynamic programming | value iteration on a gridworld |
| 15.3 | Monte Carlo and TD(0) | bootstrapping intuition |
| 15.4 | Q-learning | Four Rooms with a live Q-value visual |
| 15.5 | Exploration | ε-greedy schedules |
| 15.6 | Function approximation | linear features |
| 15.7 | DQN | CartPole with replay and a target network (local) |
| 15.8 | Double DQN | fixing overestimation bias |
| 15.9 | Policy gradients and PPO | REINFORCE, then the idea behind PPO |

### Module 16: Full-Stack Tooling

| # | Lesson | Objective |
|---|---|---|
| 16.1 | Docker basics | images, containers, volumes |
| 16.2 | Docker for ROS 2 | dev containers, networking |
| 16.3 | CI for ROS 2 | colcon build and test in Actions |
| 16.4 | FastAPI telemetry server | REST endpoints |
| 16.5 | WebSocket dashboard | live robot telemetry in the browser |
| 16.6 | Foxglove | MCAP viewing and layouts |
| 16.7 | micro-ROS | ESP32 publishing to ROS 2 |

### Module 17: Robot Learning and Simulation (advanced)

| # | Lesson | Objective |
|---|---|---|
| 17.1 | Gazebo Harmonic plus ROS 2 | spawn and drive a robot |
| 17.2 | MuJoCo | Python bindings, contacts |
| 17.3 | Nav2 concepts | costmaps, behavior trees, planners/controllers |
| 17.4 | MoveIt 2 concepts | planning scene, planning pipeline |
| 17.5 | Imitation learning with LeRobot | behavior cloning on a sim dataset |
| 17.6 | Isaac Sim / Isaac Lab | overview on the RTX 4080 |
| 17.7 | Foundation models for robots | an overview of the vision-language-action trend |

### Module 18: Test, Validation and Reliability (new; leverages your maintenance experience)

| # | Lesson | Objective |
|---|---|---|
| 18.1 | Requirements and test plans | testable requirements, traceability |
| 18.2 | Measurement statistics | mean, std, confidence intervals, repeatability |
| 18.3 | SIL and HIL testing | fakes, simulators, hardware-in-the-loop rigs |
| 18.4 | Automated test sequencing | scripted step tests, fixtures, safe states |
| 18.5 | Pass/fail criteria | tolerances, limits, data-driven verdicts |
| 18.6 | Reliability engineering | MTBF, Weibull basics, endurance and drift (preventive maintenance link) |
| 18.7 | Root-cause analysis for robots | 5 Whys, fishbone, fault trees, debug scenario practice |
| 18.8 | Test reports | one-page reports that hiring managers read |

**Project:** polished H2 endurance test report as a work sample.

### Capstone

A simulated robot that localizes with an EKF, plans with A*, follows the path with pure pursuit, PID, or MPC, detects a colored target with OpenCV, and logs data. It's packaged as a ROS 2 package in a Dockerized repo with tests, CI, and GIFs in the README. Hardware version: H7.

---

## 3. Parallel tracks

### 3.1 C for Embedded (30 min/day inside the course block)

Run commands: desktop C uses `gcc -Wall -Wextra -std=c11 file.c -o file && ./file` in the VM. Firmware is built and uploaded with the Arduino IDE on Windows.

| Week | Lessons |
|---|---|
| W0 | C1 toolchains (gcc in the VM, Arduino IDE) and hello world · C2 types, `stdint.h`, sizes, overflow |
| W1 | C3 operators, integer division, casts · C4 control flow · C5 functions and headers · C6 arrays and char strings · C7 pointers I |
| W2 | C8 pointers and arrays, pointer arithmetic · C9 structs and packed structs (packets) · C10 bitwise ops · C11 AVR registers (blink via DDRB/PORTB) · C12 `volatile` and memory-mapped I/O |
| W3 | C13 interrupts and ISR rules (encoders) · C14 `millis()` non-blocking loops and timers · C15 timer PWM · C16 UART framing, binary `Serial.write`, checksums · C17 I2C protocol (start/stop/ACK; Wire register read/write) |
| W4 | C18 SPI · C19 ring buffers in C · C20 fixed-point math · C21 debouncing and state machines · C22 embedded debugging |
| W5 | C23 `const`, `static`, scope, memory layout · C24 embedded interview drill set |

After W5, the 30-minute slot becomes weekly C drills plus C++ reading from the Bridge boxes.

### 3.2 Interview Refreshers (inside the 1-hour applications/interview block)

Format: a short concept page, then a quiz of 10 to 15 items, then 3 interview questions with answer-feedback rubrics.

- **Circuits and analog** (W0 to W3, doubling as review for ME5245 Midterm 2 on Nov 19, which covers transistors through DC motors). Topics: A1 dividers and pull-ups · A2 RC filters and anti-aliasing · A3 op-amp configurations · A4 diodes and flyback · A5 BJT as a switch · A6 MOSFET low-side switch and logic-level gates · A7 H-bridge and PWM · A8 buck/boost · A9 signal conditioning chains · A10 reading datasheets (MPU-6050 and INA219 as cases).
- **Classical controls** (W3 to W6). Topics: B1 1st/2nd-order step specs · B2 PID tuning · B3 poles and stability · B4 Bode plots and margins · B5 state-space basics · B6 discretization and sample rate.
- **Behavioral** (W0 to W2, since you're applying now). Six STAR stories: (1) diagnosing a failure, (2) building a troubleshooting checklist, (3) reducing downtime, (4) a QA/compliance catch, (5) WALL-E integration problem-solving, (6) a team conflict or deadline from the ME5245 project. Also "tell me about yourself", "why robotics", and the "defend your resume" drill.
- **Debug scenario bank** (runs all season). Examples: "the robot drifts left", "I2C reads 0xFF", "the motor stutters at low PWM", "readings spike when the motor starts" (ground bounce / back-EMF), "the encoder count jumps". Each scenario draws on your PLC and maintenance diagnostic process.

### 3.3 Sprint Projects

The site provides milestone checklists, background lessons, wiring diagrams, tiered hints, and test files. It never provides solution code.

**Confirmed rule:** "no IMU library" means no MPU-6050 library. The Arduino `Wire` (I2C bus driver) is allowed, and all MPU-6050 register reads and writes are your own code. Bare-metal TWI register access is an optional stretch goal after C17.

**Nov 10 target and fallback:** Nov 10 is the target. Nov 13 to 14 is an acceptable fallback, but **Nov 13 is also the EECE7150 SfM due date and the Interactive Mobility application deadline**. Slipping to the fallback stacks three deadlines into one day, so the Sprint hour in W2 protects the Nov 10 date first.

**Sprint 1: IMU data pipeline**

| Milestone | Target date | Content |
|---|---|---|
| 1.1 | Oct 30 to Nov 2 | Wiring (5V to VCC, GND, A4 SDA, A5 SCL); I2C scan; read `WHO_AM_I` (0x75 should return 0x68) |
| 1.2 | Nov 3 to 6 | Wake the chip (`PWR_MGMT_1` 0x6B); burst-read 14 bytes from 0x3B; combine int16 values; stream CSV text at 100 Hz on a `millis()` schedule |
| 1.3 | Nov 6 to 10 | Python pyserial reader, CSV log, unit conversion (16384 LSB/g, 131 LSB/(°/s)), Matplotlib plot, README v0. **This is the minimal version.** |
| 1.4 | Nov 11 to 18 | Binary packets (header, sequence number, payload, checksum); resyncing parser; drop/corrupt counters |
| 1.5 | Nov 18 to 24 | pytest suite (normal, edge, bad input, fault injection); GitHub Actions CI |
| 1.6 | Nov 24 to 30 | Live plot, gyro bias calibration, complementary filter, tests |
| 1.7 | Nov 30 to Dec 4 | Allan variance on a 1 to 3 hour static log; final README with plots and wiring diagram. **This is the full version.** |

**Sprint 2: DC motor test rig** (starts about Nov 23)

| Milestone | Content |
|---|---|
| 2.1 | Wiring: L298N, 12V supply, encoder A/B on D2/D3, INA219 on the motor supply line, DS18B20 on D4 with a 4.7k pull-up. Firmware counts encoder ticks in an ISR and accepts PWM commands. |
| 2.2 | Automated Python step-test runner logs speed, current, and temperature |
| 2.3 | Derive the equations of motion, fit a first-order model with least squares, simulate it, and compare against measured data |
| 2.4 | Design a PI/PID speed controller from the model (running on the Arduino in C); compare predicted vs measured response |
| 2.5 | Endurance test (repeated load cycles), drift plots, one-page test report |

Target date: Dec 13, with a stated risk that it slips to Dec 18 (see Risks).

**Keeping the Sprint work separate from graded coursework:** Sprint 2 is speed control on your own rig, in your own repo. Your ME5245 Project 2 (team, position control) never appears on the site. The tutor's system prompt tells it to decline helping with graded coursework and to point you to general lessons instead. The same rule applies to the SfM homework. Check the ME5245 collaboration policy before publishing anything that overlaps the course project.

### 3.4 Coursework support: SfM concept primer (W1, for the EECE7150 homework due Nov 13)

Three 45-minute concept lessons with interactive visuals and no homework code:

- CS.1 Pinhole projection
- CS.2 Epipolar geometry and the essential matrix
- CS.3 Triangulation and reprojection error

The full coded version is lesson 10.15 later. These take time from M0 on three days in W1.

---

## 4. Roadmap

There are two versions:

- **Version A** assumes no co-op, so the current budget continues.
- **Version B** assumes a co-op starts in mid-January (taken as Mon Jan 18, 2027).

Both versions are **identical through Sun Jan 17** (W0 to W11). Which version applies is decided only when an offer arrives. Nothing before then changes.

### 4A. Version A: no co-op (current budget throughout)

Weeks run Monday to Sunday. Week 0 is Thu Oct 29 to Sun Nov 1. Sunday is the light day: review queue, a Boss Fight (from W2), and a STAR story pass. The tired-day option is 30 minutes: review queue plus one 10-minute drill.

Time split through Dec 13 (application season):

- 2 h course (1.5 h Python, 0.5 h C)
- 1 h Sprint Projects
- 1 h applications and interview prep

From Dec 14: 3 h course (2.5 h Python, 0.5 h C/C++ reading) and 1 h projects.

| Week | Dates | Python course | Sprint / project hour | Interview hour | Course tie-ins |
|---|---|---|---|---|---|
| W0 | Oct 29 to Nov 1 | 0.1 to 0.3 | Order parts; Arduino serial "hello"; milestone 1.1 | STAR 1 and 2; resume audit; A1 | 5245 ADC/aliasing |
| W1 | Nov 2 to 8 | 0.4 to 0.8, CS.1 to CS.3 | 1.2; background S.2 (pyserial) | STAR 3 and 4; A5, A6 | 7150 SfM homework; 5245 DC motors |
| W2 | Nov 9 to 15 | 0.9 to 0.12, M0 quiz and project | **1.3, minimal Sprint 1 due Nov 10**; background S.1, S.8 | STAR 5 and 6; A7, A4 | SfM due Nov 13; 5245 PWM/H-bridge |
| W3 | Nov 16 to 22 | S.1 to S.5 | 1.4 | Midterm review (A5 to A7, DC motor); A2 | **5245 Midterm 2 Nov 19** |
| W4 | Nov 23 to 29 | S.6 to S.10, S project | 1.5, 1.6; Sprint 2: 2.1 | B1, B2; A3 | Thanksgiving week |
| W5 | Nov 30 to Dec 6 | M1 1.1 to 1.6 | **1.7, full Sprint 1 due ~Dec 4**; 2.2, 2.3 | B3, B4; mock interview | 5245 brushless motors |
| W6 | Dec 7 to 13 | M1 1.7 to 1.10, M1 quiz and project | 2.4, 2.5, **Sprint 2 due ~Dec 13** | B5, B6; A8 to A10; mock interview | 5245 sensors, project wrap |
| W7 to W8 | Dec 14 to 27 | M2 | Sprint polish, READMEs, resume bullets | (now course time) | |
| W9 to W10 | Dec 28 to Jan 10 | M3 | Order 2 parts arrive; **VM migration to Ubuntu 24.04 + Jazzy** (below) | | |

**Winter break task: migrate the VM to Ubuntu 24.04 + ROS 2 Jazzy** (Dec 21 to Jan 10, in the project hour; about 4 to 6 hours total). This applies to both roadmap versions. Humble reaches end-of-life in May 2027.

1. Build a **fresh** Ubuntu 24.04 VM rather than upgrading in place.
2. Keep the Humble VM untouched until the new one passes every check in step 4.
3. Install `ros-jazzy-desktop`, `colcon`, `rosdep`, `build-essential`/`gcc`, and Git. Set the network adapter to Bridged.
4. Check the new VM: the talker/listener demo works, Sprint C exercises compile with `gcc`, the RViz2 launch works, and an Arduino connected over USB passthrough appears as `/dev/ttyACM0`.
5. Then archive the Humble VM.

After the migration:

- M13 (March) and every later Bridge to Real Robots box teach **Jazzy first, with Humble notes**.
- The Pi runs Ubuntu 24.04 + Jazzy whatever its model (see 7.10), so the cross-distro problem goes away.
| W11 to W12 | Jan 11 to 24 | M4 | H2 tie-in (PID review on the rig) | | |
| W13 | Jan 25 to 31 | M5 | H3 ultrasonic FSM | | |
| W14 to W16 | Feb 1 to 21 | M6 | Lab 3/Lab 4 rebuild | | |
| W17 to W19 | Feb 22 to Mar 14 | M18, then M11 | H2 report polish; package Sprint 1 | | |
| W20 | Mar 15 to 21 | M12 | H4 part 1 | | |
| W21 to W23 | Mar 22 to Apr 11 | M13 | H4 WALL-E ROS 2 driver | | |

The **interview-critical path is complete about Apr 11, 2027**, in time for full-time spring recruiting.

| Week | Dates | Python course | Project |
|---|---|---|---|
| W24 to W25 | Apr 12 to 25 | M7 | H5 odometry; ME5250 arm visualizer |
| W26 to W28 | Apr 26 to May 16 | M8, M9 | MR MPC rebuild |
| W29 to W31 | May 17 to Jun 6 | M10 | HW2 mapping mosaic; H6 line follower |
| W32 | Jun 7 to 13 | M16 | |
| W33 to W35 | Jun 14 to Jul 4 | M14 | HW3 optical flow rebuild |
| W36 to W37 | Jul 5 to 18 | M15 | Four Rooms, DQN |
| W38 | Jul 19 to 25 | M17 | |
| W39 to W41 | Jul 26 to Aug 15 | Capstone (simulated, then H7 hardware) | |
| W42 to W43 | Aug 16 to 29 | Buffer | |

**Estimate:** about 41 weeks of core curriculum, plus 2 buffer weeks (about 43 weeks total). The "core interview curriculum" (M0, S, M1 to M6, M11 to M13, M18) is 23 weeks.

Assumptions behind the estimate:

- Lessons take 1.25 to 2 hours each, including the challenge.
- Each module wrap-up (quiz, project, bridges) takes 5 to 10 hours.
- The stated time budget holds for the whole plan.

### 4B. Version B: co-op starts mid-January

**Budget from Jan 18:**

| Day | Hours | Split |
|---|---|---|
| Weekdays | 1.5 h | 1.25 h Python lessons, 15 min review queue |
| Saturday | 3 h | 2 h course (including the week's C/C++ drill), 1 h project |
| Sunday (light day) | 3 h | 1 h Boss Fight + review queue + 1 STAR/interview drill, 2 h project |

That's about 10.5 h of course and 3 h of project per week, compared with about 15 h and 6 h in Version A. So course modules take about **1.4×** as long, and hardware projects take about **2×** as long. The tired-day option is unchanged: 30 minutes of review queue plus one drill.

W0 to W11 (Oct 29 to Jan 17) are the same as Version A.

| Dates (approx.) | Python course | Project (weekends) |
|---|---|---|
| Jan 18 to Feb 1 | M4 (finish) | H2 PID review on the rig |
| Feb 1 to Feb 10 | M5 | H3 ultrasonic FSM (runs to ~Feb 21) |
| Feb 10 to Mar 14 | M6 | Lab 3/Lab 4 rebuild |
| Mar 15 to Apr 11 | M18, M11 | H2 report polish; package Sprint 1 |
| Apr 12 to Apr 21 | M12 | H4 part 1 |
| Apr 21 to May 23 | M13 | H4 WALL-E ROS 2 driver (runs to ~Jun 6) |

The **interview-critical path is complete about May 23, 2027**. That's about 6 weeks later than Version A, and it lands right at graduation.

| Dates (approx.) | Python course | Project (weekends) |
|---|---|---|
| May 24 to Jun 11 | M7 | ME5250 arm visualizer (H5 odometry is folded into the capstone to save time) |
| Jun 12 to Jul 9 | M8, M9 | MR MPC rebuild |
| Jul 10 to Aug 6 | M10 | HW2 mapping mosaic; H6 line follower |
| Aug 7 to Aug 16 | M16 | |
| Aug 17 to Sep 13 | M14 | HW3 optical flow rebuild |
| Sep 14 to Oct 2 | M15 | Four Rooms, DQN |
| Oct 3 to Oct 12 | M17 | |
| Oct 13 to Nov 21 | Capstone (simulated, then H7 hardware) | |
| Nov 22 to Dec 5 | Buffer | |

**Estimate:** about 57 weeks in total (about 55 plus 2 buffer weeks), finishing around **early December 2027**.

**If the co-op ends early** (for example, a 4-month co-op ending in mid-May): switch back to Version A pacing for the remaining modules. That moves the finish to roughly September 2027.

**During a co-op:**

- The interview hour disappears.
- Sunday keeps one STAR or interview drill so full-time recruiting skills stay warm.
- Mock interviews resume about 6 weeks before the co-op ends.

---

## 5. Project list

| # | Project | Module | Type | Becomes |
|---|---|---|---|---|
| P0 | NMEA log analyzer | M0 | Standalone tool | GPS data portfolio repo |
| PS | Serial logger toolkit | S | Simulated device, then hardware | Basis of Sprint 1 |
| SP1 | IMU data pipeline | Sprint | Hardware (H1) | Resume headline project |
| SP2 | DC motor test rig | Sprint | Hardware (H2) | Resume headline project, test report |
| P1 | Sensor buffer library | M1 | Standalone, tested | |
| P2 | Virtual robot driver | M2 | Simulator | |
| P3 | Frames toolkit + GPS to UTM | M3 | Standalone, tested | |
| P4 | PID library + tuning report | M4 | Simulator + H2 | |
| P5 | Explore-and-avoid FSM | M5 | Simulator + H3 | |
| P6 | Lab 3/Lab 4 rebuild, EKF localization | M6 | Local + simulator | 5554 portfolio |
| P7 | 3D arm FK/IK visualizer | M7 | Browser (three.js) | 5250 portfolio |
| P8 | Plan and follow | M8 | Simulator | |
| P9 | MPC vs PID path tracking | M9 | Simulator/local | MR portfolio |
| P10 | Mapping mosaic + line follower | M10 | Local + H6 | 7150 portfolio |
| P11 | Packaged Sprint 1 with CI | M11 | Local | |
| P12, P13 | WALL-E ROS 2 driver rewrite | M12, M13 | Hardware (H4) | Resume track project |
| P14 | Optical flow: deep vs classical | M14 | Local GPU | 7150 portfolio |
| P15 | Four Rooms Q-learning + DQN CartPole | M15 | Browser + local | 5180 portfolio |
| P16 | Telemetry dashboard + micro-ROS | M16 | Local + ESP32 | |
| P17 | LeRobot imitation exercise | M17 | Local GPU | |
| P18 | Endurance test report | M18 | Hardware (H2) | Work sample |
| CAP | Capstone | All | Sim + Docker + H7 | Portfolio centerpiece |

Every project exports a `.py` file plus a README template. Each passing project generates a suggested resume bullet and a 5-question "defend this bullet" quiz.

### Hardware projects (each has a simulator version for days without hardware)

| # | Project | Parts used |
|---|---|---|
| H1 | IMU orientation + Allan variance (Sprint 1) | Uno, MPU-6050 |
| H2 | Motor test rig + PID speed control (Sprint 2) | Uno, L298N, encoder motor, INA219, DS18B20, 12V supply |
| H3 | Ultrasonic obstacle stop with an FSM | Uno, HC-SR04, L298N, motors |
| H4 | WALL-E ROS 2 driver rewrite (serial bridge, Pi node, teleop) | Uno, Pi, L298N, servo controller, servos |
| H5 | Encoder odometry on 2WD vs ground truth (taped grid + ArUco from the webcam) | Chassis, encoder motors, webcam |
| H6 | Webcam color tracker + line follower | Webcam, IR line array, chassis, Pi or laptop |
| H7 | Budget mobile robot capstone | All of the above, plus ESP32 (optional micro-ROS) and a battery pack |

Optional: a KiCad breakout board for MPU-6050 + INA219 from a low-cost PCB service (usually about $2 to $5 for boards plus $10 to $20 shipping). Do this only if the buffer allows.

---

## 6. Hardware shopping list

Prices are approximate US prices for generic modules, checked against current listings where my search found them. They change often, so check the cart total. Target is $170 or less of new spending, leaving $30 of buffer.

### Order 1: place now (Prime / fast shipping), needed for the Sprint Projects

| Item | Qty | Approx. | Notes |
|---|---|---|---|
| GY-521 MPU-6050 module | 3-pack | $11 to 15 | Spares, because you will eventually kill one. Has an onboard 3.3V regulator, so it's fine on the Uno's 5V pin. Single units are about $7 [Amazon/MakerFocus]. |
| INA219 breakout (generic, ±3.2A, 26V) | 2-pack | $10 to 12 | Adafruit is about $10 to 18 each if you want the higher-quality board [Pi Hut, reach.dog]. |
| DS18B20 waterproof probe + 4.7k resistors | 5-pack | $11 to 14 | [Fruugo] |
| JGA25-370 12V gear motor with **Hall** encoder, about 200 to 300 rpm, with brackets and couplers | 2 | $30 to 36 | Encoder versions run about $15 to 30 each. Confirm the listing says "Hall encoder" [electric-b2c, Funduino, Abra]. |
| **12V DC power supply, 2A or more** (3A preferred) + 5.5×2.1 mm barrel-jack-to-screw-terminal adapter | 1 | $9 to 13 | **Dedicated to the motor test rig**, so system ID and endurance tests run at a constant voltage instead of a draining battery. Log the supply voltage (INA219 bus voltage) in every test so any sag is visible. Stall current on a JGA25-370 can exceed 1A, so 2A is the minimum and 3A gives headroom. |
| Inline blade fuse holder + 2A fuses | 1 | $6 | Motor supply protection (safety) |
Breadboard and jumpers: already owned.

Subtotal is about **$77 to $96**.

### Order 2: by about Jan 10, before H3

| Item | Qty | Approx. | Notes |
|---|---|---|---|
| HC-SR04 ultrasonic | 5-pack | $9 | Echo pin is 5V, which is fine on the Uno. Needs a divider on the Pi or ESP32. |
| 5-channel TCRT5000 IR line sensor array | 1 | $7 | |
| 65 mm wheels for a 4 mm D-shaft | 2 | $8 | Skip if the motors come with wheels or the WALL-E wheels fit |
| USB webcam (720p/1080p) | 1 | $18 | |
| ESP32 dev board | 1 | $9 | For micro-ROS (M16) |
| LM2596 buck converter | 3-pack | $8 | Steps the WALL-E battery down to 5V for logic |

The chassis and battery are reused from WALL-E.

Subtotal is about **$59**.

**Total: about $136 to $155**, under the $170 target with about $20 to $35 to spare. That spare plus the $30 buffer can cover the optional KiCad board.

**WALL-E reuse checks** (part of the H5/H7 setup):

- Check the battery voltage.
  - On a 2S pack (7.4V), the 12V encoder motors run at about 50 to 60% of rated speed. That's fine for a small mobile robot, but the motor model (Sprint 2) must be re-identified at that voltage.
  - On 3S (11.1V), they run close to rated speed.
- Check that the chassis has room and mounting holes for the 25 mm motor brackets. If not, use a drilled plate or a 3D-printed adapter.

**Future upgrade, outside the budget:** a LeRobot-compatible SO-101 arm.

**Wiring and safety notes**, carried into each project page:

- The L298N drops about 2V, so a 12V motor sees about 10V. Remove the L298N's 5V-regulator jumper above 12V.
- Always share ground between the Uno, the L298N, and the sensors.
- The INA219 goes **high-side on the motor supply**. Its limit is 26V and ±3.2A.
- Add a flyback path. The L298N has internal diodes on many boards; check yours.
- Never power motors from the Uno's 5V pin.
- 18650 cells: protected cells only, a proper charger, and never leave them charging unattended.
- The GY-521's I2C pull-ups go to 3.3V. A 5V Uno reads that as HIGH, but it's near the threshold. Keep I2C wires short, under 20 cm.

---

## 7. Project architecture

### 7.1 Repository layout

```
/
├── index.html                  # app entry; no build step
├── app/                        # application code (ES modules)
│   ├── main.js  router.js      # hash router: #/m00/l03, #/sprint/1, #/interview ...
│   ├── ui/                     # sidebar map, lesson view, quiz, radar chart, theme toggle
│   ├── editor/                 # CodeMirror 6 wrapper (Python + C highlighting, line numbers)
│   ├── runner/                 # pyodide-worker.js, run/submit protocol, timeouts, error explainer
│   ├── harness/                # in-browser pytest plugin → JSON results
│   ├── sim/                    # 2D diff-drive simulator (physics, sensors, render)
│   ├── viz/                    # reusable interactive components (tracer, plot, frame, slider-panel...)
│   ├── progress/               # localStorage store, schema migrations, export/import, streak, SRS
│   └── tutor/                  # optional Anthropic client, prompts, attempt gating
├── content/                    # ALL lesson content (data, not code)
│   ├── curriculum.json         # modules, tracks, order, unlock rules, skills
│   ├── modules/m00-python-foundations/
│   │   ├── module.json         # quiz pool, project, bridges, resume bullet template
│   │   └── l04-for-loops/      # one folder per lesson (format below)
│   ├── tracks/{c-embedded,interview,coursework}/
│   ├── sprints/{sprint1-imu,sprint2-motor}/   # milestones, hints, wiring SVGs, test files
│   ├── drills/  bossfights/  interview/  debug-scenarios/
│   └── data/                   # NMEA logs, IMU recordings, images
├── local/                      # starter files + pytest files for local-only exercises
├── vendor/VERSIONS.md          # every pinned library version and URL
├── verification/               # GITIGNORED: local clone of the PRIVATE answer-key repo (see 7.8)
├── tools/verify.py             # local verification of every lesson (conda env)
├── tools/new_lesson.py         # scaffolds a lesson folder from a template
├── my-solutions/               # LEARNER ONLY: never written by the build
├── docs/  PLAN.md  PROGRESS.md
├── config.local.example.json   # template; config.local.json is gitignored
└── .github/workflows/pages.yml # deploys only index.html, app/, content/, local/, vendor/
```

### 7.2 Lesson data format

Each lesson is a folder. **`lesson.json`** holds structure, **`lesson.md`** holds prose, and the code lives in real `.py` files so the same tests run in the browser and locally.

```
l04-for-loops/
  lesson.json      # metadata + all interactive items
  lesson.md        # explanation; embeds items with {{example:ex1}}, {{viz:v1}}, {{predict:p1}}
  examples/ex1.py ex2.py ex3.py      # worked examples (verify.py runs each, checks expected output)
  challenge/starter.py               # what the editor opens with
  challenge/test_challenge.py        # hidden tests: real pytest, imports `solution`
  bug/buggy.py  bug/test_bug.py      # find-the-bug exercise
```

```json
{
  "id": "m00.l04",
  "title": "for loops and range",
  "minutes": 75,
  "skills": {"python": 3},
  "objectives": ["Iterate over characters and ranges", "Compute an NMEA XOR checksum"],
  "whereYouSawThis": {"course": "EECE5554", "topic": "GPS driver: NMEA checksum validation"},
  "examples": [{"id": "ex1", "file": "examples/ex1.py", "expectedOutput": "..."}],
  "predict": [{"id": "p1", "code": "for i in range(2, 8, 2):\n    print(i)", "choices": ["2 4 6", "2 4 6 8", "..."], "answer": 0, "why": "range stops BEFORE 8..."}],
  "visualizations": [{"id": "v1", "component": "tracer", "props": {"code": "..."}, "notice": "...", "predictFirst": "..."}],
  "challenge": {"starter": "challenge/starter.py", "tests": "challenge/test_challenge.py", "timeLimitMs": 5000},
  "bug": {"file": "bug/buggy.py", "tests": "bug/test_bug.py", "bugType": "off-by-one"},
  "explainBack": {"prompt": "Why does the checksum skip the '$'?", "rubric": ["mentions the start and end delimiters", "..."]},
  "hints": {"challenge": ["nudge...", "approach...", "pseudocode..."]},
  "reviewItems": ["p1", "q-loop-range-end"],
  "noHands": false,
  "runtime": "pyodide"
}
```

Local-only lessons (PyTorch, rclpy, pyserial on real hardware) set `"runtime": "local"`. They point to `local/<lesson>/` with starter files, exact commands (`conda activate robotics-course`, `pytest local/m14/l06/test_train.py`), and the VM variant for ROS 2.

**Adding content:**

1. Run `python tools/new_lesson.py m03 l15-my-topic` to scaffold the folder.
2. Fill in the files.
3. Add the lesson id to `module.json`.
4. Run `python tools/verify.py m03.l15`.

No app code changes are needed.

### 7.3 Runtime

- **Pyodide 314.0.7**, pinned, running in a Web Worker. Bundled versions: numpy 2.4.6, matplotlib 3.10.8, opencv-python 4.11.0.86, scipy 1.18.0, pytest 9.0.2, pyyaml 6.0.3 [Pyodide package list]. Packages load lazily per lesson. If a package fails to load, the lesson shows a clear message plus local-run instructions.
  - **Infinite loops:** the worker is terminated on timeout and restarted.
  - **Matplotlib:** figures render to PNG and show inline.
- **Submit** writes the editor contents to `solution.py`, then runs the lesson's hidden pytest file through a small plugin that returns per-test pass/fail, messages, and hidden edge-case labels.
- **Error explainer:** parses the traceback, highlights the failing line, and maps 25+ exception patterns (IndexError, off-by-one, TypeError on `str + int`, KeyError, indentation errors, and others) to plain-English explanations with "how to read this traceback" coaching.
- **Version skew:** Pyodide runs Python 3.14, while the local env runs Python 3.11 and newer matplotlib/opencv. Lessons avoid version-specific APIs. `verify.py` runs locally (required by CLAUDE.md), and every lesson also gets a browser smoke test.
- **Other pinned libraries** (exact versions chosen and recorded in `vendor/VERSIONS.md` in Phase 2, loaded from jsDelivr/cdnjs as ESM): CodeMirror 6, marked + DOMPurify (Markdown), KaTeX (math), Plotly (charts), three.js (3D arm). The radar chart and most visuals are hand-written SVG/canvas.

### 7.4 Simulator

The simulator is a JS canvas engine. Robot and world state live in the worker next to Pyodide, so there's no per-tick message round trip. Each tick it sends the main thread only what's needed to draw the frame.

Learner API (Python):

```python
def control(sensors, dt):        # called at a fixed rate (e.g. 50 Hz)
    # sensors.range[0..n], sensors.imu.gyro_z, sensors.imu.accel, sensors.encoders.left/right,
    # sensors.gps (low rate, noisy), sensors.camera (small grayscale array for line following)
    return left_wheel_speed, right_wheel_speed
```

- Noise models are seeded, so a bug reproduces the same way every time.
- Worlds (walls, obstacles, lines, colored targets) are JSON in `content/`.
- Tests can run the simulator headlessly in the worker and assert on outcomes, for example "reached the goal without collision within 60 s".
- Display conventions: x is red, y is green, z is blue. **Ground truth is always solid gray-black, and estimates are always orange (dashed)**. Both have light and dark theme variants.

### 7.5 Progress, mastery and spaced repetition

- `localStorage` key `pfr.progress.v1`. Every access is wrapped in try/catch, and the app works in memory when storage is unavailable.
- JSON export/import lives on the dashboard. A schema version field supports migrations.
- Lesson states: locked, unlocked, mastered. A lesson is mastered when its challenge passes, the bug is fixed, explain-back is done, and predict questions are attempted.
- Module unlock: the previous module's mastery quiz at 80% or higher. Retakes draw a reshuffled sample from a pool about 2× the quiz size.
- **Spaced repetition:** Leitner boxes (1, 3, 7, 14, 30 days). Missed predict/quiz items, Boss Fight weak spots, and failed drills enter the queue automatically.
- **Streak:** any completed review session or lesson counts. The 30-minute tired-day option keeps the streak alive.
- **Skills radar:** SVG over 9 axes (Python, math, controls, estimation, planning, perception, learning, ROS 2, software engineering), driven by each lesson's `skills` weights.
- **Resume-ready skills:** a skill is listed only after both its module's mastery quiz and its No Hands checkpoint pass.
- **Attempt log:** feeds the tutor's 3-attempt rule and the Boss Fight weak-spot report.

### 7.6 Site-wide features

- **Code Reading Drills:** snippets modeled on ROS 2/Nav2/OpenCV/PyTorch code, with an annotation box per region, predict questions, and spot-the-issue questions.
- **Weekly Boss Fight:** Sunday, timed, cumulative. It shows a score breakdown per topic and sends weak spots to the review queue.
- **Interview Mode:** timed Python/C questions, "how would you test this" (you write the pytest file and it's graded against mutants), and debug scenarios.
- **No Hands checkpoints:** the tutor and hints are disabled, and solutions can't be pasted (a paste-length guard). Passing is recorded separately.
- **Accessibility:** keyboard shortcuts (Ctrl+Enter run, Ctrl+Shift+Enter submit, `?` for help), visible focus states, prefers-color-scheme plus a manual toggle, and responsive layout down to phone width.

### 7.7 Optional AI tutor

- The tutor reads `config.local.json` (gitignored, never deployed), which holds `{ "anthropicApiKey": "...", "model": "..." }`. It's fetched only when the site runs from localhost. On GitHub Pages the file doesn't exist, the tutor shows as "off", and everything else works.
- It calls the Messages API directly from the browser (with the required direct-browser-access header). The key never leaves your machine except to the API.
- Exact model ID and defaults will be confirmed against the current API reference in Phase 2. The model is a config value.
- **Context sent:** lesson title, objectives and prose summary, current code, error output, attempt count, and hint tier reached. **Never sent:** the reference solution, which isn't in the deployed site at all.
- **Modes:**
  - Socratic helper: questions first, then tiered hints (nudge, approach, pseudocode).
  - Full solution: only after 3 real attempts (each a submit with changed code that fails tests) **and** an explicit request. The app enforces this gate, not just the prompt.
  - Grill mode: follow-ups like "what if dt = 0?"
  - Explain-back grader: grades against the lesson rubric. A self-check rubric is shown when the tutor is off.
  - Mock Interviewer: scores correctness, clarity, and communication.
- **Coursework guard:** the tutor declines help with graded assignments (ME5245 Project 2, EECE7150 homework) and points you to general lessons instead.

### 7.8 Verification pipeline (`tools/verify.py`, conda env `robotics-course`)

**Where the answer key lives:**

- It's a separate **private** GitHub repo, `python-for-robotics-answer-key`.
- It's cloned into `verification/` inside this repo, and `verification/` is listed in `.gitignore`. Two repos, one working folder: the public repo never sees the files, but `verify.py` can reach them, and the key is still backed up and versioned on GitHub.
- Layout inside the clone: `verification/<lesson-id>/reference.py` and `wrong_<mistake>.py`. Sprint Project reference material isn't stored there, because the Sprint Projects have no reference solutions (you write them).
- The public repo and the deployed site contain only starter code, examples, and the test files.
- If `verification/` is missing (for example, a fresh clone of the public repo), `verify.py` still runs the examples and schema checks. It warns that the answer-key checks were skipped, and a lesson **cannot** be marked done in that state.
- The tutor never receives reference solutions, since they aren't in the site.
- I commit and push the answer-key repo separately, with its own messages, whenever a module is built.

For each lesson, `verify.py`:

1. Runs every example and diffs the output against `expectedOutput`.
2. Runs the hidden tests against `verification/<id>/reference.py`, which must pass.
3. Runs the hidden tests against each `verification/<id>/wrong_*.py` (common beginner mistakes), each of which must fail at least one test.
4. Runs the bug exercise: the buggy file must fail and the fixed reference must pass.
5. Validates the JSON schema and checks that every referenced file exists.
6. Writes a report into `docs/PROGRESS.md`.

Local-only exercises are verified the same way: on Windows for the conda-env exercises, and in the VM for C and ROS 2 (with exact commands logged). A lesson is never marked done without a clean run.

### 7.9 Deployment

- Local: `python -m http.server 8000`, then open `http://localhost:8000`.
- GitHub Pages: a GitHub Actions workflow uploads only the site folders (`index.html`, `app/`, `content/`, `local/`, `vendor/`). `verification/`, `docs/`, `my-solutions/`, and `config.local.json` are never published.
- `.gitignore`: `config.local.json`, `verification/`, `__pycache__/`, `.pytest_cache/`, and local data dumps.

### 7.10 Raspberry Pi and VM: ROS 2 compatibility

**Step 1: identify the Pi** (part of the H4 setup and the first item of M13's VM exercises).

- On the Pi, run `cat /proc/device-tree/model`.
- Or check the board itself: a Pi 5 has a PCIe ribbon connector, a fan header, an RTC battery header, and a small power button. "Raspberry Pi 5" is printed on the board.

**Step 2: pick the setup by model.**

| Pi model | OS / ROS 2 | Plan |
|---|---|---|
| **Pi 4** (2 GB or more) | Ubuntu 22.04 Server, Humble | Matches the VM exactly. Simplest. |
| **Pi 3B/3B+** | Ubuntu 22.04 Server, Humble | Works, but 1 GB of RAM is tight. Build nothing on the Pi; only run nodes there. |
| **Pi 5** | Ubuntu 24.04 is the only officially supported Ubuntu, which pairs with Jazzy | See the compatibility issues and options below. |

**Humble (VM) talking to Jazzy (Pi 5): compatibility issues to know:**

1. **Cross-distro communication isn't officially supported.** Humble and Jazzy often talk to each other over the same DDS (both default to Fast DDS), but nothing guarantees it.
2. **Message definitions must be identical on both sides.** Standard messages (`geometry_msgs/Twist`, `sensor_msgs/Imu`) are generally unchanged between the two distros and usually work. Custom messages must be built from the same `.msg` files on both machines.
3. **Type hashes:** Jazzy nodes publish type description hashes and Humble nodes don't. This can cause warnings or failures in tools that compare types, such as some `ros2 topic` introspection.
4. **Services and actions** are more fragile across distros than plain topics.
5. **Separate from the distro question, VM networking:** the VM's network adapter must be **Bridged** (not NAT) so DDS multicast discovery reaches the Pi. Set the same `ROS_DOMAIN_ID` on both machines and allow UDP through the Windows firewall. This bites every VM-plus-Pi setup, Pi 4 included.

**Decision: the VM moves to Ubuntu 24.04 + Jazzy over winter break** (see the roadmap). After that, the Pi runs Ubuntu 24.04 Server + Jazzy on any model (Pi 4 and Pi 5 are both supported by 24.04; confirm Pi 3 support before relying on it). Both sides then run the same distro, and the cross-distro issues above don't apply.

**If ROS 2 work on the Pi happens before the migration:**

- On a Pi 4, run Humble on 22.04.
- On a Pi 5, run Humble in Docker (official `ros:humble` arm64 image, host networking, `/dev/ttyACM0` passed through).
- Don't mix distros.

Every Bridge to Real Robots box already includes Humble vs Jazzy notes. For a Pi 5, H4 will also include the Docker commands.

---

## 8. Resume rebuild track (summary)

| Project | Draft bullet shape |
|---|---|
| SP1 | "Built an MPU-6050 IMU pipeline: register-level I2C firmware in C, checksummed binary serial protocol, Python driver with N pytest tests in CI; characterized noise with Allan variance (ARW = X °/√h)." |
| SP2 | "Designed an automated DC motor test rig (encoder, INA219, DS18B20); identified a first-order model (τ = X ms, R² = Y) and tuned a PI speed loop that met predicted rise time within Z%; ran an N-cycle endurance test with drift analysis." |
| H4 | "Rewrote the WALL-E robot's ROS 2 stack from scratch: Arduino serial bridge, Raspberry Pi rclpy node, teleop, systemd/udev deployment." |
| M18 / maintenance | "Applied PLC troubleshooting and preventive maintenance methods to robot test and validation (root-cause analysis, reliability data)." This connects the old resume to the new one honestly. |

Each bullet is filled in with your measured numbers only after its project's tests pass, and you must pass its 5-question defense quiz first.

---

## 9. Risks

1. **Sprint 1 minimal by Nov 10 is tight.** You'll be in Module 0 while also writing firmware and a pyserial script. Mitigations:
   - The milestones are small.
   - Background lessons S.1, S.2, and S.8 are delivered just in time inside the Sprint hour.
   - The minimal version uses text CSV, not binary packets.
   - If it slips, the fallback is Nov 13 to 14.
2. **Sprint 2 by mid-December overlaps with Sprint 1's final stretch.** The ME5245 motor lectures (Nov 5 to 19) help, but the realistic finish is Dec 13 to 18.
3. **The parts order must go out by Oct 29** for Sprint 1 to stay on schedule.
4. **Hidden tests are public.** They can be read on GitHub and in browser DevTools. That's inherent to a public repo and static site, so it's an honor system. Reference solutions live only in the private answer-key repo.
5. **The co-op scenario (Version B)** pushes the interview-critical path to about May 23 and the full curriculum to about December 2027.

## 10. Resolved questions (2026-10-28)

| Question | Answer |
|---|---|
| Wire | Allowed as the I2C bus driver. All MPU-6050 register reads/writes are the learner's own code. |
| Nov 10 | Target. Nov 13 to 14 is an acceptable fallback (but see 3.3). |
| Pi model | Unknown. Identify it first (7.10). The VM migrates to 24.04 + Jazzy over winter break. |
| Co-op | Not confirmed. Both roadmap versions are planned (Section 4). |
| Parts | Breadboard and jumpers owned. WALL-E chassis and battery reused. |
| Answer key | Separate private repo, cloned into gitignored `verification/`. The public site repo ships only tests. |
| pyserial | Approved and installed (3.5). |

## 11. Dependencies still needing approval (ask before each install)

  - `scipy`, `pyyaml`, `utm` in `robotics-course` (local exercises, M3 to M9)
  - `torch` with CUDA (M14), `gymnasium` (M15)
  - optionally Playwright for automated browser tests
  - in the VM: confirm `gcc` and `build-essential` are present

## Sources

- [Pyodide: packages built in Pyodide (314.0.7)](https://pyodide.org/en/stable/usage/packages-in-pyodide.html)
- [Huntr: robotics engineer resume skills (257 postings, 2026)](https://huntr.co/resume-skills/robotics-engineer)
- [Magna robotics engineering co-op](https://www.careerbeacon.com/en/job-22/3381958/magna/robotics-engineering-co-op) · [AEVEX robotics co-op](https://www.jobera.com/job/aevexaerospace-robotics-engineering-co-op-d5f25d21/) · [KansasWorks robotics posting](https://www.kansasworks.com/jobs/13616599) · [Beko industrial robotics engineer](https://kockariyerim.com/jobAd/beko-engineer-industrial-robotics/b1afc4b0-2dd9-4424-83d3-8f3e6cde8bb3) · [ZipRecruiter co-op robotics software](https://www.ziprecruiter.com/Jobs/Co-Op-Robotics-Software-Engineer/3)
- MPU-6050 pricing: [Fruugo GY-521 kits](https://www.fruugo.us/gy521-mpu6050-sensor-module-3-axis-gyroscope-accelerometer-for-arduino-precision-tracking/p-460022782), [Maplin](https://pro.maplin.co.uk/products/gy-521-mpu-6050-3-axis-gyroscope-accelerometer-gyro-module)
- Encoder motor pricing: [electric-b2c](https://www.electric-b2c.com/products/dc-6v-12v-24v-high-torque-electric-motor-gear-motor-with-encoder), [Funduino](https://funduinoshop.com/en/diy-workshop/kits/chassis/jga25-370-encoder-gear-motor-kit-12v-12rpm-with-wheel), [Abra JGA25-370-E](https://abra-electronics.com/electromechanical/motors/gear-motors/metal-gearmotors/jga25-370-series/jga25-370-e.html)
- INA219 pricing: [The Pi Hut](https://thepihut.com/products/voltage-current-sensor-ina219-breakout), [Fruugo](https://www.fruugo.us/ina219-dc-current-sensor-with-i2c-interface-for-arduino/p-395202385), [reach.dog Adafruit](https://reach.dog/shop/3dmakerworld-inc/products/adafruit-ina219-high-side-dc-current-sensor-breakout-26v-3-2a-max)
- DS18B20 pricing: [Fruugo 5-pack](https://www.fruugo.ca/5-pack-waterproof-ds18b20-temperature-sensor-probes-with-2-pack-47k-ohm-resistors-for-arduino-raspberry-pi-diy/p-449265981)
- Remaining part prices (HC-SR04, TCRT5000, chassis, webcam, ESP32, LM2596, 18650 kit) are typical US listing ranges, not confirmed by search. Check them in the cart.
