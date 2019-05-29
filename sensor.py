import abc
from vehicle import *
from type_check import *


class Measurement(abc.ABC):
    @accepts(Vehicle, np.ndarray, np.ndarray)
    def __init__(self, vehicle: Vehicle, meas: np.ndarray, sensor_pos: np.ndarray):
        self.vehicle = vehicle
        self.val = meas
        self.sensor_pos = sensor_pos

    @abc.abstractmethod
    def get_abs_cartesian(self) -> np.ndarray:
        pass


# A measurement in a rectangular 2D plane
class PlaneMeasurement(Measurement):
    @accepts(Vehicle, np.ndarray, np.ndarray)
    def __init__(self, vehicle: Vehicle, meas: np.ndarray, sensor_pos: np.ndarray):
        super().__init__(vehicle, meas, sensor_pos)

    @property
    @returns(float)
    def x(self) -> float:
        return self.val[0]

    @property
    @returns(float)
    def y(self) -> float:
        return self.val[1]

    @returns(np.ndarray)
    def get_abs_cartesian(self) -> np.ndarray:
        return self.val + self.sensor_pos


# A measurement in polar coordinates
class RadarMeasurement(Measurement):
    @accepts(Vehicle, np.ndarray, np.ndarray)
    def __init__(self, vehicle: Vehicle, meas: np.ndarray, sensor_pos: np.ndarray):
        super().__init__(vehicle, meas, sensor_pos)

    @property
    @returns(float)
    def rho(self) -> float:
        return self.val[0]

    @property
    @returns(float)
    def phi(self) -> float:
        return self.val[1]

    @returns(np.ndarray)
    def get_abs_cartesian(self) -> np.ndarray:
        return self.rho * np.asarray([math.cos(self.phi), math.sin(self.phi)]) + self.sensor_pos


class ISensorMeasure(abc.ABC):
    @accepts(float, np.ndarray)
    def __init__(self, meas_interval: float, cov_mat: np.ndarray):
        self.meas_interval = meas_interval
        self.cov_mat = cov_mat

        self.cov_mat_draw = True
        self.measurements = {}
        self.last_meas_time = 0.

        self.listeners = []

    @accepts(float)
    def set_meas_interval(self, meas_interval: float):
        self.meas_interval = meas_interval

    @accepts(np.ndarray)
    def set_cov_mat(self, cov_mat: np.ndarray):
        self.cov_mat_draw = False
        self.cov_mat = cov_mat

    @accepts(float)
    @returns(bool)
    def trigger(self, t: float) -> bool:
        if t >= self.last_meas_time + self.meas_interval:
            self.last_meas_time += self.meas_interval  # Don't loose the modulo rest
            return True
        else:
            return False

    @accepts(callable)
    def add_measure_listener(self, l: callable):
        self.listeners.append(l)

    @accepts(callable)
    def remove_measure_listener(self, l: callable):
        self.listeners.remove(l)

    @abc.abstractmethod
    @accepts(Vehicle)
    @returns(Measurement)
    def _measure(self, vehicle: Vehicle, **kwargs) -> Measurement:
        pass

    @accepts(Vehicle)
    @returns(Measurement)
    def measure(self, vehicle: Vehicle, **kwargs) -> Measurement:
        res = self._measure(vehicle, **kwargs)

        for l in self.listeners:
            l(vehicle, res)  # Callback

        return res

    @accepts(Vehicle, Measurement)
    def append_measurement(self, vehicle: Vehicle, meas: Measurement):
        # Add position measurement to the measurement list
        if vehicle not in self.measurements:
            self.measurements[vehicle] = []

        self.measurements[vehicle].append(meas)


class ISensor:
    @accepts(str, bool, np.ndarray)
    def __init__(self, name: str, active: bool, pos: np.ndarray):
        self.name = name
        self.active = active
        self.pos = pos

    @returns(str)
    def __str__(self) -> str:
        return self.name

    @staticmethod
    @accepts(float)
    @returns(np.ndarray)
    def calc_rotation_matrix_2d(theta) -> np.ndarray:
        c, s = np.cos(theta), np.sin(theta)

        return np.array(((c, -s), (s, c)))  # Rotation matrix

    @staticmethod
    @accepts(np.ndarray)
    @returns(tuple)
    def calc_cov_ell_params_2d(cov: np.ndarray) -> tuple:
        # Calculate eigenvalues
        eVa, eVe = np.linalg.eig(np.asarray(cov))

        # Calculate transformation matrix from eigen decomposition
        R, S = eVe, np.diag(np.sqrt(eVa))

        # Calculate values for the covariance ellipse
        cov_r_theta = math.atan2(R[1, 0], R[1, 1])
        cov_r_r1 = S[0, 0]
        cov_r_r2 = S[1, 1]

        return cov_r_theta, cov_r_r1, cov_r_r2

    @accepts(Vehicle)
    @returns(float)
    def calc_rotation_angle(self, vehicle: Vehicle) -> float:
        if vehicle is not None:
            return math.atan2(vehicle.r[1] - self.pos[1], vehicle.r[0] - self.pos[0])
        else:
            return 0


class Plane(ISensor, ISensorMeasure):
    @accepts(str, bool, np.ndarray, float, np.ndarray)
    def __init__(self, name: str, active: bool, pos: np.ndarray, meas_interval: float, cov_mat: np.ndarray):
        ISensor.__init__(self, name, active, pos)
        ISensorMeasure.__init__(self, meas_interval, cov_mat)

    @accepts(Vehicle)
    @returns(PlaneMeasurement)
    def _measure(self, vehicle: Vehicle, **kwargs) -> PlaneMeasurement:
        # Measure position
        meas = np.random.multivariate_normal(np.asarray([0, 0]), self.cov_mat, 1)[0]
        meas += vehicle.r - self.pos

        measurement = PlaneMeasurement(vehicle, meas, self.pos)
        self.append_measurement(vehicle, measurement)

        return measurement


class Radar(ISensor, ISensorMeasure):
    @accepts(str, bool, np.ndarray, float, np.ndarray)
    def __init__(self, name: str, active: bool, pos: np.ndarray, meas_interval: float, cov_mat: np.ndarray):
        ISensor.__init__(self, name, active, pos)
        ISensorMeasure.__init__(self, meas_interval, cov_mat)

    @accepts(Vehicle)
    @returns(RadarMeasurement)
    def _measure(self, vehicle: Vehicle, **kwargs) -> RadarMeasurement:
        meas = np.random.multivariate_normal(np.asarray([0, 0]), self.cov_mat, 1)[0]
        meas += np.asarray([np.linalg.norm(vehicle.r - self.pos), self.calc_rotation_angle(vehicle)])

        measurement = RadarMeasurement(vehicle, meas, self.pos)
        self.append_measurement(vehicle, measurement)

        return measurement
