# Count sentence types in a log: the most common dict pattern there is.
log = [
    "$GPGGA,152305.00,4220.1234,N,07105.5678,W,1,09,1.1,12.3,M,-33.1,M,,*64",
    "$GPRMC,152305.00,A,4220.1234,N,07105.5678,W,0.05,87.30,281026,,,A*75",
    "$GPGSA,A,3,03,04,06,13,17,19,24,28,,,,,1.8,1.0,1.5*3F",
    "$GPGSV,3,1,11,03,03,111,00,04,15,270,00,06,01,010,00,13,06,292,00*74",
    "$GPGGA,152306.00,4220.1240,N,07105.5690,W,1,03,2.8,13.0,M,-33.1,M,,*60",
    "",                                  # blank line from the serial port
    "$GPVTG,309.62,T,,M,0.13,N,0.2,K,A*03",
    "$GPGGA,152307.00,4220.1251,N,07105.5702,W,2,07,1.4,12.8,M,-33.1,M,,*6A",
]

counts = {}
for line in log:
    line = line.strip()
    if line.startswith("$"):
        kind = line[3:6]
        counts[kind] = counts.get(kind, 0) + 1   # 0 the first time, then +1

print(counts)
for kind, n in counts.items():
    print(kind, n)

print("GSA" in counts, counts.get("ZDA", 0))   # never seen ZDA: default 0
print(sum(counts.values()), "sentences")
