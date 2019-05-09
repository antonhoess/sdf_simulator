import tkinter as tk
import math
import numpy as np


class SensorVisu:
    def __init__(self, sensor, canvas, fill=None, outline=None, radius=2500, n_sides=4, rot_offset=math.pi/4, font_size_scale=1., meas_buf_max=100):
        self.sensor = sensor
        self.canvas = canvas
        self.fill = fill
        self.outline = outline

        self._radius = radius
        self._n_sides = n_sides
        self._rot_offset = rot_offset
        self._font_size_scale = font_size_scale
        self._meas_buf_max = meas_buf_max
        self.cov_ell_cnt = 0

    def draw(self, omit_clear=False, draw_meas=True, vehicles=None):
        # Clear canvas
        if not omit_clear:
            self.clear()

        # The sensor itself
        def cb_mouse_enter(event, item):
            event.widget.itemconfig(item, fill="red")

        def cb_mouse_leave(event, item):
            event.widget.itemconfig(item, fill=self.fill)

        if not isinstance(vehicles, list):
            vehicles = [vehicles]

        # Draw the sensor box itself
        vehicle = vehicles[0]
        angle = self.sensor.calc_rotation_angle(vehicle)  # Look to the first vehicle

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
            if self.cov_ell_cnt > 0:
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
            self.sensor.measurements = self.sensor.measurements[-self._meas_buf_max:]

            if draw_meas:
                x_style = 1
                for meas in self.sensor.measurements:
                    if meas.vehicle is not vehicle:
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
        # end for

    def clear(self):
        self.canvas.delete(tk.ALL)
