import numpy as np
import math
import abc


class Measurement:
    def __init__(self, vehicle, pos):
        self.vehicle = vehicle
        self.val = pos  # XXX List of different measures, the sensor can measure (position, range, azimuth, etc.)


# A measurement in a rectangular 2D plane
class PlaneMeasurement(Measurement):
    def __init__(self, vehicle, pos):
        super().__init__(vehicle, pos)

    @property
    def x(self):
        return self.val[0]

    @property
    def y(self):
        return self.val[1]


# A measurement in polar coordinates
class RadarMeasurement(Measurement):
    def __init__(self, vehicle, pos):
        super().__init__(vehicle, pos)

    @property
    def rho(self):
        return self.val[0]

    @property
    def phi(self):
        return self.val[1]


class ISensorMeasure(abc.ABC):
    def __init__(self, meas_interval, cov_mat):
        self.meas_interval = meas_interval
        self.cov_mat = cov_mat

        self.cov_mat_draw = True
        self.measurements = {}
        self.last_meas_time = 0.

    def set_meas_interval(self, meas_interval):
        self.meas_interval = meas_interval

    def set_cov_mat(self, cov_mat):
        self.cov_mat_draw = False
        self.cov_mat = cov_mat

    def trigger(self, t):
        if t >= self.last_meas_time + self.meas_interval:
            self.last_meas_time += self.meas_interval  # Don't loose the modulo rest

            return True
        else:
            return False

    @abc.abstractmethod
    def measure(self, vehicle, **kwargs):
        pass

    def append_measurement(self, meas):
        vehicle = meas.vehicle

        # Add position measurement to the measurement list
        if vehicle not in self.measurements:
            self.measurements[vehicle] = []

        self.measurements[vehicle].append(meas)


class ISensor:
    def __init__(self, name, active, pos):

        self.name = name
        self.active = active
        self.pos = pos

    def __str__(self):
        return self.name

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


class Plane(ISensor, ISensorMeasure):
    def __init__(self, name, active, pos, meas_interval, cov_mat):
        ISensor.__init__(self, name, active, pos)
        ISensorMeasure.__init__(self, meas_interval, cov_mat)

    def measure(self, vehicle, **kwargs):
        # Measure position
        meas = np.random.multivariate_normal(vehicle.r, self.cov_mat, 1)[0]
        self.append_measurement(PlaneMeasurement(vehicle, meas))


class Radar(ISensor, ISensorMeasure):
    def __init__(self, name, active, pos, meas_interval, cov_mat):
        ISensor.__init__(self, name, active, pos)
        ISensorMeasure.__init__(self, meas_interval, cov_mat)

    def measure(self, vehicle, **kwargs):
        meas = np.random.multivariate_normal(vehicle.r, self.cov_mat, 1)[0]
        self.append_measurement(RadarMeasurement(vehicle, meas))
