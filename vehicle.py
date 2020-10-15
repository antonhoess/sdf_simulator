import numpy as np
import math


__author__ = "Anton Höß"
__copyright__ = "Copyright 2020"


class Vehicle:
    """Defines a vehicle which can be detected by sensors.

    Parameters
    ----------
    name : str
        The name of the vehicle.
    active : bool
        Defines if the vehicle is active on starting the simulation (can be activated later).
    v : float, optional
        The vehicle's velocity.
    q : float, optional
        The vehicle's acceleration.
    """

    def __init__(self, name, active, v=100., q=10.):
        self.name = name
        self.active = active
        self.v_max = v
        self.q_max = q

        self.A = v * v / q
        self.omega = q / (2 * v)

        self.r = np.zeros(2)
        self.rd = np.zeros(2)       # r'(t)         -> velocity
        self.rdd = np.zeros(2)      # r''(t)        -> acceleration
        self.rdt = np.zeros(2)      # t(t)          -> tangent (normalized)
        self.rdn = np.zeros(2)      # n(t)          -> normal (normalized)
        self.rddxrdt = np.zeros(2)  # r''(t) x t(t) -> acceleration x tangent (normalized)
        self.rddxrdn = np.zeros(2)  # r''(t) x n(t) -> acceleration x normal (normalized)
    # end def

    def __str__(self):
        return "{}: vel={}, accel={}, pos=({:10.4f} {:10.4f})".format(self.name, self.v_max, self.q_max, self.r[0], self.r[1])
    # end def

    def update(self, t):
        """Updates the Vehicle's state (position, velocity, acceleration).

        Parameters
        ----------
        t : float
            The time to calculate the Vehicle's state for.
        """
        vec = np.array([math.sin(self.omega * t), math.sin(2 * self.omega * t)])
        self.r = self.A * vec

        vec = np.array([math.cos(self.omega * t) / 2.0, math.cos(2 * self.omega * t)])
        self.rd = self.v_max * vec

        vec = np.array([math.sin(self.omega * t) / 4.0, math.sin(2 * self.omega * t)])
        self.rdd = -self.q_max * vec

        self.rdt = self.rd / np.linalg.norm(self.rd)

        self.rdn = np.array([-self.rd[1], self.rd[0]]) / np.linalg.norm(self.rd)

        self.rddxrdt = self.rdd * self.rdt

        self.rddxrdn = self.rdd * self.rdn
    # end def
# end class
