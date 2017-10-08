import math
DAY = 24*60*60.0

# WGS-84 data
EARTH_RADIUS = 6378137.0
EARTH_FLATTENING = 298.257223563
EARTH_ECCENTRICITY = 0.0818191908426215
EARTH_ANGULAR_VELOCITY = 7292115e-11
EARTH_MU = 3.986004418e14
EARTH_J2 = 108263e-8

# Minimum orbit altitude (the beginning of the atmosphere, where the satellites would normally decay)
MIN_ORBIT_ALTITUDE = 100e3
