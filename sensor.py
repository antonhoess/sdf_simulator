import numpy as np
import math
import abc


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


class ISensorCovMat:
    def __init__(self, cov_mat):
        self.cov_mat = cov_mat
        #XXX hier evtl. eine set_cov_mat() funktion einbauen? diese könnte im konstruktor aufgerufen werden


class ISensorMeasure(abc.ABC):
    def __init__(self):
        self.measurements = {}

    @abc.abstractmethod
    def measure(self, vehicle, *kargs, **kwargs):
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


class StandAloneSensor(ISensor, ISensorMeasure, ISensorCovMat):
    def __init__(self, name, active, pos, cov_mat):
        ISensor.__init__(self, name, active, pos)
        ISensorMeasure.__init__(self)
        ISensorCovMat.__init__(self, cov_mat)

class GroupSensor(ISensor, ISensorMeasure):
    def __init__(self, name, active, pos):
        ISensor.__init__(self, name, active, pos)
        ISensorMeasure.__init__(self)


class Plane(GroupSensor):
    def __init__(self, name, active, pos):
        GroupSensor.__init__(self, name, active, pos)


    def measure(self, vehicle, cov_mat, *kargs, **kwargs):
        # Measure position
        meas = np.random.multivariate_normal(vehicle.r, cov_mat, 1)[0]
        self.append_measurement(PlaneMeasurement(vehicle, meas))

        return meas

class StandAlonePlane(StandAloneSensor):
    def __init__(self, name, active, pos, cov_mat):
        StandAloneSensor.__init__(self, name, active, pos, cov_mat)

    def measure(self, vehicle, *kargs, **kwargs):
        # Measure position
        meas = np.random.multivariate_normal(vehicle.r, self.cov_mat, 1)[0]
        self.append_measurement(PlaneMeasurement(vehicle, meas))

        return meas

# class Radar(Sensor):
#     def __init__(self, name, active, pos):
#         super().__init__(name, active, pos)
#
#     def measure(self, vehicle, cov_mat, *kargs, **kwargs):
#         # Measure azimuth and range
#         theta = self.calc_rotation_angle(vehicle)
#         R = self.calc_rotation_matrix_2d(theta)
#         # meas_res = np.dot(R, np.random.multivariate_normal(vehicle.r, cov_r, 1)[0])
#         # ...
