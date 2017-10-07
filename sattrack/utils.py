import math
import datetime
from dateutil import tz
from sattrack.geodesy import DAY

# Note: assumes dates in the TLE range (2000-2057), can safely ignore the leap year rules for years ending in 00.

JD2000_EPOCH = datetime.datetime(2000, 1, 1, 12, 0, 0)

def jd_now():
    utc_now = datetime.datetime.utcnow()
    delta = utc_now - JD2000_EPOCH
    jd = 2451545.0 + delta.days + delta.seconds / DAY

    return jd

def jd_to_date(jd):
    delta = jd - 2451545.0
    date = (JD2000_EPOCH + datetime.timedelta(delta)).replace(tzinfo=tz.tzutc())
    return date


def epoch_to_jd(epoch_year, epoch):
    date = 2451544.5 + epoch_year*365 + int((epoch_year-1)/4) + epoch
    return date