sentences = [
    "$GPGGA,153012.00,4220.0101,N,07105.6600,W,1,09,0.9,10.2,M,-33.1,M,,*62",
    "$GPGGA,,,,,,0,,,,,,,,*66",        # no fix: the satellites field is empty
    "$GPGGA,153015.00,4220.01",         # truncated: there is no field 7 at all
]

for s in sentences:
    fields = s.split(",")
    try:
        sats = int(fields[7])
        print("satellites:", sats)
    except ValueError:                  # field 7 exists but isn't a number
        print("field 7 is not a number")
    except IndexError:                  # field 7 doesn't exist
        print(f"only {len(fields)} fields, no field 7")

# One handler for both, when you'd do the same thing either way.
# 'as err' gives you the exception object, so you can report its type.
for s in sentences:
    try:
        sats = int(s.split(",")[7])
    except (ValueError, IndexError) as err:
        print("skipped:", type(err).__name__)
