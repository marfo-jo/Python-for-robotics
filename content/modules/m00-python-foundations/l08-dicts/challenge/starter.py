# Two functions. The docstrings are the spec. Replace each placeholder return.


def gga_to_dict(sentence):
    """Parse a GGA sentence (any talker) into a dict.

    Keys and types:
        "time"       str    field 1
        "quality"    int    field 6
        "satellites" int    field 7
        "hdop"       float  field 8
        "altitude"   float  field 9

    Leave a key OUT if its field is empty (receivers send empty fields
    before they have a fix). Return None if the sentence is not GGA or has
    fewer than 15 fields.
    """
    return {}


def count_types(sentences):
    """Return a dict mapping each sentence type ('GGA', 'RMC', ...) to how
    many times it appears in the list. The type is characters 3 to 6 of the
    stripped line, so $GPGGA and $GNGGA both count as 'GGA'. Skip blank
    lines and lines that don't start with '$'.
    """
    return {}


# Try your functions with Run before you Submit:
print(gga_to_dict("$GPGGA,152305.00,4220.1234,N,07105.5678,W,1,09,1.1,12.3,M,-33.1,M,,*64"))
print(gga_to_dict("$GPGGA,,,,,,0,00,,,M,,M,,*66"))       # expect {'quality': 0, 'satellites': 0}
print(count_types([
    "$GPGGA,152305.00,4220.1234,N,07105.5678,W,1,09,1.1,12.3,M,-33.1,M,,*64",
    "$GPRMC,152305.00,A,4220.1234,N,07105.5678,W,0.05,87.30,281026,,,A*75",
    "$GNGGA,201530.00,4220.0101,N,07105.6600,W,4,12,0.6,10.2,M,-33.1,M,1.0,0000*52",
]))                                                        # expect {'GGA': 2, 'RMC': 1}
