import numpy as np


__author__ = "Anton Höß"
__copyright__ = "Copyright 2020"


class EKF:
    """Creates a N-dimensional Kalman filter.

    Parameters
    ----------
    x_init : numpy.ndarray, optional
        Initial state vector: What we know about the (probable) start state.
    P_init : numpy.ndarray, optional
        Initial (uncertainty) covariance matrix: How sure are we about the start state - in each dimension?
    F : numpy.ndarray, optional
        State transition matrix: For predicting the next state from the current state.
    B : numpy.ndarray, optional
        Control matrix: For predicting the next state from the current state using control signals.
    Q : numpy.ndarray, optional
        Process noise covariance matrix: Describes the (Gaussian) randomness of state transitions in each dimension.
    H : numpy.ndarray, optional
        Measurement matrix: Describes how we think that our sensors map states to measurements z.
    R : numpy.ndarray, optional
        Measurement noise covariance matrix: Describes the (Gaussian) randomness of measurements per dimension.
    cb_f : callable, optional
        Callback that predicts a point in the state space (necessary for the EKF). If set, overwrites F.
    cb_F : callable, optional
        Callback that returns the matrix F (calculated for the current time).
    cb_h : callable, optional
        Callback that transforms a point from the state space to the measurement space (necessary for the EKF). If set, overwrites H.
    cb_H : callable, optional
        Callback that returns the matrix H (calculated for the current time).
    init_with_first_meas : bool
        Indicates if the first measurement shall be used to initialize the filters extimated position.

    Returns
    -------
    EKF
        An initialized (Extended) Kalman filter object which can be used for further filtering.
    """

    def __init__(self, x_init, P_init, F, B, Q, H, R, cb_f=None, cb_F=None, cb_h=None, cb_H=None, init_with_first_meas=False):
        # KF
        self.x = x_init
        self.P = P_init
        self.F = F
        self.B = B
        self.Q = Q
        self.H = H
        self.R = R

        # EKF
        self.f = cb_f
        self.cb_F = cb_F
        self.h = cb_h
        self.cb_H = cb_H

        if bool(self.f is None) != bool(self.cb_F is None):
            raise ValueError("cb_f() and cb_F() need to be set both or none of them.")

        if bool(self.h is None) != bool(self.cb_H is None):
            raise ValueError("cb_h() and cb_H() need to be set both or none of them.")

        self._inited = not init_with_first_meas  # Makes the first measurement used as the initial state
    # end def

    def predict(self, u):
        """Predicts the new state vector x using the transition matrix F and the specified control vector u and updates the uncertainty covariance. Matrix F embodies our knowledge about the system dynamics.

        Parameters
        ----------
        u : numpy.ndarray
            Control vector applied by the control-input-model B.
        """
        if not self._inited:
            return

        # Predict new state
        if self.f is None:
            self.x = np.dot(self.F, self.x) + np.dot(self.B, u)
        else:
            self.x = self.f(self.x) + np.dot(self.B, u)

        if self.cb_F is not None:
            self.F = self.cb_F(self.x)

        # Update uncertainty covariance matrix
        self.P = np.dot(self.F, np.dot(self.P, self.F.T)) + self.Q
    # end def

    def filter(self, z, R=None):
        """Updates the previously predicted state by incorporating the new measurement.

        Parameters
        ----------
        z : numpy.ndarray
            Measurement vector used to update the estimation.
        R : numpy.ndarray, optional
            Measurement covariance matrix. Can be set to overwrite the initial one (in case R is not constant).
        """

        if not self._inited:
            self._inited = True
            self.x = np.pad(z, (0, len(self.x) - len(z)), 'constant')  # XXX Not correct - needs to be transformed from the measurement corrdinate system to the dynamic one's - but works, if both systems are the same

        if R is not None:
            self.R = R

        # Compute innovation y
        if self.h is None:
            y = z - np.dot(self.H, self.x)
        else:
            y = z - self.h(self.x)

        if self.cb_H is not None:
            self.H = self.cb_H(self.x)

        # Compute residual covariance matrix S
        S = np.dot(self.H, np.dot(self.P, self.H.T)) + self.R

        # Compute Kalman gain matrix the Kalman gain matrix tells us how strongly to correct each dimension of the
        # predicted state vector by the help of the measurement
        K = np.dot(self.P, np.dot(self.H.T, np.linalg.inv(S)))

        # Correct previously predicted new state vector
        self.x = self.x + np.dot(K, y)

        # Update uncertainty covariance matrix
        self.P = self.P - np.dot(K, np.dot(self.H, self.P))

    #
    def get_current_state_estimate(self):
        """Returns the current estimated state vector x, may it be after the predict() or after the correct_by_measurement() step.

        Returns
        -------
        numpy.ndarray
            Current estimated state vector x.
        """

        return self.x
    # end def

    # Returns the current estimated uncertainty covariance matrix P may it be after the predict() or after the
    # correct_by_measurement() step the covariance matrix describes the variance of each state vector argument
    # = uncertainty about this argument of the state vector
    def get_current_uncertainty(self):
        """Returns the current estimated uncertainty covariance matrix P may it be after the predict() or after the
        correct_by_measurement() step the covariance matrix describes the variance of each state vector argument
         = uncertainty about this argument of the state vector.

        Returns
        -------
        numpy.ndarray
            Current estimated uncertainty covariance matrix P.
        """

        return self.P
    # end def

    @staticmethod
    def join_measurements(R_z_list, mode=1):
        """Joins multiple measurements.

        Parameters
        ----------
        R_z_list
            List of tuples where each tuple holds the pair of R and z.
        mode : int
            If mode equals 1, the inverse of the sum of all inverted measurements is being used.  Mode 0 (stacking of measurements) is not implemented yet.
        """

        R_res = None
        z_res = None

        if mode == 0:
            pass
        else:  # if mode == 1
            if not isinstance(R_z_list, list):
                R_z_list = [R_z_list]

            # Calculate R and z
            R_res = 0
            z_res = 0

            for R, z in R_z_list:
                R_res += np.linalg.inv(R)
                z_res += np.dot(np.linalg.inv(R), z)

            R_res = np.linalg.inv(R_res)
            z_res = np.dot(z_res, R_res)
        # end if

        return R_res, z_res
    # end def


class KF(EKF):
    """Creates a Kalman filter (as a special case of the Extended Kalman filter). See description of class EKF."""

    def __init__(self, x_init, P_init, F, B, Q, H, R, init_with_first_meas=False):
        EKF.__init__(self, x_init, P_init, F, B, Q, H, R, init_with_first_meas=init_with_first_meas)
    # end def
# end class
