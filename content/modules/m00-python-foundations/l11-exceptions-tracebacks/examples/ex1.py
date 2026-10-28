# Satellite-count fields as they really arrive from receivers.
for text in ["08", "", "x9", " 12 ", "7.0"]:
    try:
        sats = int(text)             # might raise ValueError
        print(f"{text!r:7} -> {sats}")
    except ValueError:
        print(f"{text!r:7} -> not a whole number, skipped")

print("the loop finished: one bad field didn't stop the program")
