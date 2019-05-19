import numpy as np
import math
from kalman_filter import KalmanFilter

class RadarMeasurement:
    def __init__(self, vehicle, r, rd, rdd):
        super().__init__()
        self.vehicle = vehicle
        self.r = r
        self.rd = rd
        self.rdd = rdd


class Sensor:
    def __init__(self, name, active, pos_x, pos_y):
        self.name = name
        self.active = active
        self.r = np.asarray([pos_x, pos_y])

        self.measurements = {}
        self.kalman_filter = {}
        self.last_meas_time = 0.

    def measure(self, vehicle):
        raise NotImplementedError("Not implemented yet!")


class Radar(Sensor):
    def __init__(self, name, active, pos_x, pos_y, meas_interval, cov_r, cov_rd, cov_rdd):
        super().__init__(name, active, pos_x, pos_y)
        self.meas_interval = meas_interval
        self.cov_r = cov_r
        self.cov_rd = cov_rd
        self.cov_rdd = cov_rdd

    def __str__(self):
        return "{}: ∆T={:f})".format(self.name, self.meas_interval)

    def calc_rotation_angle(self, vehicle):
        if vehicle is not None:
            return math.atan2(vehicle.r[1] - self.r[1], vehicle.r[0] - self.r[0])
        else:
            return 0

    @staticmethod
    def calc_rotation_matrix(theta):
        c, s = np.cos(theta), np.sin(theta)

        return np.array(((c, -s), (s, c)))  # Rotation matrix

    @staticmethod
    def calc_cov_ell_params(cov):
        # Calculate eigenvalues
        eVa, eVe = np.linalg.eig(np.asarray(cov))

        # Calculate transformation matrix from eigen decomposition
        R, S = eVe, np.diag(np.sqrt(eVa))

        # Calculate values for the covariance ellipse
        cov_r_theta = math.atan2(R[1, 0], R[1, 1])
        cov_r_r1 = S[0, 0]
        cov_r_r2 = S[1, 1]

        return cov_r_theta, cov_r_r1, cov_r_r2

    def measure(self, vehicle):
        # Measure position, velocity and acceleration
        theta = self.calc_rotation_angle(vehicle)
        R = self.calc_rotation_matrix(theta)

        meas_r = np.dot(R, np.random.multivariate_normal(np.asarray([0, 0]), self.cov_r, 1)[0]) + vehicle.r
        meas_rd = np.dot(R, np.random.multivariate_normal(np.asarray([0, 0]), self.cov_rd, 1)[0]) + vehicle.rd
        meas_rdd = np.dot(R, np.random.multivariate_normal(np.asarray([0, 0]), self.cov_rdd, 1)[0]) + vehicle.rdd

        # Add position measurement to the measurement list
        if not vehicle in self.measurements:
            self.measurements[vehicle] = []

        self.measurements[vehicle].append(RadarMeasurement(vehicle, meas_r, meas_rd, meas_rdd))

        # Add filtered position measurement to the measurement_filter list
        if not vehicle in self.kalman_filter:
            DT = self.meas_interval
            I = np.identity(2)
            O = np.zeros((2, 2))
            F = np.block([[I, DT * I, 0.5 * DT * DT * I],
                          [O,      I,            DT * I],
                          [O,      I,                 I]])
            Σ = np.ones(6).T * 9 * 0.75  # m/s^2
            G = np.block([[0.5 * DT * DT * I],
                          [           DT * I],
                          [                I]])
            H = np.block([[I, O, O],
                          [O, I, O],
                          [O, O, O]])
            R = np.block([[self.cov_r,           O,            O],
                          [         O, self.cov_rd,            O],
                          [         O,           O, self.cov_rdd]])  # XXX cov_r* is not rotated yet
            self.kalman_filter[vehicle] = KalmanFilter(#x_init=np.zeros(6),
                                                       x_init=np.asarray([1000, 1000, 150, 300, 0, 0]),  # np.ones(6) * 1.e4,
                                                       P_init=np.identity(6) * 1.e10,
                                                       F=F,
                                                       B=np.identity(6),
                                                       Q=np.dot(G, G.T) * Σ**2,
                                                       H=H,  # np.identity(6),
                                                       R=R  # np.identity(6),
                                                       )
        self.kalman_filter[vehicle].predict(u=np.zeros(6))
        self.kalman_filter[vehicle].filter(z=np.concatenate([meas_r, meas_rd, meas_rdd]))
