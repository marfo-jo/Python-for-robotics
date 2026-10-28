import math

M_PER_DEG_LAT = 111320          # about 40,075 km around the Earth / 360 degrees
lat = 42.34                     # Boston
m_per_deg_lon = M_PER_DEG_LAT * math.cos(math.radians(lat))   # meridians converge
print(f"1° of longitude at {lat}°N is {m_per_deg_lon:,.0f} m")
print()
print(f"{'places':>6} | {'step (deg)':>10} | {'north-south':>11} | {'east-west':>11}")
for places in range(1, 8):
    step = 10 ** -places        # 0.1, 0.01, ... the smallest change you can show
    ns = step * M_PER_DEG_LAT
    ew = step * m_per_deg_lon
    print(f"{places:>6} | {step:>10.7f} | {ns:>9.3f} m | {ew:>9.3f} m")
