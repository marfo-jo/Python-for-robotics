# A realistic field log: a receiver boot banner, a blank line, a corrupted
# sentence, and a last line cut off when the robot's battery died.
with open("run1.txt", "w", encoding="utf-8") as f:
    f.write("u-blox NEO-M8N ROM 2.01\n")
    f.write("$GPGGA,153012.00,4220.0101,N,07105.6600,W,1,09,0.9,10.2,M,-33.1,M,,*62\n")
    f.write("\n")
    f.write("$GPRMC,153012.00,A,4220.0101,N,07105.6600,W,0.52,54.70,281026,,,A*71\n")
    f.write("$GPGGA,153013.00,4220.0105,N,07105.6592,W,1,09,0.9,10.4,M,-33.1,M,,*69\n")
    f.write("$GPGGA,153014.00,4220.0110,N,07105.6584,W,1,10,0.8,10.5,M,-33.1,M,,*66\n")
    f.write("$GPGGA,153015.00,4220.01")


def looks_like_nmea(sentence):
    """Shape check only: '$' at the start, and exactly 2 characters after '*'."""
    star = sentence.find("*")
    return sentence.startswith("$") and star != -1 and len(sentence) == star + 3


good = []
errors = 0
line_number = 0
with open("run1.txt", encoding="utf-8") as f:
    for line in f:
        line_number += 1
        line = line.strip()
        if line == "":
            continue
        if looks_like_nmea(line):
            good.append(line)
        else:
            errors += 1
            print(f"line {line_number}: rejected ...{line[-12:]!r}")

print(f"{len(good)} good sentences, {errors} errors, {line_number} lines read")
print(good[-1][:16], "<- corrupted, but it LOOKS fine: only a checksum catches it")
