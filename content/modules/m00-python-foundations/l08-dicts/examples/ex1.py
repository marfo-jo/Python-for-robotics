fix = {"time": "152305.00", "quality": 1, "satellites": 9}   # key: value pairs

print(fix["satellites"])      # look up by NAME, not by position
fix["hdop"] = 1.1             # assigning to a new key ADDS it
fix["satellites"] = 10        # assigning to an existing key OVERWRITES it
print(fix)
print(len(fix))               # number of key: value pairs

print("hdop" in fix, "altitude" in fix, 10 in fix)   # `in` checks KEYS only

print(fix.get("altitude"))         # missing key: None, no crash
print(fix.get("altitude", 0.0))    # missing key: your default instead
print(fix.get("hdop", 0.0))        # present key: the real value

# print(fix["altitude"])   # remove the # and Run: KeyError, the key doesn't exist
