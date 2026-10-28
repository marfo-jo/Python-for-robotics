# Comparisons produce booleans: True or False.
sats = 8
print(sats > 4)              # greater than
print(sats == 8, sats != 8)  # == asks "equal?"  (a single = stores a value)

print("8" == 8)              # text vs number: NEVER equal, and no error either
print(int("08") == 8)        # convert the text first, then compare

volts = 11.1
print(10.5 <= volts < 11.1)  # a comparison chain: both halves must be True
print(volts >= 11.1 and sats >= 4)
print(not sats > 4)          # not flips True <-> False
