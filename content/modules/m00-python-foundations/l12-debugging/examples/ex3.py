# A 4-stage pipeline: RMC sentence -> ground speed in m/s.
# Symptom: the robot (top speed 3 m/s) reports 9.63 m/s. Where does it go wrong?

def clean(raw):
    return raw.strip()                      # stage 1

def speed_field(sentence):
    return sentence.split(",")[7]           # stage 2: speed over ground, in knots

def to_number(text):
    return float(text)                      # stage 3

def knots_to_mps(knots):
    return knots * 1.852                    # stage 4: 1 knot = 1852 m per HOUR


raw = "$GPRMC,153020.00,A,4220.0301,N,07105.6100,W,5.20,54.70,281026,,,A*75\r\n"

# Probe each stage's output and compare it with what you EXPECT.
s1 = clean(raw)
s2 = speed_field(s1)
s3 = to_number(s2)
s4 = knots_to_mps(s3)
print(f"stage 1: {s1[-4:]=}   expect 'A*75', no \\r\\n")
print(f"stage 2: {s2=}   expect '5.20'")
print(f"stage 3: {s3=}   expect 5.2")
print(f"stage 4: {s4=:.3f}   expect about 2.7 m/s")
# Stages 1-3 are right, stage 4 is wrong: the bug is INSIDE knots_to_mps.
# Hypothesis: 1.852 converts knots to km/h, not m/s. Test it with a known value:
print(f"{knots_to_mps(1)=}   (1 knot should be 0.514 m/s)")

# Fix: divide by 3600 seconds per hour, then VERIFY with the same probes.
def knots_to_mps(knots):
    return knots * 1852 / 3600

print(f"fixed: {knots_to_mps(1)=:.3f}   {knots_to_mps(s3)=:.3f}")
