# Battery bands for a 3S LiPo pack (nominal 11.1 V).
volts = 10.9
if volts >= 11.1:
    level = "OK"
elif volts >= 10.5:      # we only get here if volts < 11.1
    level = "LOW"
else:
    level = "CRITICAL"
print(volts, level)

# Hysteresis, like a Schmitt trigger: start docking below 10.5 V,
# but don't stop docking until the pack recovers ABOVE 11.4 V.
docking = True           # the robot is already heading to the dock
volts = 11.2             # voltage bounced back up a little under lighter load
if docking and volts > 11.4:
    docking = False
elif not docking and volts < 10.5:
    docking = True
print("docking:", docking)

volts = 11.6             # now it has really recovered
if docking and volts > 11.4:
    docking = False
elif not docking and volts < 10.5:
    docking = True
print("docking:", docking)
