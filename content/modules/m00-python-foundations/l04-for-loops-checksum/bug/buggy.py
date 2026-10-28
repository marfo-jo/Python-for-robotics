# Build a command to SEND to a GPS module, for example the PMTK command that
# sets the update rate on MediaTek-based GPS modules (common on Arduino breakouts):
#   with_checksum("PMTK220,1000")  should give  "$PMTK220,1000*1F\r\n"
# The module silently ignores any command whose checksum is wrong.

def with_checksum(body):
    sentence = "$" + body
    total = 0
    for ch in sentence:
        total = total ^ ord(ch)
    return sentence + "*" + format(total, "02X") + "\r\n"


print(repr(with_checksum("PMTK220,1000")))
