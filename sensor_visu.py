import tkinter as tk
import math
import numpy as np


class SensorVisu:
    def __init__(self, sensor, canvas, color=None, meas_buf_max=100):
        self.sensor = sensor
        self.canvas = canvas
        self.color = color

        self._RADIUS = 2500

        self._meas_buf_max = meas_buf_max
        self.cov_ell_cnt = 0

    def draw(self, omit_clear=False, draw_meas=True, vehicle=None):
        # Clear canvas
        if not omit_clear:
            self.clear()

        # The sensor itself
        def cb_mouse_enter(event, item):
            event.widget.itemconfig(item, fill="red")

        def cb_mouse_leave(event, item):
            event.widget.itemconfig(item, fill=self.color)

        if vehicle is not None:
            angle = math.atan2(vehicle.r[1] - self.sensor.r[1], vehicle.r[0] - self.sensor.r[0])
        else:
            angle = 0

        ps = []
        n_sides = 4
        for i in range(n_sides):
            theta = math.pi * 2. / float(n_sides) * float(i) + angle
            c, s = np.cos(theta), np.sin(theta)
            R = np.array(((c, -s), (s, c)))  # Rotation matrix

            p = np.dot(np.asarray([self._RADIUS / 2, 0]), R.T) + self.sensor.r
            ps.append(p[0])
            ps.append(p[1])
        # end for

        shape = self.canvas.create_polygon(ps, fill=self.color, outline="black", tag="{:x}".format(id(self.sensor)))
        font_size = int(self.canvas.scale_factor * self.canvas.zoom * self.canvas.ratio_scale_factor * 1.e03)
        print(font_size)
        self.canvas.create_line(self.sensor.r[0], self.sensor.r[1], vehicle.r[0], vehicle.r[1], dash=(2, 5))
        self.canvas.create_text(self.sensor.r[0], self.sensor.r[1], text=self.sensor.name, font=(None, font_size),
                                anchor=tk.CENTER, tag="{:x}".format(id(self.sensor)))

        self.canvas.tag_bind("{:x}".format(id(self.sensor)), '<Enter>',
                             lambda event, item=shape: cb_mouse_enter(event, item))
        self.canvas.tag_bind("{:x}".format(id(self.sensor)), '<Leave>',
                             lambda event, item=shape: cb_mouse_leave(event, item))

        # The covariance ellipses
        handled_vehicles = []
        for m in range(len(self.sensor.measurements) - 1, 0, -1):
            meas = self.sensor.measurements[m]
            if meas.vehicle not in handled_vehicles:  # XXX This only works, if all sensors have the same frequency, otherwise it can stop before all sensors got handled - change logic!
                handled_vehicles.append(meas.vehicle)

                for sigma in range(1, self.cov_ell_cnt + 1):
                    self.canvas.create_oval_rotated(meas.r_mean[0], meas.r_mean[1], self.sensor.cov_r_r1 * sigma,
                                                    self.sensor.cov_r_r2 * sigma, self.sensor.cov_r_theta,
                                                    n_segments=20, fill="", width=3, outline="black")
                    self.canvas.create_oval_rotated(meas.r_mean[0], meas.r_mean[1], self.sensor.cov_r_r1 * sigma,
                                                    self.sensor.cov_r_r2 * sigma, self.sensor.cov_r_theta,
                                                    n_segments=20, fill="", width=1, outline=self.color)
                # end for
            else:
                break
            # end if
        # end for

        self.sensor.measurements = self.sensor.measurements[-self._meas_buf_max:]

        # The sensor's measurements
        if draw_meas:
            x_style = 1
            for meas in self.sensor.measurements:
                if x_style == 0:  # Point
                    self.canvas.create_oval(meas.r[0], meas.r[1], meas.r[0], meas.r[1], width=5, outline="black")
                    self.canvas.create_oval(meas.r[0], meas.r[1], meas.r[0], meas.r[1], width=3, outline=self.color)
                elif x_style == 1:  # \ + /
                    x = 100
                    self.canvas.create_line(meas.r[0] - x, meas.r[1] - x, meas.r[0] + x, meas.r[1] + x, width=3,
                                            fill="black")
                    self.canvas.create_line(meas.r[0] - x, meas.r[1] + x, meas.r[0] + x, meas.r[1] - x, width=3,
                                            fill="black")

                    self.canvas.create_line(meas.r[0] - x, meas.r[1] - x, meas.r[0] + x, meas.r[1] + x, width=1,
                                            fill=self.color)
                    self.canvas.create_line(meas.r[0] - x, meas.r[1] + x, meas.r[0] + x, meas.r[1] - x, width=1,
                                            fill=self.color)
                else:  # ❌
                    self.canvas.create_text(meas.r[0], meas.r[1], text="❌", anchor=tk.CENTER, font=(None, 12),
                                            fill="black")
                    self.canvas.create_text(meas.r[0], meas.r[1], text="❌", anchor=tk.CENTER, font=(None, 8),
                                            fill=self.color)
                # end if
            # end for
        # end if

    def clear(self):
        self.canvas.delete(tk.ALL)
