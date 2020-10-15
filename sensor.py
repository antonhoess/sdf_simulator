import abc
from vehicle import *
from type_check import *


__author__ = "Anton Höß"
__copyright__ = "Copyright 2020"


class Measurement(abc.ABC):
    """An abstract measurement class.

    Parameters
    ----------
    vehicle : Vehicle
        The vehicle that the measurement is assigned to.
    meas : numpy.ndarray
        The measurement vector relative to the Sensor's position.
    sensor_pos : numpy.ndarray
        The sensor's position.
    """

    @accepts(Vehicle, np.ndarray, np.ndarray)
    def __init__(self, vehicle: Vehicle, meas: np.ndarray, sensor_pos: np.ndarray):
        self.vehicle = vehicle
        self.val = meas
        self.sensor_pos = sensor_pos
    # end def

    @abc.abstractmethod
    def get_abs_cartesian(self) -> np.ndarray:
        """Return the measurements position as cartesian coordinates.

        Returns
        -------
        numpy.ndarray
            The cartesian coordinates.
        """

        pass
    # end def
# end class


class PlaneMeasurement(Measurement):
    """A measurement in a rectangular 2D plane."""

    @accepts(Vehicle, np.ndarray, np.ndarray)
    def __init__(self, vehicle: Vehicle, meas: np.ndarray, sensor_pos: np.ndarray):
        super().__init__(vehicle, meas, sensor_pos)
    # end def

    @property
    @returns(float)
    def x(self) -> float:
        return self.val[0]
    # end def

    @property
    @returns(float)
    def y(self) -> float:
        return self.val[1]
    # end def

    @returns(np.ndarray)
    def get_abs_cartesian(self) -> np.ndarray:
        return self.val + self.sensor_pos
    # end def
# end class


class RadarMeasurement(Measurement):
    """A measurement in polar coordinates."""

    @accepts(Vehicle, np.ndarray, np.ndarray)
    def __init__(self, vehicle: Vehicle, meas: np.ndarray, sensor_pos: np.ndarray):
        super().__init__(vehicle, meas, sensor_pos)
    # end def

    @property
    @returns(float)
    def rho(self) -> float:
        return self.val[0]
    # end def

    @property
    @returns(float)
    def phi(self) -> float:
        return self.val[1]
    # end def

    @returns(np.ndarray)
    def get_abs_cartesian(self) -> np.ndarray:
        return self.rho * np.asarray([math.cos(self.phi), math.sin(self.phi)]) + self.sensor_pos
    # end def
# end class


