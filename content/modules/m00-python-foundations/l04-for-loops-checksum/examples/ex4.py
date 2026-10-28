# Three lines off the serial port. One is clean, one had a digit corrupted
# in transit ('3' became '8'), and one had two characters swapped.
received = [
    "$GPVTG,309.62,T,,M,0.13,N,0.2,K,A*03",
    "$GPVTG,309.62,T,,M,0.18,N,0.2,K,A*03",
    "$GPVTG,309.62,T,,M,0.31,N,0.2,K,A*03",
]

for line in received:
    star = line.find("*")
    total = 0
    for i in range(1, star):           # indexes 1 .. star-1: skips '$' and '*'
        total ^= ord(line[i])
    computed = format(total, "02X")
    if computed == line[star + 1:]:
        print("speed", line[19:23], "OK", computed)
    else:
        print("speed", line[19:23], "CORRUPT", computed, "!=", line[star + 1:])

# Why the swap slipped through: XOR doesn't care about ORDER.
print(ord("1") ^ ord("3"), ord("3") ^ ord("1"))
# And why the corruption was caught: '3' and '8' differ in 3 bits.
print(format(ord("3"), "08b"), format(ord("8"), "08b"))
