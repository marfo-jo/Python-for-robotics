with open("short_log.txt", "w", encoding="utf-8") as f:
    f.write("$GPGGA,153012.00,4220.0101,N,07105.6600,W,1,09,0.9,10.2,M,-33.1,M,,*62\n")
    f.write("\n")
    f.write("   \n")
    f.write("$GPRMC,153012.00,A,4220.0101,N,07105.6600,W,0.52,54.70,281026,,,A*71\n")

# Three ways to read. Each one opens the file fresh.
with open("short_log.txt", encoding="utf-8") as f:
    text = f.read()            # the whole file as ONE string
print(len(text), repr(text[-4:]))

with open("short_log.txt", encoding="utf-8") as f:
    lines = f.readlines()      # a list of lines, each still ending in '\n'
print(len(lines), repr(lines[1]), repr(lines[2]))

# The usual way: loop over the file, strip each line, skip the blank ones.
sentences = 0
blank = 0
with open("short_log.txt", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if line == "":
            blank += 1
            continue           # skip to the next line
        sentences += 1
        print(line[:6], len(line))
print(f"{sentences} sentences, {blank} blank lines")
