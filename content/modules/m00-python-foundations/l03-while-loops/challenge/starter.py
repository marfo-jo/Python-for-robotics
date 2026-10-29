# Fill in the body of each function with a while loop.
# (Functions are covered properly in lesson 0.6. For now: the input arrives in
# the parameters, and `return` hands back the answer and ends the function.)
# Every loop you write must END: check your progress step and your limits.


def first_fix(lines, max_tries):
    # lines is the list of raw lines from the serial port, in arrival order.
    # Read them one at a time from index 0, at most max_tries reads (and never
    # past the end of the list). Return the first line (stripped) that is a GGA
    # sentence with a real fix: at least 7 fields, quality field (index 6) not empty and
    # not "0". If none arrives in time, return "".
    return "?"     # replace this with your loop


def settled_index(readings, threshold, needed):
    # Return the index of the reading where the sensor has been BELOW threshold
    # for `needed` readings in a row (needed is 1 or more). A reading at or
    # above the threshold resets the run. If it never settles, return -1.
    return -2      # replace this with your loop


# Try your functions with Run before you Submit:
log = ["", "$GPGGA,,,,,,0,,,,,,,,*66", "$GPGGA,142208.00,4220.1155,N,07105.4886,W,1,04,2.1,13.0,M,-33.1,M,,*6F\r\n"]
print(first_fix(log, 5))
print(settled_index([5.0, 3.2, 0.9, 0.4, 0.3, 0.2], 1.0, 3))
