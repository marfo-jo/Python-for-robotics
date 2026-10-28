# Battery monitor for a 3S LiPo pack (nominal 11.1 V).
#   volts >= 11.1         -> "OK"
#   10.5 <= volts < 11.1  -> "LOW"       (warn the operator)
#   volts < 10.5          -> "CRITICAL"  (return to dock NOW, before the cells are damaged)

def battery_state(volts):
    if volts < 11.1:
        return "LOW"
    elif volts < 10.5:
        return "CRITICAL"
    else:
        return "OK"


print(battery_state(12.3))
print(battery_state(10.9))
print(battery_state(9.8))
