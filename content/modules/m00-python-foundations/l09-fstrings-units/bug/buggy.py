# Converts a $GPGGA sentence to (lat, lon) in signed decimal degrees,
# so the GPS track can be plotted on top of the wheel-odometry track.

def gga_to_latlon(sentence):
    fields = sentence.strip().split(",")
    lat_text, lat_hemi = fields[2], fields[3]
    lon_text, lon_hemi = fields[4], fields[5]

    lat = float(lat_text[:2]) + float(lat_text[2:]) / 100
    lon = float(lon_text[:3]) + float(lon_text[3:]) / 100

    if lat_hemi == "S":
        lat = -lat
    if lon_hemi == "W":
        lon = -lon
    return lat, lon


lat, lon = gga_to_latlon("$GPGGA,153012.00,4221.5730,N,07105.6600,W,1,09,0.9,10.2,M,-33.1,M,,*62")
print(f"{lat:.6f}, {lon:.6f}")
