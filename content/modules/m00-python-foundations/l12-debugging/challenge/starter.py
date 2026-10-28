# GPS track length for the Lab 4 report: how far did the robot drive?
#
#   lines --stage 1--> GGA fix sentences --stage 2--> (lat, lon) in degrees
#         --stage 3--> (x, y) in meters from the first fix --stage 4--> total meters
#
# This pipeline has THREE planted bugs, in three different stages. Nothing crashes
# on the demo log below, but the answer is wrong. Debug it like a technician:
# reproduce, isolate the stage (the hidden test names say which stage they probe),
# hypothesize, test, fix, verify. Fix the bugs; don't rewrite the design.
import math

EARTH_RADIUS_M = 6371000.0


def gga_fixes(lines):
    """Stage 1: keep stripped GGA sentences that have a fix (quality is not '0')."""
    good = []
    for line in lines:
        line = line.strip()
        if line == "":
            continue
        fields = line.split(",")
        if fields[0][3:6] != "GGA":
            continue
        if fields[6] == 0:
            continue
        good.append(line)
    return good


def parse_latlon(sentence):
    """Stage 2: GGA sentence -> (lat, lon) in signed decimal degrees."""
    fields = sentence.split(",")
    lat = int(fields[2][:2]) + float(fields[2][2:]) / 60
    lon = int(fields[4][:3]) + float(fields[4][3:]) / 60
    if fields[3] == "S":
        lat = -lat
    if fields[5] == "W":
        lon = -lon
    return lat, lon


def to_local_xy(lat, lon, lat0, lon0):
    """Stage 3: meters east (x) and north (y) of the origin (lat0, lon0)."""
    x = math.radians(lon - lon0) * EARTH_RADIUS_M * math.cos(lat0)
    y = math.radians(lat - lat0) * EARTH_RADIUS_M
    return x, y


def path_length(points):
    """Stage 4: total length in meters of the path through a list of (x, y) points."""
    total = 0.0
    for i in range(1, len(points) - 1):
        x0, y0 = points[i - 1]
        x1, y1 = points[i]
        total += math.sqrt((x1 - x0) ** 2 + (y1 - y0) ** 2)
    return total


def track_length(lines):
    """The whole pipeline: log lines -> meters driven."""
    sentences = gga_fixes(lines)
    if len(sentences) == 0:
        return 0.0
    latlons = []
    for s in sentences:
        latlons.append(parse_latlon(s))
    lat0, lon0 = latlons[0]
    points = []
    for lat, lon in latlons:
        points.append(to_local_xy(lat, lon, lat0, lon0))
    return path_length(points)


# Reproduce: the robot drove 37 m north, then 41 m east (about 78 m in total).
log = [
    "$GPGGA,153020.00,4220.0200,N,07105.6400,W,1,09,0.9,10.3,M,-33.1,M,,*62",
    "$GPGGA,153040.00,4220.0400,N,07105.6400,W,1,09,0.9,10.3,M,-33.1,M,,*62",
    "$GPGGA,153100.00,4220.0400,N,07105.6100,W,1,10,0.8,10.4,M,-33.1,M,,*6C",
]
print(f"{track_length(log)=:.1f} m")
