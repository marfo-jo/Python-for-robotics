# Geofence check: is the robot inside the rectangular test area?

def to_degrees(ddmm, hemisphere):
    """Convert NMEA ddmm.mmmm text to signed decimal degrees (S and W are negative)."""
    value = float(ddmm)
    degrees = int(value / 100)
    minutes = value - degrees * 100
    result = degrees + minutes / 60
    if hemisphere == "S" or hemisphere == "W":
        result = -result
    return result


def position(sentence):
    """Return (lat, lon) in decimal degrees from a GGA sentence."""
    fields = sentence.strip().split(",")
    return (to_degrees(fields[2], fields[3]), to_degrees(fields[4], fields[5]))


def inside_fence(sentence, fence):
    """True if the fix is inside fence = (min_lat, max_lat, min_lon, max_lon)."""
    lon, lat = position(sentence)
    min_lat, max_lat, min_lon, max_lon = fence
    lat_ok = min_lat <= lat and lat <= max_lat
    lon_ok = min_lon <= lon and lon <= max_lon
    return lat_ok and lon_ok


TEST_AREA = (42.3350, 42.3360, -71.0935, -71.0920)
parked = "$GPGGA,152305.00,4220.1234,N,07105.5678,W,1,09,1.1,12.3,M,-33.1,M,,*64"
print(position(parked))
print(inside_fence(parked, TEST_AREA))
