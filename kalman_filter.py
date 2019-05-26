import numpy as np


class KalmanFilter:
    def __init__(self, x_init, P_init, F, B, Q, H, R):
        """ Constructor of the The N-dimensional Kalman filter

        Parameters:
        x_init (array): Initial state vector: What we know about the (probable) start state
        P_init (array): Initial (uncertainty) covariance matrix: How sure are we about the start state - in each dimension?
        F      (array): State transition matrix: For predicting the next state from the current state
        B      (array): Control matrix: For predicting the next state from the current state using control signals
        Q      (array): Process noise covariance matrix: Describes the (Gaussian) randomness of state transitions in each dimension
        H      (array): Measurement matrix: Describes how we think that our sensors map states to measurements z
        R      (array): Measurement noise covariance matrix: Describes the (Gaussian) randomness of measurements per dimension

        Returns:
        An initialized Kalman filter object which can be used for further filtering.
        """

        self.x = x_init
        self.P = P_init
        self.F = F
        self.B = B
        self.Q = Q
        self.H = H
        self.R = R

    # Predicts the new state vector x using the transition matrix F and the specified control vector u and updates the
    # uncertainty covariance
    # Matrix F embodies our knowledge about the system dynamics
    def predict(self, u, F=None, f=None):
        if F is not None:
            self.F = F

        # Predict new state
        if f is None:
            self.x = np.dot(self.F, self.x) + np.dot(self.B, u)
        else:
            self.x = f(self.x) + np.dot(self.B, u)

        # Update uncertainty covariance matrix
        self.P = np.dot(self.F, np.dot(self.P, self.F.T)) + self.Q

    def filter(self, z, R=None, H=None, h=None):
        if R is not None:
            self.R = R

        if H is not None:
            self.H = H

        # Compute innovation y
        if h is None:
            y = z - np.dot(self.H, self.x)
        else:
            y = z - h(self.x)

        # Compute residual covariance matrix S
        S = np.dot(self.H, np.dot(self.P, self.H.T)) + self.R

        # Compute Kalman gain matrix the Kalman gain matrix tells us how strongly to correct each dimension of the
        # predicted state vector by the help of the measurement
        K = np.dot(self.P, np.dot(self.H.T, np.linalg.inv(S)))

        # Correct previously predicted new state vector
        self.x = self.x + np.dot(K, y)

        # Update uncertainty covariance matrix
        self.P = self.P - np.dot(K, np.dot(self.H, self.P))

    # Returns the current estimated state vector x, may it be after the predict() or
    # after the correct_by_measurement() step
    def get_current_state_estimate(self):
        return self.x

    # Returns the current estimated uncertainty covariance matrix P may it be after the predict() or after the
    # correct_by_measurement() step the covariance matrix describes the variance of each state vector argument
    # = uncertainty about this argument of the state vector
    def get_current_uncertainty(self):
        return self.P

    @staticmethod
    def join_measurements(R_z_list, mode=1):
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
