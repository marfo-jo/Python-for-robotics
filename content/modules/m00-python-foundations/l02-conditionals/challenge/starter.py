# Fill in the body of each function using if / elif / else, comparisons,
# and and / or / not. (Functions are covered properly in lesson 0.6. For now:
# the input arrives in the parameters, and `return` hands back the answer.)
# Remember: sentences may have spaces or "\r\n" around them, and fields may be empty.


def fix_status(sentence):
    # Return exactly one of these strings:
    #   "not GGA"   the sentence isn't a $--GGA sentence at all
    #   "no data"   GGA, but the fix-quality field is empty
    #   "no fix"    quality "0"
    #   "GPS"       quality "1"
    #   "DGPS"      quality "2"
    #   "RTK fixed" quality "4"
    #   "RTK float" quality "5"
    #   "other"     any other quality code
    return ""      # replace this with your if / elif / else


def is_usable(sentence, min_sats):
    # True only if: it's a GGA sentence, the quality is a real fix
    # ("1", "2", "4", or "5"), the satellite field is not empty, and the
    # number of satellites is at least min_sats. Otherwise False.
    return False


# Try your functions with Run before you Submit:
print(fix_status("$GPGGA,123519,4807.038,N,01131.000,E,1,08,0.9,545.4,M,46.9,M,,*47"))
print(fix_status("$GNRMC,220516,A,4221.123,N,07105.456,W,0.13,309.62,281026,,,A*7C"))
print(is_usable("$GPGGA,123519,4807.038,N,01131.000,E,1,08,0.9,545.4,M,46.9,M,,*47", 6))
