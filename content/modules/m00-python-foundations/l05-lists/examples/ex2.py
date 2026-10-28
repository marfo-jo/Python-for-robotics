# Four fixes from a walk around the quad, one second apart.
log = [
    "$GPGGA,152305.00,4220.1234,N,07105.5678,W,1,09,1.1,12.3,M,-33.1,M,,*64",
    "$GPGGA,152306.00,4220.1240,N,07105.5690,W,1,03,2.8,13.0,M,-33.1,M,,*60",
    "$GPGGA,152307.00,4220.1251,N,07105.5702,W,2,07,1.4,12.8,M,-33.1,M,,*6A",
    "$GPGGA,152308.00,4220.1262,N,07105.5714,W,1,08,1.0,12.9,M,-33.1,M,,*6B",
]

sats = []                          # start EMPTY, then grow it
hdops = []
for line in log:
    fields = line.split(",")
    sats.append(int(fields[7]))    # text "09" -> number 9
    hdops.append(float(fields[8])) # text "1.1" -> number 1.1

print(sats)
print(hdops)
print(len(sats), "fixes")
print("best HDOP:", min(hdops))
print("worst HDOP:", max(hdops))

for i, h in enumerate(hdops):      # enumerate gives (position, item) pairs
    if h > 2.0:
        print("fix", i, "is poor: HDOP", h, "with", sats[i], "satellites")

print("average satellites:", sum(sats) / len(sats))
