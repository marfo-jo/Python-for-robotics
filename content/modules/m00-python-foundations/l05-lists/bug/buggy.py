# Clamp altitude readings for the live plot, so one multipath spike
# (a GPS signal bouncing off a building) doesn't squash the y-axis.
# The raw log must stay untouched: it's saved for the post-run report.

def clamped(altitudes, ceiling):
    result = altitudes
    for i, alt in enumerate(result):
        if alt > ceiling:
            result[i] = ceiling
    return result


raw = [12.3, 13.0, 87.4, 12.9]
plot = clamped(raw, 20.0)
print("plot:", plot)
print("raw: ", raw)
