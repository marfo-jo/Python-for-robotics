sats = 8
hdop = 0.9
alt = 545.4
talker = "GP"

print("sats: " + str(sats))        # the old way: convert to text, then glue
print(f"sats: {sats}")              # f-string: Python fills in {sats} for you
print(f"{talker}GGA: {sats} satellites, HDOP {hdop}")
print(f"altitude {alt:.2f} m")      # .2f = fixed point, exactly 2 decimals
print(f"altitude {alt:.0f} m")      # .0f = no decimals (it rounds)
print(f"[{sats:4d}]")               # width 4, numbers line up on the right
print(f"[{sats:02d}]")              # width 2, zero-padded, like NMEA's "08"
print(f"[{talker:<4}]")             # text, left-aligned in width 4
print(f"[{alt:8.2f}]")              # width 8 counts EVERY character: "545.40" is 6
print(f"{-3.5:+.1f} {3.5:+.1f}")    # + always shows the sign
print(f"{alt:.1f} m = {alt * 3.28084:.1f} ft")   # any expression works inside {}
