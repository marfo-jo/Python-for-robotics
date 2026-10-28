# What a serial read really gives you: the sentence PLUS "\r\n" on the end.
raw = "$GPGGA,123519,4807.038,N,01131.000,E,1,08,0.9,545.4,M,46.9,M,,*47\r\n"

print(len(raw))           # 2 more than the visible text
print(repr(raw[-2:]))     # repr() shows invisible characters
print(repr(raw[-4:-2]))   # the checksum is hiding just before them

line = raw.strip()        # a NEW string with whitespace removed from both ends
print(len(line))
print(line[-2:])

fields = line.split(",")
print(fields[2], fields[3])   # latitude and its hemisphere
print(repr(fields[13]))       # an empty field: two commas in a row
