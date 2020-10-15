import tkinter as tk
import math
import numpy as np
from base_visu import *
from sensor import *


__author__ = "Anton Höß"
__copyright__ = "Copyright 2020"


class SensorVisu(BaseVisu, TraceVisu):
    """A sensor's visualization.

    Parameters
    ----------
    sensor
        The ISensor to draw.
    canvas
        The canvas to draw the ISensor on.
    fill : str, optional
        The polygon's fill color.
    outline : str, optional
        The polygon's outline color.
    radius : float, optional
        The polygon's radius.
    n_sides : int, optional
        Number of sides of the polygon sued to visualize.
    rot_offset : float, optional
        The polygon's rotation offset angle.
    font_size_scale : float, optional
        The relative text size (scales depending on the zoom factor, mulitplied by this scale factor) of the sensor's name drawn within the polygon.
    trace_length_max : int, optional
        The max. trace length for drawing the trace.
    meas_buf_max : int, optional
        The max. measurement buffer length (needs to be at least as long as trace_length_max, which can be adjusted during runtime.
    """

    def __init__(self, sensor, canvas, fill=None, outline=None, radius=2500, n_sides=4, rot_offset=None, font_size_scale=1., trace_length_max=10, meas_buf_max=100):
        BaseVisu.__init__(self, canvas)
        TraceVisu.__init__(self, trace_length_max)

        self.sensor = sensor
        self.canvas = canvas
        self.fill = fill
        self.outline = outline

        self._radius = radius
        self._n_sides = n_sides
        if rot_offset is None:
            if n_sides % 2 == 1:
                self._rot_offset = math.pi / 2
            else:
                self._rot_offset = math.pi / 2 + math.pi / n_sides
        else:
            self._rot_offset = rot_offset

        self._font_size_scale = font_size_scale
        self.meas_buf_max = meas_buf_max
        self.cov_ell_cnt = 0

        self._trace_pos = dict()
    # end def

    def add_cur_vals_to_traces(self, vehicle=None):
        """Adds the current measurement of the vehicle to its corresponding trace.

        Parameters
        ----------
        vehicle, optional
            The vehicle who's trace to add the position to.
        """

        self.add_cur_pos_to_trace(vehicle)
    # end def

    # Update filtered pos trace array
    def add_cur_pos_to_trace(self, vehicle):
        """Adds the current measurement of the vehicle to its corresponding trace.

        Parameters
        ----------
        vehicle
            The vehicle who's trace to add the position to.
        """

        if vehicle not in self._trace_pos:
            self._trace_pos[vehicle] = list()

        self.add_cur_val_to_trace(self._trace_pos[vehicle], self.sensor.measurements[vehicle][-1].get_abs_cartesian())
    # end def

    def _draw_trace(self, trace, draw_arrow=True, fill_format="#000000", **kwargs):
        """Draws a trace onto the SensorVisu's canvas.

        Parameters
        ----------
        trace
            The trace to be drawn.
        draw_arrow : bool, optional
            Indicates if the trace's arrow shall be drawn.
        fill_format : str, optional
            Defines the format string for creating the color gradient depending on the relative trace position.
        **kwargs : dict, optional
            Keyword arguments passed to tkinter.Canvas.create_line().
        """

        BaseVisu.draw_trace(self.canvas, trace=trace, draw_arrow=draw_arrow, fill_format=fill_format, color=self.fill, trace_length_max=self.trace_length_max, **kwargs)
    # end def

    def draw(self, draw_meas=True, vehicles=None):
        """Draws the sensor, the measurement lines to each vehicle, and the measurements (confidence ellipses) the SensorVisu's canvas.
        When hovering the sensor with the mouse cursor, it's color changes to red.

        Parameters
        ----------
        draw_meas : bool
            Indicates if the measurements shall be drawn.
        vehicles, optional
            List of vehicles to draw the measurement information for.
        """

        # The sensor itself
        def cb_mouse_enter(event, item):
            event.widget.itemconfig(item, fill="red")
        # end def

        def cb_mouse_leave(event, item):
            event.widget.itemconfig(item, fill=self.fill)
        # end def

        if not isinstance(vehicles, list):
            vehicles = [vehicles]

        # Draw the sensor box itself
        vehicle = None

        for v in vehicles:
            if v.active:
                vehicle = v
                break
            # end if
        # end for

        if vehicle is not None and isinstance(self.sensor, Radar):
            angle = self.sensor.calc_rotation_angle(vehicle)  # Look to the first vehicle
        else:
            angle = 0.
        # end if

        ps = list()
        for i in range(self._n_sides):
            theta = math.pi * 2. / float(self._n_sides) * float(i) + angle + self._rot_offset
            R = self.sensor.calc_rotation_matrix_2d(theta)

            p = np.dot(np.asarray([self._radius / 2, 0]), R.T) + self.sensor.pos
            ps.append(p[0])
            ps.append(p[1])
        # end for

        shape = self.canvas.create_polygon(ps, fill=self.fill, outline=self.outline, tag="{:x}".format(id(self.sensor)))
        font_size = int(self.canvas.scale_factor * self.canvas.zoom * self.canvas.ratio_scale_factor * 1.e03 * self._font_size_scale)

        if vehicle is not None:
            self.canvas.create_line(self.sensor.pos[0], self.sensor.pos[1], vehicle.r[0], vehicle.r[1], fill=self.outline, dash=(2, 5))
        # end if

        self.canvas.create_text(self.sensor.pos[0], self.sensor.pos[1], text=self.sensor.name, fill=self.outline, font=(None, font_size),
                                anchor=tk.CENTER, tag="{:x}".format(id(self.sensor)))

        self.canvas.tag_bind("{:x}".format(id(self.sensor)), '<Enter>',
                             lambda event, item=shape: cb_mouse_enter(event, item))
        self.canvas.tag_bind("{:x}".format(id(self.sensor)), '<Leave>',
                             lambda event, item=shape: cb_mouse_leave(event, item))

        # For each vehicle draw the measurement information
        for vehicle in vehicles:
            # The covariance ellipses
            if self.sensor.cov_mat_draw:
                self.draw_cov_mat_ell(self.sensor, vehicle, self.sensor.cov_mat, self.cov_ell_cnt, self.fill, orient=isinstance(self.sensor, Radar))

            # The sensor's measurements
            measurements = list()
            if vehicle in self.sensor.measurements:
                self.sensor.measurements[vehicle] = self.sensor.measurements[vehicle][-self.meas_buf_max:]
                measurements = self.sensor.measurements[vehicle]
            # end if

            if draw_meas:
                x_style = 1
                for meas in measurements:
                    if meas.vehicle is not vehicle or not vehicle.active:
                        continue

                    if x_style == 0:  # Point
                        self.canvas.create_oval(meas.val[0], meas.val[1], meas.val[0], meas.val[1], width=5, outline="black")
                        self.canvas.create_oval(meas.val[0], meas.val[1], meas.val[0], meas.val[1], width=3, outline=self.fill)
                    elif x_style == 1:  # \ + /
                        x = 100
                        self.canvas.create_line(meas.val[0] - x, meas.val[1] - x, meas.val[0] + x, meas.val[1] + x, width=3,
                                                fill="black")
                        self.canvas.create_line(meas.val[0] - x, meas.val[1] + x, meas.val[0] + x, meas.val[1] - x, width=3,
                                                fill="black")

                        self.canvas.create_line(meas.val[0] - x, meas.val[1] - x, meas.val[0] + x, meas.val[1] + x, width=1,
                                                fill=self.fill)
                        self.canvas.create_line(meas.val[0] - x, meas.val[1] + x, meas.val[0] + x, meas.val[1] - x, width=1,
                                                fill=self.fill)
                    else:  # ❌
                        self.canvas.create_text(meas.val[0], meas.val[1], text="❌", anchor=tk.CENTER, font=(None, 12),
                                                fill="black")
                        self.canvas.create_text(meas.val[0], meas.val[1], text="❌", anchor=tk.CENTER, font=(None, 8),
                                                fill=self.fill)
                    # end if
                # end for
            # end if
        # end for
    # end def
# end class
