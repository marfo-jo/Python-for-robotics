# Text from a sentence is always a str. Converting it is YOUR job.
print(int("08"))               # leading zeros are fine
print(float("545.4"))          # text with a decimal point needs float()
print(float("4807.038") + 1)   # now it's a number, so math works

print(int(4807.038))           # int() of a float CHOPS the decimals off
print(int(-3.7))               # it chops toward zero, so -3, not -4
print(round(3.7), round(-3.7)) # round() goes to the NEAREST whole number
print(round(0.5), round(1.5), round(2.5))  # exact ties go to the EVEN number
print(round(48.1173004, 6))    # round to 6 decimal places (still a float)

# Floats are stored in binary, so most decimals are not exact:
minutes = 4807.038 - 4800
print(minutes)                 # not exactly 7.038
print(f"{minutes:.4f}")        # formatting hides the tiny error when printing
print(minutes == 7.038)        # never compare floats with == ...
print(abs(minutes - 7.038) < 1e-9)   # ... compare with a tolerance instead
