# A wheel coasting to a stop. Each 10 ms control scan it keeps 60% of its speed.
# How many scans until it's below 50 rpm? A while loop answers "how many?"
# questions when you can't know the count in advance.
rpm = 1200.0
scans = 0
while rpm >= 50.0:
    rpm = rpm * 0.6
    scans += 1
print(scans, "scans =", scans * 10, "ms")
print("final speed:", round(rpm, 1), "rpm")

# The same loop with a safety limit: give up after 5 scans even if not settled.
rpm = 1200.0
scans = 0
max_scans = 5
while rpm >= 50.0 and scans < max_scans:
    rpm = rpm * 0.6
    scans += 1
if rpm >= 50.0:
    print("TIMEOUT after", scans, "scans, still at", round(rpm, 1), "rpm")
