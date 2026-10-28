# Dispatch: a dict that maps a sentence type to the function that handles it.
# Like a PLC jump table: the opcode picks which routine runs.

def handle_gga(fields):
    return "fix quality " + fields[6] + " with " + fields[7] + " satellites"


def handle_rmc(fields):
    return "status " + fields[2]


HANDLERS = {"GGA": handle_gga, "RMC": handle_rmc}   # no () : the functions themselves

log = [
    "$GPGGA,152305.00,4220.1234,N,07105.5678,W,1,09,1.1,12.3,M,-33.1,M,,*64",
    "$GPRMC,152304.00,V,,,,,,,281026,,,N*73",
    "$GPVTG,309.62,T,,M,0.13,N,0.2,K,A*03",
]

for line in log:
    fields = line.strip().split(",")
    kind = fields[0][3:6]
    handler = HANDLERS.get(kind)          # a function, or None if we don't know this type
    if handler is None:
        print(kind, "-> ignored")
    else:
        print(kind, "->", handler(fields))   # NOW call it, with ()

print(HANDLERS["GGA"] is handle_gga)
