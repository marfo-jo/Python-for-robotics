"""2D differential-drive robot simulator (pure Python, no NumPy).

The same file runs in the browser (Pyodide) and in local pytest, so any
hidden test that drives the simulator is verified with real CPython.

Units: meters, seconds, radians. World frame: x right, y up, theta CCW from +x.

Learner API:
    def control(sensors, dt):
        ...
        return left_wheel_speed, right_wheel_speed    # m/s at the wheel rim

sensors fields (all noisy, seeded so runs are reproducible):
    sensors.t                 time since start [s]
    sensors.range             list of distances [m] for RANGE_ANGLES (max RANGE_MAX)
    sensors.range_angles      the beam angles relative to the robot heading [rad]
    sensors.imu.gyro_z        yaw rate [rad/s] (includes a small constant bias)
    sensors.imu.accel_x       forward acceleration [m/s^2]
    sensors.encoders.left     cumulative wheel ticks (TICKS_PER_REV per revolution)
    sensors.encoders.right
    sensors.gps               None, or (x, y) [m] once per GPS_PERIOD with ~0.3 m noise
    sensors.camera            list of CAMERA_PIXELS brightness values in [0, 1]
                              looking at the floor ahead (0 = dark line)
"""
import math
import random
from types import SimpleNamespace

DT = 0.05                      # control period [s] (20 Hz)
SUBSTEPS = 4                   # physics substeps per control period
WHEEL_BASE = 0.16              # distance between wheels [m]
WHEEL_RADIUS = 0.033           # [m]
ROBOT_RADIUS = 0.09            # collision radius [m]
MAX_WHEEL_SPEED = 0.4          # [m/s]
TICKS_PER_REV = 360
RANGE_ANGLES = [-math.pi / 2, -math.pi / 4, 0.0, math.pi / 4, math.pi / 2]
RANGE_MAX = 2.0
GPS_PERIOD = 1.0
CAMERA_PIXELS = 16
CAMERA_AHEAD = 0.12            # [m] in front of the robot center
CAMERA_WIDTH = 0.20            # [m] field of view across the robot
LINE_HALF_WIDTH = 0.012        # [m] (a 2.4 cm tape line)

NOISE = {"range": 0.01, "gyro": 0.005, "gyro_bias": 0.01, "accel": 0.02,
         "encoder_slip": 0.01, "gps": 0.3, "camera": 0.05}


def wrap_angle(a):
    """Wrap an angle to (-pi, pi]."""
    a = math.fmod(a + math.pi, 2 * math.pi)
    if a <= 0:
        a += 2 * math.pi
    return a - math.pi


class World:
    def __init__(self, width=4.0, height=3.0, walls=None, obstacles=None,
                 line=None, start=(0.5, 0.5, 0.0), goal=None, name="world"):
        self.width = width
        self.height = height
        self.name = name
        boundary = [(0, 0, width, 0), (width, 0, width, height),
                    (width, height, 0, height), (0, height, 0, 0)]
        self.walls = boundary + [tuple(w) for w in (walls or [])]
        self.obstacles = [tuple(o) for o in (obstacles or [])]   # (x, y, r)
        self.line = [tuple(p) for p in (line or [])]             # polyline
        self.start = tuple(start)
        self.goal = tuple(goal) if goal else None                # (x, y, r)

    @classmethod
    def from_dict(cls, d):
        return cls(width=d.get("width", 4.0), height=d.get("height", 3.0),
                   walls=d.get("walls"), obstacles=d.get("obstacles"),
                   line=d.get("line"), start=d.get("start", (0.5, 0.5, 0.0)),
                   goal=d.get("goal"), name=d.get("name", "world"))

    # ---- geometry helpers ------------------------------------------------
    def raycast(self, x, y, angle, max_range=RANGE_MAX):
        dx, dy = math.cos(angle), math.sin(angle)
        best = max_range
        for (x1, y1, x2, y2) in self.walls:
            ex, ey = x2 - x1, y2 - y1
            denom = dx * ey - dy * ex
            if abs(denom) < 1e-12:
                continue
            t = ((x1 - x) * ey - (y1 - y) * ex) / denom
            u = ((x1 - x) * dy - (y1 - y) * dx) / denom
            if 0 <= u <= 1 and 0 < t < best:
                best = t
        for (cx, cy, r) in self.obstacles:
            fx, fy = x - cx, y - cy
            b = fx * dx + fy * dy
            c = fx * fx + fy * fy - r * r
            disc = b * b - c
            if disc >= 0:
                t = -b - math.sqrt(disc)
                if 0 < t < best:
                    best = t
        return best

    def collides(self, x, y, radius=ROBOT_RADIUS):
        for (x1, y1, x2, y2) in self.walls:
            if _point_segment_distance(x, y, x1, y1, x2, y2) < radius:
                return True
        for (cx, cy, r) in self.obstacles:
            if math.hypot(x - cx, y - cy) < r + radius:
                return True
        return False

    def line_distance(self, x, y):
        if len(self.line) < 2:
            return float("inf")
        return min(_point_segment_distance(x, y, *self.line[i], *self.line[i + 1])
                   for i in range(len(self.line) - 1))

    def to_dict(self):
        return {"name": self.name, "width": self.width, "height": self.height,
                "walls": [list(w) for w in self.walls[4:]],
                "obstacles": [list(o) for o in self.obstacles],
                "line": [list(p) for p in self.line], "start": list(self.start),
                "goal": list(self.goal) if self.goal else None}


