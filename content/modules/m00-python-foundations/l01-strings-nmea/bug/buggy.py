# Returns the fix-quality field of a $GPGGA sentence as a string.
# Fix quality: "0" = no fix, "1" = GPS fix, "2" = DGPS fix, "4" = RTK fixed.

def fix_quality(sentence):
    fields = sentence.strip().split(",")
    return fields[5]


print(fix_quality("$GPGGA,123519,4807.038,N,01131.000,E,1,08,0.9,545.4,M,46.9,M,,*47"))
