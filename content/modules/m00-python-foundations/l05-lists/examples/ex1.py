line = "$GPGGA,123519,4807.038,N,01131.000,E,1,08,0.9,545.4,M,46.9,M,,*47"
fields = line.split(",")      # split() hands you a LIST of strings

print(type(fields).__name__)  # what kind of object is it?
print(len(fields))            # how many items
print(fields[0], fields[7])   # index 0 is '$GPGGA'; index 7 is satellites
print(fields[-1])             # the last item (the checksum is glued to it)
print(fields[2:6])            # a slice of a list is a new list
print(len(fields) - 1)        # the LAST valid index is len - 1, not len
print("M" in fields, "GGA" in fields)   # `in` checks whole items, not text inside them