class ISensorMeasure(abc.ABC):
    """A sensor measurement interface."""

    @accepts(float, np.ndarray)
    def __init__(self, meas_interval: float, cov_mat: np.ndarray):
        """Initializes the ISensorMeasure interface.

        Parameters
        ----------
        meas_interval : float
            The measurement interval in [s] (since the last measurement).
        cov_mat : numpy.ndarray
            The measurements covariance matrix.
        """

        self.meas_interval = meas_interval
        self.cov_mat = cov_mat

        self.cov_mat_draw = True
        self.measurements = {}
        self.last_meas_time = 0.

        self.listeners = list()
    # end def

    @accepts(float)
    def set_meas_interval(self, meas_interval: float):
        """Sets the measurement interval to the given value.

        Parameters
        ----------
        meas_interval : float
            The measurement interval.
        """

        self.meas_interval = meas_interval
    # end def

    @accepts(np.ndarray)
    def set_cov_mat(self, cov_mat: np.ndarray):
        """Sets the covariance matrix to the given value.

        Parameters
        ----------
        cov_mat : numpy.ndarray
            The covariance matrix.
        """

        self.cov_mat_draw = False
        self.cov_mat = cov_mat
    # end def

    @accepts(float)
    @returns(bool)
    def trigger(self, t: float) -> bool:
        """Triggers the sensor.

        Parameters
        ----------
        t : float
            The trigger timestamp.

        Returns
        -------
        bool
            True if it has triggered (only happens if t is plausible, i.e. not older than the latest trigger).
        """

        if t >= self.last_meas_time + self.meas_interval:
            self.last_meas_time += self.meas_interval  # Don't loose the modulo rest
            return True
        else:
            return False
        # end if
    # end def

    @accepts(callable)
    def add_measure_listener(self, l: callable):
        """Adds a measurement listener to the list of listeners.

        Parameters
        ----------
        l : callable
            The listener callback to add.
        """

        self.listeners.append(l)
    # end def

    @accepts(callable)
    def remove_measure_listener(self, l: callable):
        """Removes a measurement listener from the list of listeners.

        Parameters
        ----------
        l : callable
            The listener callback to remove.
        """

        self.listeners.remove(l)
    # end def

    @abc.abstractmethod
    @accepts(Vehicle)
    @returns(Measurement)
    def _measure(self, vehicle: Vehicle, **kwargs) -> Measurement:
        """Creates a measurement of the given vehicle.

        Parameters
        ----------
        vehicle : Vehicle
            The vehicle to measure.
        **kwargs : dict, optional
            Not used.

        Returns
        -------
        Measurement
            The created measurement.
        """

        pass
    # end def

    @accepts(Vehicle)
    @returns(Measurement)
    def measure(self, vehicle: Vehicle, **kwargs) -> Measurement:
        """Creates a measurement of the given vehicle and informs all listeners.

        Parameters
        ----------
        vehicle : Vehicle
            The vehicle to measure.
        **kwargs : dict, optional
            Not used.

        Returns
        -------
        Measurement
            The created measurement.
        """

        res = self._measure(vehicle, **kwargs)

        for l in self.listeners:
            l(vehicle, res)  # Callback

        return res
    # end def

    @accepts(Vehicle, Measurement)
    def append_measurement(self, vehicle: Vehicle, meas: Measurement):
        """Adds a position measurement to the measurement list.

        Parameters
        ----------
        vehicle : Vehicle
            The vehicle to add the measurement to.
        meas : Measurement
            The measurement to add.
        """

        if vehicle not in self.measurements:
            self.measurements[vehicle] = []

        self.measurements[vehicle].append(meas)
    # end def
# end class


class ISensor:
    """A sensor interface."""

    @accepts(str, bool, np.ndarray)
    def __init__(self, name: str, active: bool, pos: np.ndarray):
        """Initializes the ISensor interface.

        Parameters
        ----------
        name : str
            The sensor's name.
        active : bool
            Indicates if the sensor is active on starting the simulation.
        pos : numpy.ndarray
            The sensor's position.
        """

        self.name = name
        self.active = active
        self.pos = pos
    # end def

    @returns(str)
    def __str__(self) -> str:
        return self.name
    # end if

    @staticmethod
    @accepts(float)
    @returns(np.ndarray)
    def calc_rotation_matrix_2d(theta) -> np.ndarray:
        """Calculates a 2D rotation matrix of a given angle.

        Parameters
        ----------
        theta : float
            The rotation angle.

        Returns
        -------
        np.ndarray
            The 2D rotation matrix.
        """

        c, s = np.cos(theta), np.sin(theta)

        return np.array(((c, -s), (s, c)))  # Rotation matrix
    # end def

    @staticmethod
    @accepts(np.ndarray)
    @returns(tuple)
    def calc_cov_ell_params_2d(cov: np.ndarray) -> tuple:
        """Calculates the covariance ellipse parameters of a given covariance matrix.

        Parameters
        ----------
        cov : numpy.ndarray
            The covariance matrix.

        Returns
        -------
        (float, float, float)
            The covariance ellipse's parameters: rotation angle, radius 1, radius 2.
        """

        # Calculate eigenvalues
        eVa, eVe = np.linalg.eig(np.asarray(cov))

        # Calculate transformation matrix from eigen decomposition
        R, S = eVe, np.diag(np.sqrt(eVa))

        # Calculate values for the covariance ellipse
        cov_r_theta = math.atan2(R[1, 0], R[1, 1])
        cov_r_r1 = S[0, 0]
        cov_r_r2 = S[1, 1]

        return cov_r_theta, cov_r_r1, cov_r_r2
    # end def

    @accepts(Vehicle)
    @returns(float)
    def calc_rotation_angle(self, vehicle: Vehicle) -> float:
        """Calculates the rotation angle between the sensor and the vehicle.

        Parameters
        ----------
        vehicle : Vehicle
            The vehicle to calculate the rotation angle to.

        Returns
        -------
        float
            The rotation angle.
        """

        if vehicle is not None:
            return math.atan2(vehicle.r[1] - self.pos[1], vehicle.r[0] - self.pos[0])
        else:
            return 0
        # end if
    # end def
