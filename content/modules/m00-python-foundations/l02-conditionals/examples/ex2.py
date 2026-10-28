# A receiver with no fix: almost every field is empty.
line = "$GPGGA,,,,,,0,,,,,,,,*66\r\n".strip()
fields = line.split(",")
quality = fields[6]
sats = fields[7]

print(repr(quality), repr(sats))
print(bool(quality), bool(sats))   # empty string -> False, anything else -> True
print(bool("0"))                   # careful: "0" is NOT empty, so it is True!

if sats:                           # "if the field has something in it"
    print("satellites:", int(sats))
else:
    print("satellite field is empty")

if quality == "0":                 # compare the TEXT "0", not the number 0
    print("receiver says: no fix")
