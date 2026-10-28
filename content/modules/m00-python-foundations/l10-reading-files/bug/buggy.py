# Summarizes a GPS log for the Lab 4 report: how many non-blank lines the
# file has, and how many of those are GGA fix sentences.

def log_summary(path):
    with open(path, encoding="utf-8") as f:
        total = 0
        for line in f:
            if line.strip() != "":
                total += 1

        gga = 0
        for line in f:
            if line.strip()[3:6] == "GGA":
                gga += 1
    return total, gga


with open("lab4_log.txt", "w", encoding="utf-8") as f:
    f.write("$GPGGA,153012.00,4220.0101,N,07105.6600,W,1,09,0.9,10.2,M,-33.1,M,,*62\n")
    f.write("$GPRMC,153012.00,A,4220.0101,N,07105.6600,W,0.52,54.70,281026,,,A*71\n")
    f.write("$GPGGA,153013.00,4220.0105,N,07105.6592,W,1,09,0.9,10.4,M,-33.1,M,,*69\n")

total, gga = log_summary("lab4_log.txt")
print(f"lines: {total}, GGA fixes: {gga}")
