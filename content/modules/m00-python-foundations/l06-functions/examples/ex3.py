minimum = 4          # a GLOBAL name, defined at the top level of the file


def enough_satellites(count, minimum=4):
    """True if a fix used at least `minimum` satellites (4 by default)."""
    ok = count >= minimum     # `ok` and this `minimum` are LOCAL to the call
    return ok


print(enough_satellites(9))                   # minimum uses its default, 4
print(enough_satellites(3))
print(enough_satellites(3, 3))                # positional: 3 -> count, 3 -> minimum
print(enough_satellites(count=5, minimum=6))  # keyword arguments, by name


def lower_threshold():
    minimum = 0        # this makes a NEW local name; the global is untouched
    return minimum


print(lower_threshold())
print(minimum)         # still 4
