sentence = "$GPGGA,123519,4807.038,N,01131.000,E,1,08,0.9,545.4,M,46.9,M,,*47"

print(len(sentence))      # how many characters in total
print(sentence[0])        # first character (index 0)
print(sentence[1:6])      # indexes 1, 2, 3, 4, 5 (stops BEFORE 6)
print(sentence[7:13])     # the UTC time field
print(sentence[-2:])      # the last two characters
print(sentence[:6] + "!") # slices are new strings you can combine
