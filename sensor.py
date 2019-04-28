import numpy as np
import math


class RadarMeasurement:
    def __init__(self, vehicle, r_mean, r, rd, rdd):
        super().__init__()
        self.vehicle = vehicle
        self.r_mean = r_mean
        self.r = r
        self.rd = rd
        self.rdd = rdd


class Sensor:
    def __init__(self, name, pos_x, pos_y):
        self.name = name
        self.r = np.asarray([pos_x, pos_y])

        self.measurements = []
        self.last_meas_time = 0.

    def measure(self, vehicle):
        raise NotImplementedError("Not implemented yet!")


class Radar(Sensor):
    def __init__(self, name, pos_x, pos_y, meas_interval, cov_r, cov_rd, cov_rdd):
        super().__init__(name, pos_x, pos_y)
        self.meas_interval = meas_interval
        self.cov_r = cov_r
        self.cov_rd = cov_rd
        self.cov_rdd = cov_rdd

        # Calculate eigenvalues
        eVa, eVe = np.linalg.eig(self.cov_r)

        # Calculate transformation matrix from eigen decomposition
        R, S = eVe, np.diag(np.sqrt(eVa))

        # Calculate values for drawing the cov ellipse
        self.cov_r_theta = math.atan2(R[1, 0], R[1, 1])
        self.cov_r_r1 = S[0, 0]
        self.cov_r_r2 = S[1, 1]

    def __str__(self):
        return "{}: ∆T={:f})".format(self.name, self.meas_interval)

    def measure(self, vehicle):
        mean = vehicle.r
        meas_r = np.random.multivariate_normal(mean, self.cov_r, 1)[0]
        meas_rd = np.random.multivariate_normal(mean, self.cov_rd, 1)[0]
        meas_rdd = np.random.multivariate_normal(mean, self.cov_rdd, 1)[0]
        self.measurements.append(RadarMeasurement(vehicle, mean, meas_r, meas_rd, meas_rdd))
