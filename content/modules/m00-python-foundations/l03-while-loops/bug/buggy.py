# Gyro bias calibration at startup.
# While the robot sits still, a perfect gyro would read 0.0 rad/s. A real one
# reads a small constant offset (the bias). Average the FIRST n samples to
# estimate it, so the rest of the code can subtract it from every reading.

def gyro_bias(samples, n):
    total = 0.0
    i = 1
    while i <= n:
        total += samples[i]
        i += 1
    return total / n


print(gyro_bias([0.021, 0.019, 0.020, 0.020, 0.250], 4))
