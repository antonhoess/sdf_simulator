import numpy as np
import math


class Measurement:
    def __init__(self, vehicle):
        self.vehicle = vehicle
        self.meas = []  # List of different measures, the sensor can measure (position, range, azimuth, etc.)


# A measurement in a rectangular 2D plane
class PlaneMeasurement(Measurement):
    def __init__(self, vehicle, pos):
        super().__init__(vehicle)
        self.meas = [pos]


# A measurement in polar coordinates
class RadarMeasurement(Measurement):
    def __init__(self, vehicle, pos):
        super().__init__(vehicle)
        self.meas = [pos]


class Sensor:
    def __init__(self, name, active, pos):
        self.name = name
        self.active = active
        self.pos = pos

        self.measurements = {}

    def __str__(self):
        return self.name

    def measure(self, vehicle, *kargs, **kwargs):
        raise NotImplementedError("Not implemented yet!")

    @staticmethod
    def calc_rotation_matrix_2d(theta):
        c, s = np.cos(theta), np.sin(theta)

        return np.array(((c, -s), (s, c)))  # Rotation matrix

    @staticmethod
    def calc_cov_ell_params_2d(cov):
        # Calculate eigenvalues
        eVa, eVe = np.linalg.eig(np.asarray(cov))

        # Calculate transformation matrix from eigen decomposition
        R, S = eVe, np.diag(np.sqrt(eVa))

        # Calculate values for the covariance ellipse
        cov_r_theta = math.atan2(R[1, 0], R[1, 1])
        cov_r_r1 = S[0, 0]
        cov_r_r2 = S[1, 1]

        return cov_r_theta, cov_r_r1, cov_r_r2

    def calc_rotation_angle(self, vehicle):
        if vehicle is not None:
            return math.atan2(vehicle.r[1] - self.pos[1], vehicle.r[0] - self.pos[0])
        else:
            return 0

    def append_measurement(self, meas):
        vehicle = meas.vehicle

        # Add position measurement to the measurement list
        if vehicle not in self.measurements:
            self.measurements[vehicle] = []

        self.measurements[vehicle].append(meas)


class Plane(Sensor):
    def __init__(self, name, active, pos):
        super().__init__(name, active, pos)

    def measure(self, vehicle, cov_mat, *kargs, **kwargs):
        # Measure position
        meas = np.random.multivariate_normal(vehicle.r, cov_mat, 1)[0]
        self.append_measurement(PlaneMeasurement(vehicle, meas))

        return meas


class Radar(Sensor):
    def __init__(self, name, active, pos):
        super().__init__(name, active, pos)

    def measure(self, vehicle, cov_mat, *kargs, **kwargs):
        # Measure azimuth and range
        theta = self.calc_rotation_angle(vehicle)
        R = self.calc_rotation_matrix_2d(theta)
        # meas_res = np.dot(R, np.random.multivariate_normal(vehicle.r, cov_r, 1)[0])
        # ...
