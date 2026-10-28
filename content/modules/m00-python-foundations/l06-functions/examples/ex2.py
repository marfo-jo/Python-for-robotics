GGA = "$GPGGA,152305.00,4220.1234,N,07105.5678,W,1,09,1.1,12.3,M,-33.1,M,,*64"


def sats_print(sentence):
    fields = sentence.strip().split(",")
    print(int(fields[7]))      # puts it on the SCREEN, and that's all


def sats_return(sentence):
    fields = sentence.strip().split(",")
    return int(fields[7])      # hands the value BACK to the caller


a = sats_print(GGA)            # the 9 you see comes from print inside the function
b = sats_return(GGA)           # nothing is shown, but b now holds 9

print("a =", a)
print("b =", b)
print(b >= 4)
print(a is None)
# print(a >= 4)   # remove the # and Run: TypeError, because a is None
