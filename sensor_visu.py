import tkinter as tk
import math
import numpy as np
from base_visu import BaseVisu


class SensorVisu:
    def __init__(self, sensor, canvas, fill=None, outline=None, radius=2500, n_sides=4, rot_offset=math.pi/4, font_size_scale=1., trace_length_max=10, meas_buf_max=100):
        self.sensor = sensor
        self.canvas = canvas
        self.fill = fill
        self.outline = outline

        self._radius = radius
        self._n_sides = n_sides
        self._rot_offset = rot_offset
        self._font_size_scale = font_size_scale
        self.trace_length_max = trace_length_max
        self.meas_buf_max = meas_buf_max
        self.cov_ell_cnt = 0

        self._trace_pos_filtered = {}

    def add_cur_vals_to_traces(self):
        self.add_cur_pos_filtered_to_trace()

    # Update trace array
    def add_cur_val_to_trace(self, trace, val):
        trace.append(val)

        while len(trace) > self.trace_length_max:  # Limit trace array length
            trace.pop(0)

    # Update filtered pos trace array
    def add_cur_pos_filtered_to_trace(self):
        for vehicle in self.sensor.kalman_filter:
            if vehicle not in self._trace_pos_filtered:
                self._trace_pos_filtered[vehicle] = []

            self.add_cur_val_to_trace(self._trace_pos_filtered[vehicle], self.sensor.kalman_filter[vehicle].get_current_state_estimate())
        # end for

    def _draw_trace(self, trace, draw_arrow=True, fill_format="#000000", **kwargs):
        BaseVisu.draw_trace(self.canvas, trace=trace, draw_arrow=draw_arrow, fill_format=fill_format, color=self.fill, trace_length_max=self.trace_length_max, **kwargs)

    def draw(self, draw_meas=True, vehicles=None, draw_meas_filtered=True):
        # The sensor itself
        def cb_mouse_enter(event, item):
            event.widget.itemconfig(item, fill="red")

        def cb_mouse_leave(event, item):
            event.widget.itemconfig(item, fill=self.fill)

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

        if vehicle is not None:
            angle = self.sensor.calc_rotation_angle(vehicle)  # Look to the first vehicle
        else:
            angle = 0.

        ps = []
        for i in range(self._n_sides):
            theta = math.pi * 2. / float(self._n_sides) * float(i) + angle + self._rot_offset
            R = self.sensor.calc_rotation_matrix(theta)

            p = np.dot(np.asarray([self._radius / 2, 0]), R.T) + self.sensor.r
            ps.append(p[0])
            ps.append(p[1])
        # end for

        shape = self.canvas.create_polygon(ps, fill=self.fill, outline=self.outline, tag="{:x}".format(id(self.sensor)))
        font_size = int(self.canvas.scale_factor * self.canvas.zoom * self.canvas.ratio_scale_factor * 1.e03 * self._font_size_scale)

        if vehicle is not None:
            self.canvas.create_line(self.sensor.r[0], self.sensor.r[1], vehicle.r[0], vehicle.r[1], fill=self.outline, dash=(2, 5))

        self.canvas.create_text(self.sensor.r[0], self.sensor.r[1], text=self.sensor.name, fill=self.outline, font=(None, font_size),
                                anchor=tk.CENTER, tag="{:x}".format(id(self.sensor)))

        self.canvas.tag_bind("{:x}".format(id(self.sensor)), '<Enter>',
                             lambda event, item=shape: cb_mouse_enter(event, item))
        self.canvas.tag_bind("{:x}".format(id(self.sensor)), '<Leave>',
                             lambda event, item=shape: cb_mouse_leave(event, item))

        # For each vehicle draw the measurement information
        for vehicle in vehicles:
            # The covariance ellipses
            if vehicle.active and self.cov_ell_cnt > 0:
                theta = self.sensor.calc_rotation_angle(vehicle)

                # Calculate values for drawing the cov ellipse
                cov_r_theta, cov_r_r1, cov_r_r2 = self.sensor.calc_cov_ell_params(np.asarray(self.sensor.cov_r))
                cov_r_theta += theta

                for sigma in range(1, self.cov_ell_cnt + 1):
                    self.canvas.create_oval_rotated(vehicle.r[0], vehicle.r[1], cov_r_r1 * sigma, cov_r_r2 * sigma,
                                                    cov_r_theta, n_segments=20, fill="", width=3, outline="black")
                    self.canvas.create_oval_rotated(vehicle.r[0], vehicle.r[1], cov_r_r1 * sigma, cov_r_r2 * sigma,
                                                    cov_r_theta, n_segments=20, fill="", width=1, outline=self.fill)
                # end for
            # end if

            # The sensor's measurements
            measurements = []
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
                        self.canvas.create_oval(meas.r[0], meas.r[1], meas.r[0], meas.r[1], width=5, outline="black")
                        self.canvas.create_oval(meas.r[0], meas.r[1], meas.r[0], meas.r[1], width=3, outline=self.fill)
                    elif x_style == 1:  # \ + /
                        x = 100
                        self.canvas.create_line(meas.r[0] - x, meas.r[1] - x, meas.r[0] + x, meas.r[1] + x, width=3,
                                                fill="black")
                        self.canvas.create_line(meas.r[0] - x, meas.r[1] + x, meas.r[0] + x, meas.r[1] - x, width=3,
                                                fill="black")

                        self.canvas.create_line(meas.r[0] - x, meas.r[1] - x, meas.r[0] + x, meas.r[1] + x, width=1,
                                                fill=self.fill)
                        self.canvas.create_line(meas.r[0] - x, meas.r[1] + x, meas.r[0] + x, meas.r[1] - x, width=1,
                                                fill=self.fill)
                    else:  # ❌
                        self.canvas.create_text(meas.r[0], meas.r[1], text="❌", anchor=tk.CENTER, font=(None, 12),
                                                fill="black")
                        self.canvas.create_text(meas.r[0], meas.r[1], text="❌", anchor=tk.CENTER, font=(None, 8),
                                                fill=self.fill)
                    # end if
                # end for
            # end if

            if draw_meas_filtered:
                for vehicle in self._trace_pos_filtered:
                    if vehicle.active:
                        self._draw_trace(self._trace_pos_filtered[vehicle], draw_arrow=True, fill_format="#000000", width=1.0)
            # end if
        # end for

    def clear(self):
        self.canvas.delete(tk.ALL)
