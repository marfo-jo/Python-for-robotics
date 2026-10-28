# A dict can map field NAMES to field INDEXES, so the magic numbers live in one place.
GGA_FIELDS = {"time": 1, "lat": 2, "lat_dir": 3, "lon": 4, "lon_dir": 5,
              "quality": 6, "satellites": 7, "hdop": 8, "altitude": 9}


def raw_fields(sentence):
    """Return {field name: text} for every NON-empty GGA field."""
    fields = sentence.strip().split(",")
    result = {}
    for name, index in GGA_FIELDS.items():    # items() gives (key, value) pairs
        if fields[index] != "":
            result[name] = fields[index]
    return result


good = raw_fields("$GPGGA,152305.00,4220.1234,N,07105.5678,W,1,09,1.1,12.3,M,-33.1,M,,*64")
for name, text in good.items():
    print(name, "=", text)

no_fix = raw_fields("$GPGGA,,,,,,0,00,,,M,,M,,*66")
print(no_fix)
print(no_fix.get("altitude", "no altitude yet"))
print(list(no_fix.keys()))
