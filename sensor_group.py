from kalman_filter_factory import *
from sensor import *
import numpy as np


class _SensorGroup:
    def __init__(self, name, sensors):
        self.name = name
        self.sensors = sensors

    def __str__(self):
        return self.name

    @property
    def active(self):
        for s in self.sensors:
            if s.active:
                return True
        # end for

        return False

    @abc.abstractmethod
    def _cb_meas(self, vehicle, measurement):
        pass

    def add_sensor(self, sensor):
        self.sensors.append(sensor)
        self.sensors.add_measure_listener(self._cb_meas)

    def remove_sensor(self, sensor):
        self.sensors.remove(sensor)
        self.sensors.remove_measure_listener(self._cb_meas)


class HomogeneousTriggeredSensorGroup(ISensorMeasure, _SensorGroup):
    def __init__(self, name, sensors, meas_interval=None, cov_mat=None):
        ISensorMeasure.__init__(self, meas_interval, cov_mat)
        _SensorGroup.__init__(self, name, sensors)

        self.kalman_filter = {}
        self.temp_measurements = {}

        for sensor in sensors:
            sensor.set_meas_interval(self.meas_interval)
            sensor.set_cov_mat(self.cov_mat)
            sensor.add_measure_listener(self._cb_meas)

    def __str__(self):
        return "{}: ∆T={:f}".format(self.name, self.meas_interval)

    def _cb_meas(self, vehicle, measurement):
        if vehicle not in self.temp_measurements:
            self.temp_measurements[vehicle] = []

        self.temp_measurements[vehicle].append(measurement)

    def _measure(self, vehicle, **kwargs):
        meas_res = []

        for meas in self.temp_measurements[vehicle]:
            meas_res.append((self.cov_mat, meas.val + meas.sensor_pos))  # Is it correct to add sensor_pos at this point at this point?
        # end for

        self.temp_measurements[vehicle].clear()

        if vehicle not in self.kalman_filter:
            self.kalman_filter[vehicle] \
                = KalmanFilterFactory.get_kalman_filter(KalmanFilterType.PLANE_2D,
                                                        self.meas_interval, self.cov_mat,
                                                        vehicle.v_max / vehicle.q_max * 0.75,
                                                        x_init=np.asarray([10000, 10000, 150, 300, 0, 0]))
        # end if

        # Add filtered position measurement to the measurement list
        self.kalman_filter[vehicle].predict(u=np.zeros(6))

        R, z = KF.join_measurements(meas_res)

        self.kalman_filter[vehicle].filter(z=z, R=R)

        measurement = PlaneMeasurement(vehicle, self.kalman_filter[vehicle].get_current_state_estimate(), np.zeros(6))
        self.append_measurement(vehicle, measurement)
        # self.measurements[vehicle].append(self.kalman_filter[vehicle].get_current_state_estimate())

        return measurement

    def add_sensor(self, sensor):
        _SensorGroup.add_sensor(sensor)
        sensor.set_meas_interval(self.meas_interval)
        sensor.set_cov_mat(self.cov_mat)
