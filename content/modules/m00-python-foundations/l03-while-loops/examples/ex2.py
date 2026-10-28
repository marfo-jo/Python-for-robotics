# Wait until a sensor reading settles below 1.0 (say, wheel speed after a stop).
readings = [4.0, 2.5, 1.2, 0.6, 0.3]

# BUGGY version: i never changes, so the condition never changes.
# A scan counter acts like a watchdog so this example can't hang forever.
i = 0
scans = 0
while i < len(readings) and readings[i] >= 1.0:
    scans += 1
    if scans > 10:
        print("watchdog: still stuck at i =", i)
        break                      # break: leave the loop immediately
print("buggy loop gave up after", scans, "scans")

# FIXED version: each pass moves to the next reading.
i = 0
while i < len(readings) and readings[i] >= 1.0:
    i += 1
print("settled at index", i, "value", readings[i])
