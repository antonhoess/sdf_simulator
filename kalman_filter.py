import numpy as np


class KalmanFilter:
    # x_init: Initial state vector: What we know about the (probable) start state
    # P_init: Initial (uncertainty) covariance matrix: How sure are we about the start state - in each dimension?
    # F     : State transition matrix: For predicting the next state from the current state
    # B     : Control matrix: For predicting the next state from the current state using control signals
    # Q     : Process noise covariance matrix: Describes the (Gaussian) randomness of
    #         state transitions in each dimension
    # H     : Measurement matrix: Describes how we think that our sensors map states to measurements z
    # R     : Measurement noise covariance matrix: Describes the (Gaussian) randomness of measurements per dimension
    def __init__(self, x_init, P_init, F, B, Q, H, R):
        self.x = x_init
        self.P = P_init
        self.F = F
        self.B = B
        self.Q = Q
        self.H = H
        self.R = R

    # Predicts the new state vector x using the transition matrix F and the specified control vector u and updates the
    # uncertainty covariance matrix F embodies our knowledge about the system dynamics
    def predict(self, u):
        # Predict new state
        self.x = self.F * self.x + self.B * u

        # Update uncertainty covariance matrix
        self.P = self.F * self.P * self.F.T + self.Q

    def filter(self, z):
        # Compute innovation y
        y = z - self.H * self.x

        # Compute residual covariance matrix S
        S = self.H * self.P * self.H.T + self.R

        # Compute Kalman gain matrix the Kalman gain matrix tells us how strongly to correct each dimension of the
        # predicted state vector by the help of the measurement
        K = self.P * self.H.T * S.inv()

        # Correct previously predicted new state vector
        self.x = self.x + K * y

        # Update uncertainty covariance matrix
        self.P = self.P - K * self.H * self.P

    # Returns the current estimated state vector x, may it be after the predict() or
    # after the correct_by_measurement() step
    def get_current_state_estimate(self):
        return self.x

    # Returns the current estimated uncertainty covariance matrix P may it be after the predict() or after the
    # correct_by_measurement() step the covariance matrix describes the variance of each state vector argument
    # = uncertainty about this argument of the state vector
    def get_current_uncertainty(self):
        return self.P
