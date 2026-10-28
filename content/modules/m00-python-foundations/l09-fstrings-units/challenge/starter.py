# 1. nmea_to_decimal: NMEA position text + hemisphere letter -> signed decimal degrees.
#    Latitude arrives as ddmm.mmmm, longitude as dddmm.mmmm, and you are NOT told
#    which one you got, so find the degrees/minutes split another way.
#    Return None if either field is empty (the receiver has no fix yet).
# 2. format_position: signed decimal degrees -> a label like '42.333502°N, 71.094333°W'.


def nmea_to_decimal(value, hemisphere):
    return 0.0     # replace with your conversion


def format_position(lat, lon):
    return ""      # replace with an f-string


# Try your functions with Run before you Submit:
print(nmea_to_decimal("4220.0101", "N"))     # expect about 42.333502
print(nmea_to_decimal("07105.6600", "W"))    # expect about -71.094333
print(nmea_to_decimal("", ""))               # expect None
print(format_position(42.3335017, -71.0943333))
