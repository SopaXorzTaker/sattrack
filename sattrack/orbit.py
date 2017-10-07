import math

from sattrack.utils import epoch_to_jd


class OrbitalElements(object):
    def __init__(self, epoch_year, epoch, mean_motion_derivative, mean_motion_derivative_2, bstar, inclination,
                 ascending_node, eccentricity, argument_of_perigee, mean_anomaly, mean_motion, epoch_revolution):
        """
        Creates the OrbitalElements object.
        :param epoch_year: the year of epoch
        :param epoch: the day of epoch
        :param mean_motion_derivative: the first derivative of mean motion
        :param mean_motion_derivative_2: the second derivative of mean motion
        :param bstar: the drag coefficient
        :param inclination: the orbital inclination
        :param ascending_node: the ascending node of the orbit
        :param eccentricity: the orbital eccentricity
        :param argument_of_perigee: the argument of perigee of the orbit
        :param mean_anomaly: the mean anomaly of the orbit at the epoch
        :param mean_motion: the mean motion of the orbit at the epoch
        :param epoch_revolution: the revolution number at the epoch
        """

        self.epoch_year, self.epoch, self.mean_motion_derivative, self.mean_motion_derivative_2, self.bstar, \
            self.inclination, self.ascending_node, self.eccentricity, self.argument_of_perigee, self.mean_anomaly,\
            self.mean_motion, self.epoch_revolution = epoch_year, epoch, mean_motion_derivative,\
            mean_motion_derivative_2, bstar, inclination, ascending_node, eccentricity, argument_of_perigee,\
            mean_anomaly, mean_motion, epoch_revolution

    @staticmethod
    def from_tle(tle):
        """
        Creates an OrbitalElements object from a two-line element set.
        :param tle: the TLE lines to use
        :return: the created OrbitalElements object
        """
        digits = "0123456789 -"
        tle_lines = [line.strip() for line in tle.split("\n")]
        first_line = ""
        second_line = ""

        for line in tle_lines:
            if line.startswith("1"):
                first_line = line
            elif line.startswith("2"):
                second_line = line

        first_line_checksum = sum([digits.index(c) if c in digits else 0 for c in first_line[:68]]) % 10
        second_line_checksum = sum([digits.index(c) if c in digits else 0 for c in second_line[:68]]) % 10

        if not int(first_line[68]) == first_line_checksum:
            raise ValueError("Invalid line 1 checksum")

        if not int(second_line[68]) == second_line_checksum:
            raise ValueError("Invalid line 2 checksum")

        epoch_year = int(first_line[18:20])
        epoch = float(first_line[20:32])
        mean_motion_derivative = float(first_line[33:43])*2
        mean_motion_derivative_2 = float(first_line[44] + "." + first_line[45:50] + "e" + first_line[50:52])*6
        bstar = float(first_line[53] + "." + first_line[54:59] + "e" + first_line[59:61])
        inclination = float(second_line[8:16]) / 180 * math.pi
        ascending_node = float(second_line[17:25]) / 180 * math.pi
        eccentricity = float("." + second_line[26:33])
        argument_of_perigee = float(second_line[34:42]) / 180 * math.pi
        mean_anomaly = float(second_line[43:51]) / 180 * math.pi
        mean_motion = float(second_line[52:63])
        epoch_revolution = int(second_line[63:68])

        return OrbitalElements(epoch_year, epoch, mean_motion_derivative, mean_motion_derivative_2, bstar, inclination,
                               ascending_node, eccentricity, argument_of_perigee, mean_anomaly, mean_motion,
                               epoch_revolution)

    def get_epoch_jd(self):
        """
        Computes the Julian date of the epoch.
        :return: the computed date
        """

        return epoch_to_jd(self.epoch_year, self.epoch)
