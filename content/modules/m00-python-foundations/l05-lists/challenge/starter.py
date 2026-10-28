# Fill in each function body between the def line and the return.
# (Functions are covered properly in lesson 0.6. For now, treat each one as a
# circuit block: the inputs come in on the def line, the result leaves on return.)


def satellite_counts(sentences):
    # sentences is a list of NMEA lines (strings). Build and return a list of
    # satellite counts (ints) from the GGA sentences, in order.
    counts = []
    # your loop goes here
    return counts


def last_n(readings, n):
    # Return a NEW list holding the newest n readings (the end of the list).
    # Don't change `readings` itself.
    return []


# Try your functions with Run before you Submit:
log = [
    "$GPGGA,152305.00,4220.1234,N,07105.5678,W,1,09,1.1,12.3,M,-33.1,M,,*64",
    "$GNRMC,220516,A,4221.123,N,07105.456,W,0.13,309.62,281026,,,A*7C",
    "$GPGGA,152306.00,4220.1240,N,07105.5690,W,1,03,2.8,13.0,M,-33.1,M,,*60",
]
print(satellite_counts(log))                      # expect [9, 3]
print(last_n([12.3, 13.0, 12.8, 12.9, 13.1], 3))  # expect [12.8, 12.9, 13.1]
