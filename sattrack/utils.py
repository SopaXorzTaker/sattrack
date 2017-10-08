import math
import datetime
from dateutil import tz
from sattrack.geodesy import DAY

# Note: assumes dates in the TLE range (2000-2057), can safely ignore the leap year rules for years ending in 00.

JD2000_EPOCH = datetime.datetime(2000, 1, 1, 12, 0, 0)


def jd_now():
    """
    Computes the current Julian date.
    :return: the current Julian date
    """
    utc_now = datetime.datetime.utcnow()
    delta = utc_now - JD2000_EPOCH
    jd = 2451545.0 + delta.days + delta.seconds / DAY

    return jd


def jd_to_date(jd):
    """
    Converts a Julian date to a datetime object.
    :param jd: a Julian date
    :return: a datetime object corresponding to the date given
    """
    delta = jd - 2451545.0
    date = (JD2000_EPOCH + datetime.timedelta(delta)).replace(tzinfo=tz.tzutc())
    return date


def epoch_to_jd(epoch_year, epoch):
    """
    Converts a TLE epoch to a Julian date.
    :param epoch_year: the epoch year
    :param epoch: the epoch day
    :return: the computed Julian date
    """
    if epoch_year > 57:
        epoch_year -= 100

    date = 2451544.5 + epoch_year*365 + int((epoch_year-1)/4) + epoch
    return date