def _point_segment_distance(px, py, x1, y1, x2, y2):
    ex, ey = x2 - x1, y2 - y1
    seg2 = ex * ex + ey * ey
    t = 0.0 if seg2 == 0 else max(0.0, min(1.0, ((px - x1) * ex + (py - y1) * ey) / seg2))
    return math.hypot(px - (x1 + t * ex), py - (y1 + t * ey))


class SimResult:
    def __init__(self, world):
        self.world = world
        self.frames = []
        self.collided = False
        self.reached_goal = False
        self.time_to_goal = None
        self.distance = 0.0

    def to_dict(self):
        return {"world": self.world.to_dict(), "frames": self.frames,
                "collided": self.collided, "reachedGoal": self.reached_goal,
                "timeToGoal": self.time_to_goal, "distance": round(self.distance, 4),
                "dt": DT}


def _clamp(v, lo, hi):
    return lo if v < lo else hi if v > hi else v


def run(world, control, seconds=30.0, seed=1, stop_at_goal=True):
    """Run a control function in the world and record every control step."""
    rng = random.Random(seed)
    x, y, th = world.start
    v_prev = 0.0
    gyro_bias = NOISE["gyro_bias"]
    ticks_l = ticks_r = 0.0
    wheel_l = wheel_r = 0.0
    result = SimResult(world)
    steps = int(round(seconds / DT))
    for k in range(steps):
        t = k * DT
        ranges = [max(0.0, world.raycast(x, y, th + a) + rng.gauss(0, NOISE["range"]))
                  for a in RANGE_ANGLES]
        ranges = [min(r, RANGE_MAX) for r in ranges]
        omega_true = (wheel_r - wheel_l) / WHEEL_BASE
        v_true = (wheel_r + wheel_l) / 2
        gps = None
        if abs((t / GPS_PERIOD) - round(t / GPS_PERIOD)) < 1e-9:
            gps = (x + rng.gauss(0, NOISE["gps"]), y + rng.gauss(0, NOISE["gps"]))
        camera = []
        for i in range(CAMERA_PIXELS):
            lateral = (i - (CAMERA_PIXELS - 1) / 2) * CAMERA_WIDTH / (CAMERA_PIXELS - 1)
            px = x + CAMERA_AHEAD * math.cos(th) - lateral * math.sin(th)
            py = y + CAMERA_AHEAD * math.sin(th) + lateral * math.cos(th)
            dark = world.line_distance(px, py) < LINE_HALF_WIDTH
            value = (0.1 if dark else 0.9) + rng.gauss(0, NOISE["camera"])
            camera.append(_clamp(value, 0.0, 1.0))
        sensors = SimpleNamespace(
            t=round(t, 6), range=ranges, range_angles=list(RANGE_ANGLES),
            imu=SimpleNamespace(gyro_z=omega_true + gyro_bias + rng.gauss(0, NOISE["gyro"]),
                                accel_x=(v_true - v_prev) / DT + rng.gauss(0, NOISE["accel"])),
            encoders=SimpleNamespace(left=int(ticks_l), right=int(ticks_r)),
            gps=gps, camera=camera)
        v_prev = v_true

        command = control(sensors, DT)
        if not (isinstance(command, (tuple, list)) and len(command) == 2):
            raise TypeError("control() must return a pair (left_speed, right_speed), "
                            f"but it returned {command!r}")
        left, right = (float(c) for c in command)
        if math.isnan(left) or math.isnan(right):
            raise ValueError("control() returned NaN; check for a division by zero.")
        wheel_l = _clamp(left, -MAX_WHEEL_SPEED, MAX_WHEEL_SPEED)
        wheel_r = _clamp(right, -MAX_WHEEL_SPEED, MAX_WHEEL_SPEED)

        result.frames.append({"t": round(t, 3), "x": round(x, 4), "y": round(y, 4),
                              "th": round(th, 4), "ranges": [round(r, 3) for r in ranges],
                              "cmd": [round(wheel_l, 3), round(wheel_r, 3)],
                              "gps": [round(g, 3) for g in gps] if gps else None})

        h = DT / SUBSTEPS
        for _ in range(SUBSTEPS):
            v = (wheel_r + wheel_l) / 2
            w = (wheel_r - wheel_l) / WHEEL_BASE
            nx = x + v * math.cos(th) * h
            ny = y + v * math.sin(th) * h
            nth = wrap_angle(th + w * h)
            if world.collides(nx, ny):
                result.collided = True
                th = nth
                continue
            result.distance += math.hypot(nx - x, ny - y)
            x, y, th = nx, ny, nth
            circumference = 2 * math.pi * WHEEL_RADIUS
            slip_l = 1 + rng.gauss(0, NOISE["encoder_slip"])
            slip_r = 1 + rng.gauss(0, NOISE["encoder_slip"])
            ticks_l += wheel_l * h / circumference * TICKS_PER_REV * slip_l
            ticks_r += wheel_r * h / circumference * TICKS_PER_REV * slip_r
        if world.goal and not result.reached_goal:
            gx, gy, gr = world.goal
            if math.hypot(x - gx, y - gy) < gr:
                result.reached_goal = True
                result.time_to_goal = round(t + DT, 3)
                if stop_at_goal:
                    result.frames.append({"t": round(t + DT, 3), "x": round(x, 4),
                                          "y": round(y, 4), "th": round(th, 4),
                                          "ranges": ranges, "cmd": [0, 0], "gps": None})
                    break
    return result

