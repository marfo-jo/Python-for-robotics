fix = ("123519", 48.1173, 11.5167)   # (time, lat, lon): a fixed-size record

print(type(fix).__name__)
print(len(fix))
print(fix[0], fix[1])        # indexing works exactly like a list
print(fix[-1])
print(fix[1:])               # a slice of a tuple is a tuple

time, lat, lon = fix         # UNPACKING: one name per slot, in order
print(lat)
print(lon)

pair = 48.1173, 11.5167      # the COMMAS make a tuple; parentheses are optional
print(pair)

one = (8,)                   # a one-item tuple needs a trailing comma
just_eight = (8)             # this is just the number 8 in parentheses
print(type(one).__name__, type(just_eight).__name__)

# fix[1] = 0.0   # remove the # and Run: TypeError, a tuple can't be changed
