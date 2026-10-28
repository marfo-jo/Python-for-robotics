def sentence_type(sentence):
    """Return the 3-letter type of an NMEA sentence, like 'GGA'."""
    clean = sentence.strip()
    return clean[3:6]


# `sentence` above is the PARAMETER (the input terminal).
# The text we pass in below is the ARGUMENT (the signal on that terminal).
kind = sentence_type("$GPGGA,123519,4807.038,N,01131.000,E,1,08,0.9,545.4,M,46.9,M,,*47")
print(kind)

# One definition, reused on any input: that's the point of a function.
print(sentence_type("  $GNRMC,220516,A,4221.123,N,07105.456,W,0.13,309.62,281026,,,A*7C\r\n"))
print(sentence_type("$GPVTG,309.62,T,,M,0.13,N,0.2,K,A*03") == "VTG")

# The docstring is the datasheet for the block.
print(sentence_type.__doc__)
