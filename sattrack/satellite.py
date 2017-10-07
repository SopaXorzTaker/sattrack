import math
from .geodesy import *


class Satellite(object):
    def __init__(self, orbital_elements):
        """
        Creates a new Satellite object.
        :param orbital_elements: an OrbitalElements object, the set of orbital elements to use for propagation
        """

        self.orbital_elements = orbital_elements

    def propagate(self, seconds_since_epoch):
        """
        Computes the satellite's position after a number of seconds since the epoch.
        :param seconds_since_epoch: the time in seconds since the epoch
        :return: the ECI position of the satellite
        """

        days_since_epoch = seconds_since_epoch / DAY

        # Compute the current derivative of mean motion
        mean_motion_derivative = self.orbital_elements.mean_motion_derivative +\
                                         self.orbital_elements.mean_motion_derivative_2 * days_since_epoch

        # Compute the current mean motion
        mean_motion = self.orbital_elements.mean_motion + mean_motion_derivative * days_since_epoch
        mean_motion_radians_per_second = (mean_motion / DAY) * math.pi * 2

        # Compute the current mean anomaly
        current_mean_anomaly = self.orbital_elements.mean_anomaly + mean_motion_radians_per_second * seconds_since_epoch

        # Compute the semi-major axis of the orbit
        semi_major_axis = EARTH_MU ** (1/3) / mean_motion_radians_per_second ** (2/3)

        # Compute the current eccentric anomaly iterating Kepler's equation
        old_eccentric_anomaly = 0
        eccentric_anomaly = current_mean_anomaly
        while abs(eccentric_anomaly - old_eccentric_anomaly) > 1e-12:
            old_eccentric_anomaly = eccentric_anomaly
            eccentric_anomaly = current_mean_anomaly + self.orbital_elements.eccentricity * math.sin(eccentric_anomaly)

        # Compute the true anomaly
        true_anomaly = 2*math.atan2(math.sqrt(1 + self.orbital_elements.eccentricity) * math.sin(eccentric_anomaly / 2),
                                    math.sqrt(1 - self.orbital_elements.eccentricity) * math.cos(eccentric_anomaly / 2))

        # Account for J2 perturbations in the ascending node and argument of perigee
        delta_asc = -1.5*mean_motion_radians_per_second*EARTH_J2*(EARTH_RADIUS / semi_major_axis)**2\
                * (math.cos(self.orbital_elements.inclination)/(1-self.orbital_elements.eccentricity**2)**2)

        delta_arg = 0.75*mean_motion_radians_per_second*EARTH_J2*(EARTH_RADIUS / semi_major_axis)**2\
                * ((4-5*math.sin(self.orbital_elements.inclination)**2)/(1-self.orbital_elements.eccentricity**2)**2)

        ascending_node = self.orbital_elements.ascending_node + delta_asc*seconds_since_epoch
        argument_of_perigee = self.orbital_elements.argument_of_perigee + delta_arg*seconds_since_epoch

        # Compute the ECI coordinates
        radius = semi_major_axis * (1 - self.orbital_elements.eccentricity * math.cos(eccentric_anomaly))

        cos_asc, sin_asc = math.cos(ascending_node), math.sin(ascending_node)
        cos_arg, sin_arg = math.cos(argument_of_perigee + true_anomaly), math.sin(argument_of_perigee + true_anomaly)
        cos_inc, sin_inc = math.cos(self.orbital_elements.inclination), math.sin(self.orbital_elements.inclination)

        """
            radius * (cos_asc * cos_arg_tru - sin_asc * sin_arg_tru * cos_inc),
            radius * (sin_asc * cos_arg_tru + cos_asc * sin_arg_tru * cos_inc),
            radius * (sin_inc * sin_arg_tru),
        """
        x = radius*(cos_asc * cos_arg - sin_asc * sin_arg * cos_inc)
        y = radius*(sin_asc * cos_arg + cos_asc * sin_arg * cos_inc)
        z = radius*(sin_arg * sin_inc)

        return x, y, z

    def propagate_to_jd(self, jd):
        """
        Propagate the satellite's position to the Julian date specified.
        :param jd: the Julian date to use
        :return: the calculated ECI position of the satellite.
        """

        return self.propagate((jd - self.orbital_elements.get_epoch_jd()) * DAY)