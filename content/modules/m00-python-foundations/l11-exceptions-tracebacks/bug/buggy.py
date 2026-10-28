# Mean satellite count over a GPS log, for the Lab 4 data-quality table.
# Lines that can't be parsed (junk, no satellites field) must be ignored.

def mean_satellites(lines):
    total = 0
    count = 0
    for line in lines:
        try:
            count += 1
            fields = line.strip().split(",")
            total += int(fields[7])
        except (ValueError, IndexError):
            continue
    if count == 0:
        return 0.0
    return total / count


log = [
    "$GPGGA,153012.00,4220.0101,N,07105.6600,W,1,09,0.9,10.2,M,-33.1,M,,*62",
    "u-blox NEO-M8N ROM 2.01",
    "$GPGGA,153014.00,4220.0110,N,07105.6584,W,1,10,0.8,10.5,M,-33.1,M,,*65",
]
print(f"mean satellites: {mean_satellites(log):.1f}")
