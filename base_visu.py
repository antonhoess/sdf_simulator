import tkinter as tk
import numpy as np
import abc
from sensor import *


__author__ = "Anton Höß"
__copyright__ = "Copyright 2020"


class BaseVisu:
    """A collection of basic visualization functionality.

    Parameters
    ----------
    canvas
        The canvas to draw on.
    """

    def __init__(self, canvas):
        self.canvas = canvas
    # end def

    def draw(self, omit_clear=False, draw_origin_cross=True):
        """Draws the very basic onto the canvas.

        Parameters
        ----------
        omit_clear : bool, optional
            Indicates if the clearing of the canvas shall be omitted.
        draw_origin_cross : bool, optional
            Indicates if the origin cross shall be drawn.
        """

        # Clear canvas
        if not omit_clear:
            self.clear()

        # Draw cross
        if draw_origin_cross:
            x0, y0 = self.canvas.scale_point(0, 0)
            x1, y1 = self.canvas.scale_point(self.canvas.winfo_width(), self.canvas.winfo_height())

            self.canvas.create_line(0, y0, 0, y1, dash=(3, 5))
            self.canvas.create_line(x0, 0, x1, 0, dash=(3, 5))
        # end if
    # end def

    def clear(self):
        """Clears the canvas."""

        self.canvas.delete(tk.ALL)
    # end def

    @staticmethod
    def draw_trace(canvas, trace, draw_arrow=True, proj_dim=0, proj_scale=1., fill_format="#000000", color="black", trace_length_max=100, **kwargs):
        """Draws a trace onto the VehicleVisu's canvas.

        Parameters
        ----------
        canvas
            Th canvas to draw on.
        trace
            The trace to be drawn.
        draw_arrow : bool, optional
            Indicates if the trace's arrow shall be drawn.
        proj_dim : int, optional
            Indicates where the traces shall be projected.
            0 / None = No projection.
            1 = Project onto X-axis.
            2 = Project onto Y-axis.
        proj_scale : float, optional
            Defines the scaling of the traces.
        fill_format : str, optional
            Defines the format string for creating the color gradient depending on the relative trace position.
        color : str
            The trace color.
        trace_length_max : int
            Max. trace length.
        **kwargs : dict, optional
            Keyword arguments passed to tkinter.Canvas.create_line().
        """

        num_steps = len(trace)

        if num_steps > 1:
            p0 = None
            p1 = None
            fill = None

            arrow = None
            capstyle = tk.ROUND

            for step in range(1, num_steps):
                x = step / float(trace_length_max - 1)

                fill = fill_format.format(int(x * 255), int((1 - x) * 255))

                p0 = trace[step - 1]
                p1 = trace[step]

                if proj_dim == 1:
                    p0 = p0 * np.asarray([1., 0.]) + np.asarray([0., (step - 1) * proj_scale])
                    p1 = p1 * np.asarray([1., 0.]) + np.asarray([0., step * proj_scale])

                elif proj_dim == 2:
                    p0 = p0 * np.asarray([0., 1.]) + np.asarray([(step - 1) * proj_scale, 0.])
                    p1 = p1 * np.asarray([0., 1.]) + np.asarray([step * proj_scale, 0.])

                canvas.create_line(p0[0],
                                   p0[1],
                                   p1[0],
                                   p1[1],
                                   fill=fill, capstyle=capstyle, arrow=arrow, **kwargs)
            # end for

            if draw_arrow:
                arrow = tk.LAST
                capstyle = None

                if color is not None:
                    fill = color

                p0 = p1 - (p1 - p0) * 1.e-10

                canvas.create_line(p0[0],
                                   p0[1],
                                   p1[0],
                                   p1[1],
                                   fill=fill, capstyle=capstyle, arrow=arrow, **kwargs)
            # end if
        # end if
    # end def

    def draw_cov_mat_ell(self, sensor, vehicle, cov_mat, cov_ell_cnt, fill, orient=False):
        """Draws the covariance ellipses.

        Parameters
        ----------
        sensor
            The sensor that did the measurement.
        vehicle
            The vehicle that was measured.
        cov_mat : numpy.ndarray
            The covariance matrix.
        cov_ell_cnt : int
            The number of covariances (standard deviations).
        fill : str
            The fill color for the ellipses.
        orient : bool
            Calculate the orientation of the covariance ellipses.
        """

        # The covariance ellipses
        if vehicle.active and cov_ell_cnt > 0:
            if sensor is not None and orient:
                theta = sensor.calc_rotation_angle(vehicle)
            else:
                theta = 0

            rad = np.linalg.norm(vehicle.r - sensor.pos)

            # Calculate values for drawing the cov ellipse
            cov_r_theta, cov_r_r1, cov_r_r2 = ISensor.calc_cov_ell_params_2d(cov_mat)
            cov_r_theta += theta
            cov_r_r1 *= rad
            cov_r_r2 *= rad * math.pi

            for sigma in range(1, cov_ell_cnt + 1):
                self.canvas.create_oval_rotated(vehicle.r[0], vehicle.r[1], cov_r_r1 * sigma, cov_r_r2 * sigma,
                                                cov_r_theta, n_segments=20, fill="", width=3, outline="black")
                self.canvas.create_oval_rotated(vehicle.r[0], vehicle.r[1], cov_r_r1 * sigma, cov_r_r2 * sigma,
                                                cov_r_theta, n_segments=20, fill="", width=1, outline=fill)
            # end for
        # end if
    # end def
# end class


class TraceVisu(abc.ABC):
    """Basic visualization class for traces.

    Parameters
    ----------
    trace_length_max : int
        Max. trace length.
    """

    def __init__(self, trace_length_max=10):
        self.trace_length_max = trace_length_max
    # end def

    def add_cur_val_to_trace(self, trace, val):
        """Updates the trace array.

        Parameters
        ----------
        trace : list
            The trace list.
        val
            Value added to the trace.
        """

        trace.append(val)

        while len(trace) > self.trace_length_max:  # Limit trace array length
            trace.pop(0)
    # end def

    @abc.abstractmethod
    def add_cur_vals_to_traces(self, **kwargs):
        pass
    # end def
# end class
