def to_degrees(ddmm, hemisphere):
    """Convert NMEA ddmm.mmmm text to signed decimal degrees (derived in lesson 0.9)."""
    value = float(ddmm)
    degrees = int(value / 100)          # 4220.1234 -> 42
    minutes = value - degrees * 100     # 4220.1234 -> 20.1234
    result = degrees + minutes / 60
    if hemisphere == "S" or hemisphere == "W":
        result = -result                # south and west are negative
    return result


def position(sentence):
    """Return (lat, lon) in decimal degrees from a GGA sentence."""
    fields = sentence.strip().split(",")
    lat = to_degrees(fields[2], fields[3])
    lon = to_degrees(fields[4], fields[5])
    return lat, lon                     # two values out = one tuple out


gga = "$GPGGA,152305.00,4220.1234,N,07105.5678,W,1,09,1.1,12.3,M,-33.1,M,,*64"

pos = position(gga)
print(type(pos).__name__, len(pos))

lat, lon = position(gga)                # unpack straight into two names
print(round(lat, 5), round(lon, 5))     # Boston: north is +, west is -

# Swapping: Python packs the right side into a tuple first, then unpacks it.
a, b = lon, lat                         # oops, wrong order
a, b = b, a                             # swap, no temporary variable needed
print(round(a, 5), round(b, 5))
