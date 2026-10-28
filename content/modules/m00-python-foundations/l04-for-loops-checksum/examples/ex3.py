# The NMEA checksum: XOR every character BETWEEN '$' and '*'.
raw = "$GPGGA,123519,4807.038,N,01131.000,E,1,08,0.9,545.4,M,46.9,M,,*47\r\n"
line = raw.strip()

star = line.find("*")
body = line[1:star]          # skip the '$' at index 0; stop BEFORE the '*'
print(body[:12], "...", body[-6:])

checksum = 0                 # 0 is the "do nothing" starting value for XOR
for ch in body:
    checksum = checksum ^ ord(ch)

print(checksum, format(checksum, "08b"))
print(format(checksum, "02X"))
given = line[star + 1:].upper()
print("given", given, "computed", format(checksum, "02X"))
print(format(checksum, "02X") == given)
