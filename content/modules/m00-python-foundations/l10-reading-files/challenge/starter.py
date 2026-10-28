# load_sentences(path): read a GPS log file and return (sentences, errors).
#   sentences: a list of the valid NMEA sentences, stripped, in file order
#   errors:    how many NON-BLANK lines were rejected (junk, bad checksum, truncated)
# Blank lines are skipped and are not errors.


def checksum_ok(sentence):
    # Optional helper. You wrote this in lesson 0.4: try it again from memory.
    # True if sentence starts with '$', has a '*', and the two hex digits after
    # the '*' match the XOR of every character between '$' and '*'.
    return False


def load_sentences(path):
    return [], 0


# Try it with Run: this makes a small test log, then loads it.
with open("try_log.txt", "w", encoding="utf-8") as f:
    f.write("$GPGGA,153012.00,4220.0101,N,07105.6600,W,1,09,0.9,10.2,M,-33.1,M,,*62\n")
    f.write("\n")
    f.write("u-blox NEO-M8N ROM 2.01\n")
    f.write("$GPGGA,153013.00,4220.01")

print(load_sentences("try_log.txt"))    # expect one sentence and 1 error