# end class


class Plane(ISensor, ISensorMeasure):
    """A planar sensor (only for simulation, but doesn't really exist)."""

    @accepts(str, bool, np.ndarray, float, np.ndarray)
    def __init__(self, name: str, active: bool, pos: np.ndarray, meas_interval: float, cov_mat: np.ndarray):
        """Initializes the Plane sensor.

        Parameters
        ----------
        name : str
            The sensor's name.
        active : bool
            Indicates if the sensor is active on starting the simulation.
        pos : numpy.ndarray
            The sensor's position.
        meas_interval : float
            The measurement interval in [s] (since the last measurement).
        cov_mat : numpy.ndarray
            The measurements covariance matrix.
        """

        ISensor.__init__(self, name, active, pos)
        ISensorMeasure.__init__(self, meas_interval, cov_mat)
    # end def

    @accepts(Vehicle)
    @returns(PlaneMeasurement)
    def _measure(self, vehicle: Vehicle, **kwargs) -> PlaneMeasurement:
        """Creates a measurement of the given vehicle.

        Parameters
        ----------
        vehicle : Vehicle
            The vehicle to measure.
        **kwargs :
            Not used.

        Returns
        -------
        PlaneMeasurement
            The created plane measurement.
        """

        # Measure position
        meas = np.random.multivariate_normal(np.asarray([0, 0]), self.cov_mat, 1)[0]
        meas += vehicle.r - self.pos

        measurement = PlaneMeasurement(vehicle, meas, self.pos)
        self.append_measurement(vehicle, measurement)

        return measurement
    # end def
# end class


class Radar(ISensor, ISensorMeasure):
    @accepts(str, bool, np.ndarray, float, np.ndarray)
    def __init__(self, name: str, active: bool, pos: np.ndarray, meas_interval: float, cov_mat: np.ndarray):
        """Initializes the Radar sensor.

        Parameters
        ----------
        name : str
            The sensor's name.
        active : bool
            Indicates if the sensor is active on starting the simulation.
        pos : numpy.ndarray
            The sensor's position.
        meas_interval : float
            The measurement interval in [s] (since the last measurement).
        cov_mat : numpy.ndarray
            The measurements covariance matrix.
        """

        ISensor.__init__(self, name, active, pos)
        ISensorMeasure.__init__(self, meas_interval, cov_mat)
    # end def

    @accepts(Vehicle)
    @returns(RadarMeasurement)
    def _measure(self, vehicle: Vehicle, **kwargs) -> RadarMeasurement:
        """Creates a measurement of the given vehicle.

        Parameters
        ----------
        vehicle : Vehicle
            The vehicle to measure.
        **kwargs : dict, optional
            Not used.

        Returns
        -------
        RadarMeasurement
            The created radar measurement.
        """

        meas = np.random.multivariate_normal(np.asarray([0, 0]), self.cov_mat, 1)[0]
        meas += np.asarray([np.linalg.norm(vehicle.r - self.pos), self.calc_rotation_angle(vehicle)])

        measurement = RadarMeasurement(vehicle, meas, self.pos)
        self.append_measurement(vehicle, measurement)

        return measurement
    # end def
# end class
