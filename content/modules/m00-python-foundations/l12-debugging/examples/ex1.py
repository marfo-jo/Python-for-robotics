sats_text = "8"      # what split(",") gives you: text
sats = 8             # what int() gives you: a number

print(sats_text, sats)               # they LOOK identical
print(repr(sats_text), repr(sats))   # repr() shows what they really are
print(sats_text == sats)             # so this is False, and print() never told you why
print(type(sats_text).__name__, type(sats).__name__)

# Invisible characters: print() hides them, repr() shows them.
tail = "$GPGGA,,,,,,0,,,,,,,,*66\r\n"[-4:]
print("[" + tail.strip() + "]")
print(repr(tail))
print(repr(""), repr(" "), repr("\t"))   # empty, space, tab: all invisible in print()

# Floats: print() and repr() show the full stored value; format to see it rounded.
x = 0.1 + 0.2
print(repr(x), f"{x:.2f}", x == 0.3)
