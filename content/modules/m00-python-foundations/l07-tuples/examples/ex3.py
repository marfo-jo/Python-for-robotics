# A track is a LIST (it grows) of TUPLES (each record has a fixed shape).
track = [
    ("152305.00", 42.33539, -71.09280),
    ("152306.00", 42.33540, -71.09282),
    ("152307.00", 42.33542, -71.09284),
]
track.append(("152308.00", 42.33544, -71.09286))   # add a whole record
print(len(track), "records")

# Unpack each record right in the for line.
for time, lat, lon in track:
    print(time, lat, lon)

# Track the northernmost point (largest latitude).
best_time, best_lat, best_lon = track[0]
for time, lat, lon in track:
    if lat > best_lat:
        best_time, best_lat, best_lon = time, lat, lon
print("northernmost:", best_time, best_lat)

# enumerate gives (i, record), and the record itself unpacks in parentheses.
for i, (time, lat, lon) in enumerate(track):
    if i == len(track) - 1:
        print("last fix is record", i, "at", time)

# You can't edit a record in place...
# track[0][1] = 0.0    # remove the # and Run: TypeError
# ...but you can REPLACE the whole record in the list, which is mutable.
time, lat, lon = track[0]
track[0] = (time, lat, lon + 0.00001)
print(track[0])
