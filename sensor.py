import numpy as np
import math
from kalman_filter import KalmanFilter

class RadarMeasurement:
    def __init__(self, vehicle, r_mean, r, rd, rdd):
        super().__init__()
        self.vehicle = vehicle
        self.r_mean = r_mean
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
        eVa, eVe = np.linalg.eig(cov)

        # Calculate transformation matrix from eigen decomposition
        R, S = eVe, np.diag(np.sqrt(eVa))

        # Calculate values for the covariance ellipse
        cov_r_theta = math.atan2(R[1, 0], R[1, 1])
        cov_r_r1 = S[0, 0]
        cov_r_r2 = S[1, 1]

        return cov_r_theta, cov_r_r1, cov_r_r2

    def measure(self, vehicle):
        # Measure position, velocity and acceleration
        mean = vehicle.r

        R = self.calc_rotation_matrix(self.calc_cov_ell_params(self.cov_r)[0])
        meas_r = np.random.multivariate_normal(mean, np.asarray(self.cov_r) * R, 1)[0]

        R = self.calc_rotation_matrix(self.calc_cov_ell_params(self.cov_rd)[0])
        meas_rd = np.random.multivariate_normal(mean, np.asarray(self.cov_rd) * R, 1)[0]

        R = self.calc_rotation_matrix(self.calc_cov_ell_params(self.cov_rdd)[0])
        meas_rdd = np.random.multivariate_normal(mean, np.asarray(self.cov_rdd) * R, 1)[0]

        # Add position measurement to the measurement list
        if not vehicle in self.measurements:
            self.measurements[vehicle] = []

        self.measurements[vehicle].append(RadarMeasurement(vehicle, mean, meas_r, meas_rd, meas_rdd))

        # Add filtered position measurement to the measurement_filter list
        if not vehicle in self.kalman_filter:
            DT = self.meas_interval
            I = np.identity(2)
            O = np.zeros((2, 2))
            F = np.block([[I, DT*I, 0.5*DT*DT*I],
                          [O,    I,        DT*I],
                          [O,    I,           I]])
            self.kalman_filter[vehicle] = KalmanFilter(x_init=np.zeros(6),
                                                       P_init=np.identity(6) * 1.e10,
                                                       F=F,
                                                       B=np.identity(6),
                                                       D=np.zeros([6, 6]), #XXX Here use G as in the script or on the website
                                                       H=np.identity(6),
                                                       R=np.identity(6) * 2500#xxx auch als np.block mit den 3 matrizen, aber diese sind ja winkelabhängig    np.stack([np.asarray(self.cov_r), np.asarray(self.cov_rd), np.asarray(self.cov_rdd)])
                                                       )#np.concatenate(self.cov_r, self.cov_rd, self.cov_rdd))
        self.kalman_filter[vehicle].predict(u=np.zeros(6))
        self.kalman_filter[vehicle].filter(z=np.concatenate([meas_r, meas_rd, meas_rdd]))
