from kalman_filter_factory import *
from sensor import *
import numpy as np


class SensorGroup:
    def __init__(self, name, sensors):
        self.name = name
        self.sensors = sensors

    @property
    def active(self):
        for s in self.sensors:
            if s.active:
                return True
        # end for

        return False

    def add_sensor(self, sensor):
        self.sensors.append(sensor)


class SensorGroupTrigger:
    def __init__(self, meas_interval):
        self.meas_interval = meas_interval

        self.last_meas_time = 0.

    def trigger(self, t):
        if t >= self.last_meas_time + self.meas_interval:
            self.last_meas_time += self.meas_interval  # Don't loose the modulo rest

            return True
        else:
            return False


class HomogeneousTriggeredSensorGroup(ISensorMeasure, ISensorCovMat, SensorGroup, SensorGroupTrigger):
    def __init__(self, name, sensors, meas_interval, cov_mat):
        ISensorMeasure.__init__(self)
        ISensorCovMat.__init__(self, cov_mat)
        SensorGroup.__init__(self, name, sensors)
        SensorGroupTrigger.__init__(self, meas_interval)

        self.kalman_filter = {}

    def __str__(self):
        return "{}: ∆T={:f}".format(self.name, self.meas_interval)

    def measure(self, vehicle):
        meas_res = []

        for s in self.sensors:
            meas_res.append(s.measure(vehicle, self.cov_mat))
        # end for

        if vehicle not in self.measurements:
            self.measurements[vehicle] = []

        if vehicle not in self.kalman_filter:
            self.kalman_filter[vehicle] \
                = KalmanFilterFactory.get_kalman_filter(KalmanFilterType.PLANE_2D,
                                                        self.meas_interval, self.cov_mat,
                                                        vehicle.v_max / vehicle.q_max * 0.75,
                                                        x_init=np.asarray([10000, 10000, 150, 300, 0, 0]))

        # Add filtered position measurement to the measurement list
        self.kalman_filter[vehicle].predict(u=np.zeros(6))
        self.kalman_filter[vehicle].filter(z=np.mean(meas_res, axis=0))

        self.measurements[vehicle].append(self.kalman_filter[vehicle].get_current_state_estimate())
