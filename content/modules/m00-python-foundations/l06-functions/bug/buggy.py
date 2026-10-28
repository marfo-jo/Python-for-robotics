# Fix filter for the GPS logger: reject fixes that used too few satellites.

def satellites(sentence):
    """Return the number of satellites (field 7) in a GGA sentence, as an int."""
    fields = sentence.strip().split(",")
    print(int(fields[7]))


def good_enough(sentence, minimum=4):
    """True if the fix used at least `minimum` satellites."""
    return satellites(sentence) >= minimum


n = satellites("$GPGGA,152305.00,4220.1234,N,07105.5678,W,1,09,1.1,12.3,M,-33.1,M,,*64")
print("n is", n)
