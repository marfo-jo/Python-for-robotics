# Two receivers, two talker IDs, and one sends lowercase hex.
a = "$GPGGA,123519,4807.038,N,01131.000,E,1,08,0.9,545.4,M,46.9,M,,*47"
b = "  $GNRMC,220516,A,4221.123,N,07105.456,W,0.13,309.62,281026,,,A*7c \r\n"

b = b.strip()                  # always clean the line first

print(a.startswith("$"), b.startswith("$"))
print(a[1:3], a[3:6])          # talker, type
print(b[1:3], b[3:6])

star = b.find("*")             # where the checksum marker is
print(star)
print(b[star + 1:])            # everything after '*'
print(b[star + 1:].upper())    # normalize hex to uppercase
print("RMC" in b, "GGA" in b)
print(b.find("#"))             # -1 means "not found"
