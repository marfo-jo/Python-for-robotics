def parse_alt(sentence):
    """$GPGGA sentence -> altitude in meters. Raises ValueError on bad input."""
    sentence = sentence.strip()
    if not sentence.startswith("$") or "*" not in sentence:
        raise ValueError("not an NMEA sentence")
    fields = sentence.split(",")
    try:
        text = fields[9]
    except IndexError:
        raise ValueError(f"too few fields ({len(fields)})")
    if text == "":
        raise ValueError("altitude field is empty (no fix)")
    return float(text)


log = [
    "$GPGGA,153012.00,4220.0101,N,07105.6600,W,1,09,0.9,10.2,M,-33.1,M,,*62\r\n",
    "u-blox NEO-M8N ROM 2.01",
    "$GPGGA,153013.00,4220.0105,N,07105.6592,W,1,09,0.9,10.4,M,-33.1,M,,*69",
    "$GPGGA,153015.00,,,,,0,00,99.9,,M,,M,,*5C",
    "$GPGGA,153012.00,4220.0101,N*34",
]

alts = []
checked = 0
for number, line in enumerate(log, start=1):
    try:
        alt = parse_alt(line)
    except ValueError as err:
        print(f"line {number}: skipped ({err})")
    else:
        alts.append(alt)            # only when parse_alt succeeded
    finally:
        checked += 1                # ALWAYS runs, error or not

print(f"checked {checked}, kept {len(alts)}, mean altitude {sum(alts) / len(alts):.2f} m")
