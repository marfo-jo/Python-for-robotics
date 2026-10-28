line = "$GPGGA,153012.00,4220.0101,N,07105.6600,W,1,09,0.9,10.2,M,-33.1,M,,*62\r\n"
fields = line.split(",")
sats = fields[7]
alt = float(fields[9])

# f"{expr=}" prints the expression, an equals sign, and repr() of its value.
print(f"{sats=}")
print(f"{alt=}")
print(f"{len(fields)=}")
print(f"{fields[-1]=}")            # the \r\n hiding in the last field
print(f"{sats == 9=}")             # comparisons work too: shows WHY a check fails
print(f"{alt * 3.28084=:.1f}")     # a format spec goes after the =
print(f"stage 2: {sats=} {alt=}")  # mix in a label so you know which print is which
