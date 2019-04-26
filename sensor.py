import numpy as np


class RadarMeasurement:
    def __init__(self, r, rd, rdd):
        super().__init__()
        self.r = r
        self.rd = rd
        self.rdd = rdd


class Sensor:
    def __init__(self, name, pos_x, pos_y):
        self.name = name
        self.r = np.asarray([pos_x, pos_y])

        self.measurements = []
        self.last_meas_time = 0.

    def measure(self):
        raise NotImplementedError("Not implemented yet!")
        pass


class Radar(Sensor):
    def __init__(self, name, pos_x, pos_y, meas_interval, cov_r, cov_rd, cov_rdd):
        super().__init__(name, pos_x, pos_y)
        self.meas_interval = meas_interval
        self._cov_r = cov_r
        self._cov_rd = cov_rd
        self._cov_rdd = cov_rdd

    def measure(self, vehicle):
        mean = vehicle.r
        meas_r = np.random.multivariate_normal(mean, self._cov_r, 1)[0]
        meas_rd = np.random.multivariate_normal(mean, self._cov_rd, 1)[0]
        meas_rdd = np.random.multivariate_normal(mean, self._cov_rdd, 1)[0]
        self.measurements.append(RadarMeasurement(meas_r, meas_rd, meas_rdd))
