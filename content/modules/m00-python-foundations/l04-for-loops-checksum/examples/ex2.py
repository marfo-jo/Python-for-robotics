# XOR (^) works on whole numbers bit by bit: 1 where the bits differ.
print(5 ^ 3)                                 # 0101 ^ 0011 = 0110
print(format(5, "04b"), format(3, "04b"), format(5 ^ 3, "04b"))

# Characters are numbers underneath. 'G' is 71, 'P' is 80.
g = ord("G")
p = ord("P")
print(g, format(g, "08b"))
print(p, format(p, "08b"))
x = g ^ p
print(x, format(x, "08b"))

print(x ^ p == g)        # XOR the same value twice and it cancels out
print(g ^ g)             # anything XOR itself is 0
print(g ^ 0)             # anything XOR 0 is itself: so start the checksum at 0

# Showing a number as hex, the way NMEA writes the checksum
print(hex(23), format(23, "02X"), format(3, "02X"))
print(int("7c", 16), int("7C", 16))   # hex text back to a number (base 16)
