# A for loop visits every item in order. No index, no counter, no way to forget i += 1.
for ch in "GPVTG":
    print(ch, ord(ch))       # ord() gives the character's code number (ASCII)

# range(stop): 0, 1, ..., stop - 1 (half-open, like slicing)
for scan in range(3):
    print("scan", scan)

# range(start, stop, step)
for i in range(1, 10, 4):
    print("i =", i)

# Counting down: a negative step, and the stop is still excluded
for t in range(6, 0, -2):
    print("t =", t)

# Indexes and characters together: range(len(s))
tag = "$GP"
for i in range(len(tag)):
    print(i, tag[i])
