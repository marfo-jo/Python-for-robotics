# Real serial logs contain cut-off lines. Check the length BEFORE you index.
lines = [
    "$GPGGA,152309.00,4220.1270,N,07105.5725,W,1,10,0.7,13.1,M,-33.1,M,,*6D",
    "$GPGGA,152310.00,4220.12",          # cut off mid-transmission
    "$GPGGA,,,,,,0,00,,,M,,M,,*66",      # no fix yet: empty fields
]

for line in lines:
    fields = line.split(",")
    print(len(fields), "fields")
    # fields[9] only exists if there are at least 10 items (indexes 0..9)
    if len(fields) > 9 and fields[9] != "":
        print("  altitude", fields[9], "m")
    else:
        print("  no altitude in this sentence")

short = "$GPGGA,152310.00,4220.12".split(",")
print(short[-1])     # negative indexes are safe as long as the list isn't empty
print(short[0:10])   # slices never raise, they just stop at the end
# print(short[9])   # remove the # and Run: a plain index past the end raises IndexError
