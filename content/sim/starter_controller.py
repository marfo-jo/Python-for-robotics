# A first controller: drive forward, and turn left when something is close ahead.
# control() is called 20 times per second (dt = 0.05 s).
# It returns (left_wheel_speed, right_wheel_speed) in meters per second.

SAFE_DISTANCE = 0.45   # meters


def control(sensors, dt):
    front = sensors.range[2]          # the beam pointing straight ahead
    if front < SAFE_DISTANCE:
        return (-0.10, 0.10)          # spin left in place
    return (0.25, 0.25)               # drive straight
