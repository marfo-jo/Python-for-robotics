# Sentence dispatcher for the GPS logger: send each line to the handler for
# its type. Unknown types are ignored (None).

def handle_gga(fields):
    """Summarize a GGA fix."""
    return {"type": "GGA", "satellites": int(fields[7])}


def handle_rmc(fields):
    """Summarize an RMC fix."""
    return {"type": "RMC", "status": fields[2]}


HANDLERS = {"gga": handle_gga, "rmc": handle_rmc}


def handle(sentence):
    """Dispatch one NMEA sentence to its handler; return None for unknown types."""
    fields = sentence.strip().split(",")
    kind = fields[0][3:6]
    handler = HANDLERS.get(kind)
    if handler is None:
        return None
    return handler(fields)


print(handle("$GPGGA,152305.00,4220.1234,N,07105.5678,W,1,09,1.1,12.3,M,-33.1,M,,*64"))
print(handle("$GPRMC,152305.00,A,4220.1234,N,07105.5678,W,0.05,87.30,281026,,,A*75"))
