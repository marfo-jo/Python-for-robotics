# Ground speed from consecutive GPS fixes, to compare with wheel odometry in Lab 4.
# Each sample is (utc_time_text, distance_along_track_m), e.g. ("153059.00", 120.0).
# The UTC time comes straight from GGA field 1, in hhmmss.ss format.

def utc_seconds(hhmmss):
    """'153059.00' -> seconds since midnight, as a float."""
    return float(hhmmss)


def speeds(samples):
    """Speed in m/s between each pair of consecutive samples."""
    result = []
    for i in range(1, len(samples)):
        t0, d0 = samples[i - 1]
        t1, d1 = samples[i]
        dt = utc_seconds(t1) - utc_seconds(t0)
        result.append((d1 - d0) / dt)
    return result


samples = [("153058.00", 0.0), ("153059.00", 1.5), ("153100.00", 3.0), ("153101.00", 4.5)]
for v in speeds(samples):
    print(f"{v:.2f} m/s")
