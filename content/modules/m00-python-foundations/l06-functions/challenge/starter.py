# Two functions that compose: is_gga() validates, parse_gga() uses it.
# The docstrings are the spec. Replace each placeholder return with real code.


def is_gga(sentence):
    """Return True if `sentence` is a GGA sentence, else False.

    After stripping whitespace, a GGA sentence starts with '$', its type
    (characters 3 to 6) is 'GGA' for ANY talker ('$GPGGA', '$GNGGA', ...),
    and it splits into at least 15 comma-separated fields.
    """
    return False


def parse_gga(sentence, min_sats=4):
    """Parse a GGA sentence into [utc_time, fix_quality, satellites, altitude_m].

    utc_time is a str (field 1), fix_quality an int (field 6), satellites an
    int (field 7), and altitude_m a float (field 9).

    Return None instead if the sentence is not GGA (use is_gga), if
    fix_quality is 0 (no fix), or if satellites < min_sats.
    """
    return None


# Try your functions with Run before you Submit:
line = "$GPGGA,152305.00,4220.1234,N,07105.5678,W,1,09,1.1,12.3,M,-33.1,M,,*64\r\n"
print(is_gga(line))       # expect True
print(parse_gga(line))    # expect ['152305.00', 1, 9, 12.3]
