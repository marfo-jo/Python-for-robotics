## Simulator reference

The robot is a **differential drive** robot, like a WALL-E chassis with two driven wheels and a caster. It has a 0.16 m wheel base and a 0.09 m collision radius. Your `control(sensors, dt)` runs every **dt = 0.05 s** (20 Hz). It returns `(left, right)` wheel rim speeds in **m/s**, and each is clamped to ±0.4 m/s.

| Field | Meaning | Noise |
|---|---|---|
| `sensors.t` | time since start, s | none |
| `sensors.range` | list of 5 distances in m, max 2.0 | σ ≈ 1 cm |
| `sensors.range_angles` | beam angles relative to the heading: −90°, −45°, 0°, +45°, +90° (in radians) | |
| `sensors.imu.gyro_z` | yaw rate, rad/s | σ 0.005, plus a constant **bias** of 0.01 rad/s |
| `sensors.imu.accel_x` | forward acceleration, m/s² | σ 0.02 |
| `sensors.encoders.left` / `.right` | cumulative wheel ticks (360 per revolution, wheel radius 0.033 m) | ~1% slip |
| `sensors.gps` | `None` most steps, or `(x, y)` once per second | σ ≈ 0.3 m |
| `sensors.camera` | 16 floor-brightness values in 0..1 across the robot's front, 0.12 m ahead (dark ≈ 0.1 = line) | σ 0.05 |

**Conventions used everywhere on this site:** the robot's x axis (heading) is red and its y axis is green. The true path is drawn solid and dark, and noisy measurements and estimates are orange.

**Why the noise?** Real sensors are noisy and biased. A controller that only works with perfect data fails on hardware. The gyro bias here is the same problem you'll measure on your own MPU-6050 in Sprint 1.
