from kalman_filter import *
from enum import IntEnum
import numpy as np


class KalmanFilterType(IntEnum):
    PLANE_2D = 1
    POLAR_2D = 2


class KalmanFilterFactory:
    def __init__(self):
        pass

    @staticmethod
    def get_kalman_filter(filter_type, meas_interval, cov_mat, q_sigma, x_init=None, P_init=None, F=None, B=None, Q=None, H=None, R=None, cb_f=None, cb_F=None, cb_h=None, cb_H=None):
        # KF
        _x_init = None
        _P_init = None
        _F = None
        _B = None
        _Q = None
        _H = None
        _R = None

        # EKF
        _cb_f = None
        _cb_F = None
        _cb_h = None
        _cb_H = None

        if filter_type == KalmanFilterType.PLANE_2D:
            DIM = 2
            STATE_COMP = 3  # r, rd, rdd
            DT = meas_interval

            I = np.identity(DIM)
            O = np.zeros((DIM, DIM))

            _x_init = np.zeros(DIM * STATE_COMP)
            _P_init = np.identity(DIM * STATE_COMP) * 1.e10
            _F = np.block([[I, DT * I, 0.5 * DT**2 * I],
                          [O, I, DT * I],
                          [O, I, I]])
            Σ = q_sigma
            G = np.block([[0.5 * DT**2 * I],
                          [DT * I],
                          [I]])
            _Q = np.dot(G, G.T) * Σ ** 2
            _H = np.block([I, O, O])
            _B = np.identity(DIM * STATE_COMP)
            _R = cov_mat
        elif filter_type == KalmanFilterType.POLAR_2D:
            def cb_h(pos_cartesian):
                x = pos_cartesian[0]
                y = pos_cartesian[1]

                rho = np.linalg.norm(pos_cartesian)
                phi = np.arctan2(y, x)

                return np.asarray([rho, phi])

            def cb_H(_pos_cartesian):
                return np.block([I, O, O])  # XXX

            DIM = 2
            STATE_COMP = 3  # r, rd, rdd
            DT = meas_interval

            I = np.identity(DIM)
            O = np.zeros((DIM, DIM))

            _x_init = np.zeros(DIM * STATE_COMP)
            _P_init = np.identity(DIM * STATE_COMP) * 1.e10
            _F = np.block([[I, DT * I, 0.5 * DT**2 * I],
                          [O, I, DT * I],
                          [O, I, I]])
            Σ = q_sigma
            G = np.block([[0.5 * DT**2 * I],
                          [DT * I],
                          [I]])
            _Q = np.dot(G, G.T) * Σ ** 2
            _H = None
            _B = np.identity(DIM * STATE_COMP)
            _R = cov_mat

            _cb_h = cb_h
            _cb_H = cb_H
        # end if

        # KF
        if x_init is not None:
            _x_init = x_init

        if P_init is not None:
            _P_init = P_init

        if F is not None:
            _F = F

        if B is not None:
            _B = B

        if Q is not None:
            _Q = Q

        if H is not None:
            _H = H

        if R is not None:
            _R = R

        # EKF
        if cb_f is not None:
            _cb_f = cb_f

        if cb_F is not None:
            _cb_F = cb_F

        if cb_h is not None:
            _cb_h = cb_h

        if cb_H is not None:
            _cb_H = cb_H

        return EKF(_x_init, _P_init, _F, _B, _Q, _H, _R, cb_f, cb_F, cb_h, cb_H)
