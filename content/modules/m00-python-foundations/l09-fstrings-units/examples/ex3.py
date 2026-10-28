sentence = "$GPGGA,153012.00,4220.0101,N,07105.6600,W,1,09,0.9,10.2,M,-33.1,M,,*62"
fields = sentence.split(",")
lat_text, lat_hemi = fields[2], fields[3]    # '4220.0101', 'N'
lon_text, lon_hemi = fields[4], fields[5]    # '07105.6600', 'W'

# Latitude is ddmm.mmmm: 2 digits of degrees, then minutes.
lat_deg = int(lat_text[:2])
lat_min = float(lat_text[2:])
lat = lat_deg + lat_min / 60       # 60 minutes in a degree
if lat_hemi == "S":
    lat = -lat                     # south of the equator is negative

# Longitude is dddmm.mmmm: 3 digits of degrees.
lon_deg = int(lon_text[:3])
lon_min = float(lon_text[3:])
lon = lon_deg + lon_min / 60
if lon_hemi == "W":
    lon = -lon                     # west of Greenwich is negative

print(lat_deg, lat_min)
print(lon_deg, lon_min)
print(f"lat = {lat:.6f}°  lon = {lon:.6f}°")
print(f"{abs(lat):.6f}°{lat_hemi}, {abs(lon):.6f}°{lon_hemi}")

# The classic units mistake: reading ddmm.mmmm as if it were decimal degrees.
wrong = float(lat_text) / 100
print(f"wrong: {wrong:.6f}°, off by {abs(wrong - lat) * 111320 / 1000:.1f} km")
