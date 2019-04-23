import numpy as np
import math


class Vehicle:

    def __init__(self, name, v=300, q=9):
        self.name = name
        self.v = v
        self.q = q

        self.A = v * v / q
        self.omega = q / (2 * v)

        self.r = np.zeros(2)
        self.rd = np.zeros(2)  # r'(t)
        self.rdd = np.zeros(2)  # r''(t)
        self.rdtn = np.zeros(2)  # r''(t) normalized tangent
        self.rdnn = np.zeros(2)  # r''(t) normalized normal

    def __str__(self):
        return "{}: vel={}, accel={}, pos=({:10.4f} {:10.4f})".format(self.name, self.v, self.q, self.r[0], self.r[1])

    def update(self, t):
        vec = np.array([math.sin(self.omega * t), math.sin(2 * self.omega * t)])
        self.r = self.A * vec

        vec = np.array([math.cos(self.omega * t) / 2.0, math.cos(2 * self.omega * t)])
        self.rd = self.v * vec

        vec = np.array([math.sin(self.omega * t) / 4.0, math.sin(2 * self.omega * t)])
        self.rdd = -self.q * vec

        self.rdtn = self.rd / np.linalg.norm(self.rd)

        self.rdnn = np.array([-self.rd[1], self.rd[0]]) / np.linalg.norm(self.rd)
