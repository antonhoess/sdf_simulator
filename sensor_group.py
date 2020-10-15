from kalman_filter_factory import *
from sensor import *
import numpy as np


__author__ = "Anton Höß"
__copyright__ = "Copyright 2020"


class _SensorGroup:
    """The internal sensor group base class.

    Parameters
    ----------
    name : str
        The sensor group's name.
    sensors
        An initial list of sensors to agg to this group.
    """

    def __init__(self, name, sensors):
        self.name = name
        self.sensors = sensors
    # end def

    def __str__(self):
        return self.name
    # end def

    @property
    def active(self):
        """Indicates if the sensor group is active, i.e. at least one sensor is active.

        Returns
        -------
        bool
            Indicator if the sensor group is active.
        """

        for s in self.sensors:
            if s.active:
                return True
        # end for

        return False
    # end def

    @abc.abstractmethod
    def _cb_meas(self, vehicle, measurement):
        pass
    # end def

    def add_sensor(self, sensor):
        """Adds a sensor to the sensor group.

        Parameters
        ----------
        sensor
            The sensor to be added.
        """

        self.sensors.append(sensor)
        self.sensors.add_measure_listener(self._cb_meas)
    # end def

    def remove_sensor(self, sensor):
        """Removes a sensor from the sensor group.

        Parameters
        ----------
        sensor
            The sensor to be removed.
        """

        self.sensors.remove(sensor)
        self.sensors.remove_measure_listener(self._cb_meas)
    # end def


class HomogeneousTriggeredSensorGroup(ISensorMeasure, _SensorGroup):
    """A sensor group where all sensors are triggered at the same time.

    Parameters
    ----------
    name : str
        The sensor group's name.
    sensors
        An initial list of sensors to agg to this group.
    meas_interval : float, optional
        The measurement interval in [s] (since the last measurement).
    cov_mat : numpy.ndarray, optional
        The measurements covariance matrix.
    """

    def __init__(self, name, sensors, meas_interval=None, cov_mat=None):
        ISensorMeasure.__init__(self, meas_interval, cov_mat)
        _SensorGroup.__init__(self, name, sensors)

        self.kalman_filter = dict()
        self.temp_measurements = dict()

        for sensor in sensors:
            sensor.set_meas_interval(self.meas_interval)
            sensor.set_cov_mat(self.cov_mat)
            sensor.add_measure_listener(self._cb_meas)
    # end def

    def __str__(self):
        return "{}: ∆T={:f}".format(self.name, self.meas_interval)
    # end def

    def _cb_meas(self, vehicle, measurement):
        """The measurement callback for a certain vehicle.

        Parameters
        ----------
        vehicle
            The vehicle the measuremet is assigned to.
        """

        if vehicle not in self.temp_measurements:
            self.temp_measurements[vehicle] = list()

        self.temp_measurements[vehicle].append(measurement)
    # end def

    def _measure(self, vehicle, **kwargs):
        """Creates a joined measurement (of all individual sensors of the sensor group) of the given vehicle.

        Parameters
        ----------
        vehicle : Vehicle
            The vehicle to measure.
        **kwargs : dict, optional
            Not used.

        Returns
        -------
        Measurement
            The joined measurement.
        """

        meas_res = list()

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
    # end def

    def add_sensor(self, sensor):
        """Adds a sensor to the homogeneously triggered sensor group.

        Parameters
        ----------
        sensor
            The sensor to be added.
        """

        _SensorGroup.add_sensor(sensor)
        sensor.set_meas_interval(self.meas_interval)
        sensor.set_cov_mat(self.cov_mat)
    # end def
# end class
