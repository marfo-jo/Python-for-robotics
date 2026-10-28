# Why immutability helps: a "home" waypoint that nothing can corrupt by accident.

def nudge_north_list(point):
    point[0] = point[0] + 0.001    # writes into the CALLER's list
    return point


def nudge_north_tuple(point):
    lat, lon = point
    return (lat + 0.001, lon)      # builds a NEW tuple; can't touch the old one


home_list = [42.3372, -71.0928]
target = nudge_north_list(home_list)
print("target:", target)
print("home:  ", home_list)        # home moved too! (aliasing, lesson 0.5)

home = (42.3372, -71.0928)
target = nudge_north_tuple(home)
print("target:", target)
print("home:  ", home)             # home is exactly what it was

# Same data, different jobs:
satellites_seen = [9, 3, 7]        # LIST: a growing collection of the same kind of thing
satellites_seen.append(8)
fix = ("152305.00", 42.33539, -71.09280)   # TUPLE: one record, fixed slots, each with a meaning
print(satellites_seen, fix)
