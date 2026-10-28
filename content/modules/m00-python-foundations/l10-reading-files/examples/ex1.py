# Part 1: make a small log file to practice on. (Writing is covered at the end
# of the lesson. For now, just notice that it also uses `with open(...)`.)
with open("gps_log.txt", "w", encoding="utf-8") as f:
    f.write("$GPGGA,153012.00,4220.0101,N,07105.6600,W,1,09,0.9,10.2,M,-33.1,M,,*62\n")
    f.write("$GPGGA,153013.00,4220.0105,N,07105.6592,W,1,09,0.9,10.4,M,-33.1,M,,*69\n")
    f.write("$GPGGA,153014.00,4220.0110,N,07105.6584,W,1,10,0.8,10.5,M,-33.1,M,,*65")

# Part 2: read it back, one line at a time.
with open("gps_log.txt", encoding="utf-8") as f:
    for line in f:
        print(len(line), repr(line[-5:]))   # repr() shows the invisible '\n'

print(f.closed)    # the with-block closed the file for you
