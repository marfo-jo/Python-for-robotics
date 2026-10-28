# to_degrees is given (you'll derive it yourself in lesson 0.9). Keep it.
def to_degrees(ddmm, hemisphere):
    """Convert NMEA ddmm.mmmm text to signed decimal degrees (S and W are negative)."""
    value = float(ddmm)
    degrees = int(value / 100)
    minutes = value - degrees * 100
    result = degrees + minutes / 60
    if hemisphere == "S" or hemisphere == "W":
        result = -result
    return result


def fix_record(sentence):
    """Return (utc_time, lat, lon) from a GGA sentence, as a tuple.

    utc_time is the text of field 1. lat and lon are signed decimal degrees
    (use to_degrees on fields 2-3 and 4-5). Any talker counts ($GPGGA,
    $GNGGA, ...). Return None if the sentence is not GGA, has fewer than 15
    fields, or its latitude or longitude field is empty.
    """
    return None


def bounding_box(records):
    """Return ((min_lat, min_lon), (max_lat, max_lon)) for a list of
    (utc_time, lat, lon) records, or None if the list is empty."""
    return None


# Try your functions with Run before you Submit:
a = fix_record("$GPGGA,152305.00,4220.1234,N,07105.5678,W,1,09,1.1,12.3,M,-33.1,M,,*64")
b = fix_record("$GPGGA,152309.00,4220.1270,N,07105.5725,W,1,10,0.7,13.1,M,-33.1,M,,*6D")
print(a)                    # about ('152305.00', 42.33539, -71.0928)
print(bounding_box([a, b]))
