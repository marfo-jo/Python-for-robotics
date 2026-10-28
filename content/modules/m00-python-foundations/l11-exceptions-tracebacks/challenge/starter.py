# parse_gga(sentence) -> dict, or raise ValueError with YOUR OWN message:
#   "not an NMEA sentence"  no '$' at the start, or no '*'
#   "checksum mismatch"     the checksum doesn't match
#   "not a GGA sentence"    a valid sentence of another type (RMC, GSV, ...)
#   "too few fields"        a field you need doesn't exist (an IndexError inside)
#   "no fix"                fix quality is 0 (check this BEFORE converting the
#                           other numbers: a no-fix sentence has empty fields)
# Numbers that won't convert may raise Python's own ValueError; that's fine.
#
# parse_fixes(lines) -> (fixes, errors): skip blank lines, parse the rest,
#   catch ValueError ONLY, and record (line_number, message), counting from 1.


def checksum_ok(sentence):
    # Paste in your checksum_ok from lesson 0.10 (or write it again).
    return True


def parse_gga(sentence):
    return {}


def parse_fixes(lines):
    return [], []


# Try it with Run before you Submit:
print(parse_gga("$GPGGA,153012.00,4220.0101,N,07105.6600,W,1,09,0.9,10.2,M,-33.1,M,,*62"))
print(parse_fixes(["$GPGGA,153015.00,,,,,0,00,99.9,,M,,M,,*5C", "", "garbage"]))
