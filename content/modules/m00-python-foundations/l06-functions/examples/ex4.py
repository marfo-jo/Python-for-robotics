# Small blocks that compose: type check -> extract -> decide.
# Same idea as wiring a comparator into a latch into an LED driver.

def sentence_type(sentence):
    """Return the 3-letter type, like 'RMC'."""
    return sentence.strip()[3:6]


def rmc_status(sentence):
    """Return the RMC status letter ('A' = active, 'V' = void), or None if not RMC."""
    if sentence_type(sentence) != "RMC":
        return None                  # a function can return early
    fields = sentence.strip().split(",")
    if len(fields) < 3:
        return None                  # cut off before the status field
    return fields[2]


def usable(sentence):
    """True only for an RMC sentence whose status is 'A'."""
    return rmc_status(sentence) == "A"


log = [
    "$GPRMC,152304.00,V,,,,,,,281026,,,N*73",
    "$GPRMC,152305.00,A,4220.1234,N,07105.5678,W,0.05,87.30,281026,,,A*75",
    "$GPGGA,152305.00,4220.1234,N,07105.5678,W,1,09,1.1,12.3,M,-33.1,M,,*64",
    "$GPRMC,1523",
]

for line in log:
    print(sentence_type(line), rmc_status(line), usable(line))
