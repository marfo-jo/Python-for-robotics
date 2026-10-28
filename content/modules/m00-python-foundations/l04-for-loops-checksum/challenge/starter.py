# Fill in the body of each function. Use a for loop, ord(), ^, and format().
# (Functions are covered properly in lesson 0.6. For now: the input arrives in
# the parameters, and `return` hands back the answer.)


def xor_checksum(body):
    # body is the text BETWEEN '$' and '*', for example "GPVTG,309.62,T,,M,0.13,N,0.2,K,A".
    # Return the XOR of all its characters as exactly 2 uppercase hex digits,
    # for example "03" (not "3", not "0x3").
    return "??"    # replace this with your loop


def checksum_ok(sentence):
    # True if the sentence's checksum matches its contents, otherwise False.
    # The sentence may have whitespace or "\r\n" around it and lowercase hex.
    # A sentence with no '$' at the start or no '*' is not valid: return False
    # (never crash).
    return False


# Try your functions with Run before you Submit:
print(xor_checksum("GPGGA,123519,4807.038,N,01131.000,E,1,08,0.9,545.4,M,46.9,M,,"))
print(checksum_ok("$GPGGA,123519,4807.038,N,01131.000,E,1,08,0.9,545.4,M,46.9,M,,*47\r\n"))
print(checksum_ok("$GPGGA,123519,4807.039,N,01131.000,E,1,08,0.9,545.4,M,46.9,M,,*47"))
