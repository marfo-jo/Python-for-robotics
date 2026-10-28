# Retry until a valid GGA fix arrives, but never more than max_tries reads.
# The list stands in for the serial port: incoming[i] is the i-th line read.
incoming = [
    "",                                   # partial garbage at power-up
    "$GPGGA,,,,,,0,,,,,,,,*66",           # GGA, but no fix yet
    "$GNRMC,220516,A,4221.123,N,07105.456,W,0.13,309.62,281026,,,A*7C",
    "$GPGGA,142208.00,4220.1155,N,07105.4886,W,1,04,2.1,13.0,M,-33.1,M,,*6F\r\n",
    "$GPGGA,142209.00,4220.1156,N,07105.4885,W,6,05,1.9,13.0,M,-33.1,M,,*63",
]

max_tries = 5
tries = 0
found = ""
while tries < max_tries and tries < len(incoming):
    line = incoming[tries].strip()
    tries += 1
    if line[3:6] != "GGA":
        print("try", tries, "- not GGA, retry")
    elif line.split(",")[6] == "0":
        print("try", tries, "- no fix yet, retry")
    else:
        found = line
        break

if found:
    print("fix after", tries, "tries:", found[:30])
else:
    print("timeout: no fix in", tries, "tries")
