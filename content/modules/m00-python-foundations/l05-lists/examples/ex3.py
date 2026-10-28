# A rolling window: keep only the newest N altitude readings,
# like a shift register that drops the oldest bit.
readings = [12.3, 13.0, 12.8, 12.9, 13.1]
N = 3

window = []
for alt in readings:
    window.append(alt)       # newest goes on the END
    if len(window) > N:
        window.pop(0)        # oldest is at index 0: drop it
    print(window)

print("newest:", window[-1])
print("oldest kept:", window[0])

saved = window               # NOT a copy: a second name for the SAME list
copy = window[:]             # a full slice builds a NEW list
window.append(99.9)          # change the list through one name...
print(saved)                 # ...and the other name sees it
print(copy)                  # the real copy is unaffected
print(saved is window, copy is window)
