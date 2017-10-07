import datetime
import argparse
from dateutil import tz
from sattrack.utils import *
from sattrack.orbit import *
from sattrack.geodesy import *
from sattrack.satellite import *
from sattrack.coordinates import *

parser = argparse.ArgumentParser("sattracker")
parser.add_argument("tle", help="The TLE file to use")
parser.add_argument("coords", help="The coordinates (lat, lon, alt) of the observer")
parser.add_argument("--duration", help="Days into the future to predict passes", type=int, default=14)
parser.add_argument("--step", help="The step for calculation of the orbit in seconds", type=int, default=30)
parser.add_argument("--elevation", help="Only display passes with the elevation higher than this value", type=float,
                    default=5.0)
parser.add_argument("--satellite", help="If there are multiple satellites, use the first one named", default="")

args = parser.parse_args()
lat, lon, alt = args.coords.split(",")
lat, lon, alt = float(lat), float(lon), float(alt)

with open(args.tle, "r") as tle_file:
    tle_lines = tle_file.readlines()
    tle_file.close()

tle = ""
satellite_name = None

for i in range(len(tle_lines)):
    line = tle_lines[i]
    if line.startswith("0 "):
        satellite_name = line[2:].strip()
    elif line[0] not in ["1", "2"]:
        satellite_name = line.strip()

    if (satellite_name and satellite_name == args.satellite) or not args.satellite:
        tle = tle_lines[i+1] + tle_lines[i+2]
        break

if not tle:
    print("Satellite not found")
    exit(1)

if satellite_name:
    print("Predictions for satellite %s" % satellite_name)

print("Station location: %8f %9f" % (lat, lon))

orbital_elements = None
try:
    orbital_elements = OrbitalElements.from_tle(tle)
except ValueError as err:
    print("Couldn't parse the TLE: %s" % err)
    exit(1)

satellite = Satellite(orbital_elements)

jd = jd_now()
local = tz.tzlocal()
seconds_since_epoch = (jd - orbital_elements.get_epoch_jd()) * DAY

print(orbital_elements.get_epoch_jd())
current_pass = False
max_el = 0
for i in range(0, int(DAY * args.duration / args.step)):
    theta = jd_theta(jd)
    eci = satellite.propagate_to_jd(jd)
    ecef = eci_to_ecef(eci, theta)
    topo = eci_to_topo(eci, (lat, lon, alt), theta)
    lla = ecef_to_lla(ecef)
    az, el, rg = topo
    timestamp = jd_to_date(jd).astimezone(local).strftime("%Y-%m-%d %H:%M:%S")
    if el > args.elevation:
        if not current_pass:
            print("Pass at %s" % timestamp)
            print("Timestamp           Lat      Lon        Alt     Az     El   Rng")
            current_pass = True
            max_el = 0

        if el > max_el:
            max_el = el

        print("%s %8.4f %9.4f %8.0f %6.1f %4.1f %7.0f" % (timestamp, *lla, *topo))
    elif current_pass:
        print("Maximum elevation: %.1f" % max_el)
        print("\n")
        current_pass = False

    jd += args.step / DAY