# Validate a sentence, then classify its fix quality.
raw = "  $GNGGA,142206.00,4220.1152,N,07105.4888,W,5,11,0.7,12.9,M,-33.1,M,1.2,0000*57\r\n"
line = raw.strip()

if not line.startswith("$") or line[3:6] != "GGA":
    print("rejected: not a GGA sentence")
else:
    fields = line.split(",")
    quality = fields[6]
    if quality == "":
        status = "no data"
    elif quality == "0":
        status = "no fix"
    elif quality == "1":
        status = "GPS"
    elif quality == "2":
        status = "DGPS"
    elif quality == "4":
        status = "RTK fixed"
    elif quality == "5":
        status = "RTK float"
    else:
        status = "other"
    print(line[1:3], line[3:6], "quality", quality, "->", status)

    sats = fields[7]
    if sats and int(sats) >= 6:    # and stops early if sats is empty
        print("enough satellites:", int(sats))

other = "$GNRMC,220516,A,4221.123,N,07105.456,W,0.13,309.62,281026,,,A*7C"
print(other[3:6] == "GGA")         # an RMC sentence would be rejected
