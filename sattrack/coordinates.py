import math
from .geodesy import *


def eci_to_ecef(eci, theta):
    """
    Rotates a set of ECI coordinates given to convert them to ECEF.
    :param eci: a set of ECI coordinates (X, Y, Z)
    :param theta: the rotation angle of Earth
    :return: the ECEF coordinates
    """

    xp, yp, z = eci
    x = xp*math.cos(theta) + yp*math.sin(theta)
    y = yp*math.cos(theta) - xp*math.sin(theta)

    return x, y, z


def ecef_to_lla(ecef):
    """
    Converts a set of ECEF coordinates to latitude, longitude and altitude.
    :param ecef: a set of ECEF coordinates (X, Y, Z)
    :return: the latitude, longitude and altitude above the surface of the Earth spheroid
    """

    x, y, z = ecef
    asq, esq = EARTH_RADIUS**2, EARTH_ECCENTRICITY**2
    b = math.sqrt(asq * (1-esq))
    bsq = b**2
    ep = math.sqrt((asq-bsq)/bsq)
    p = math.sqrt(x**2 + y**2)
    th = math.atan2(EARTH_RADIUS*z, b*p)
    lon = math.atan2(y, x)
    lat = math.atan2(z + (ep ** 2) * b * (math.sin(th) ** 3), p - esq * EARTH_RADIUS * (math.cos(th) ** 3))

    alt = math.sqrt(x**2 + y**2 + z**2) - EARTH_RADIUS
    lat *= 180 / math.pi
    lon *= 180 / math.pi

    return lat, lon, alt


def eci_to_topo(eci, observer_lla, theta):
    """
    Converts a set of ECI coordinates and the observer's location to azimuth, elevation and range.
    Using formulas from https://www.celestrak.com/columns/v02n02/.
    :param eci: the ECI coordinates of the object
    :param observer_lla: the location of the observer
    :param theta: the rotation angle of Earth
    :return: the azimuth, elevation and range to the observer
    """

    lat, lon, alt = observer_lla
    lat = lat / 180 * math.pi
    lon = lon / 180 * math.pi
    theta += lon
    alt += EARTH_RADIUS
    r = alt*math.cos(lat)
    xp = r*math.cos(theta)
    yp = r*math.sin(theta)
    zp = alt*math.sin(lat)
    x, y, z = eci
    rx, ry, rz = x - xp, y - yp, z - zp
    st = math.sin(lat) * math.cos(theta) * rx + math.sin(lat) * math.sin(theta) * ry - math.cos(lat) * rz
    et = -math.sin(theta) * rx + math.cos(theta) * ry
    zt = math.cos(lat) * math.cos(theta) * rx + math.cos(lat) * math.sin(theta) * ry + math.sin(lat) * rz
    az = math.atan2(-et, st) / math.pi * 180
    rg = math.sqrt(rx**2 + ry**2 + rz**2)
    el = math.asin(zt / rg) / math.pi * 180

    return az, el, rg


def jd_theta(jd):
    """
    Computes the theta (Earth rotation angle) from the Julian date given.
    :param jd: the current Julian date
    :return: the computed value of theta
    """

    gmst = math.pi*2*(0.7790572732640 + 1.00273781191135448*(jd - 2451545.0))
    return gmst
