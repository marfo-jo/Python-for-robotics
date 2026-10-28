# A countdown: the condition is checked BEFORE every pass through the body.
countdown = 3
while countdown > 0:
    print("T minus", countdown)
    countdown = countdown - 1     # progress: without this line, it never ends
print("motors armed, countdown =", countdown)

# Counting up with += (shorthand for "count = count + 1")
count = 0
while count < 4:
    count += 1
print("count after the loop:", count)

# If the condition is False at the start, the body runs zero times.
volts = 12.4
while volts < 11.1:
    print("waiting for charger")  # never printed
print("loop skipped, volts =", volts)
