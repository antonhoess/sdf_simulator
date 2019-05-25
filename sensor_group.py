from kalman_filter_factory import *
from sensor import *
import numpy as np
import abc


class _SensorGroup:
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


class HomogeneousTriggeredSensorGroup(ISensorMeasure, _SensorGroup):
    def __init__(self, name, sensors, meas_interval, cov_mat=None):
        ISensorMeasure.__init__(self, meas_interval, cov_mat)
        _SensorGroup.__init__(self, name, sensors)

        self.kalman_filter = {}

        for sensor in sensors:
            sensor.set_cov_mat(self.cov_mat)

    def __str__(self):
        return "{}: ∆T={:f}".format(self.name, self.meas_interval)

    def measure(self, vehicle, **kwargs):
        meas_res = []

        for s in self.sensors:
            meas_res.append((self.cov_mat, s.measurements[vehicle][-1].val))
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

        R, z = KalmanFilter.join_measurements(meas_res)

        self.kalman_filter[vehicle].filter(z=z, R=R)

        self.measurements[vehicle].append(self.kalman_filter[vehicle].get_current_state_estimate())

    def add_sensor(self, sensor):
        _SensorGroup.add_sensor(sensor)
        sensor.set_cov_mat(self.cov_mat)
