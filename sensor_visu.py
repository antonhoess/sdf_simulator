import tkinter as tk


class SensorVisu:
    def __init__(self, sensor, canvas, color=None, meas_buf_max=100):
        self.sensor = sensor
        self.canvas = canvas
        self.color = color

        self._EDGE_LENGTH = 1500

        self._meas_buf_max = meas_buf_max
        self.cov_ell_cnt = 0

    def draw(self, omit_clear=False, draw_meas=True):
        # Clear canvas
        if not omit_clear:
            self.clear()

        # The sensor itself
        def cb_mouse_enter(event, item):
            event.widget.itemconfig(item, fill="red")

        def cb_mouse_leave(event, item):
            event.widget.itemconfig(item, fill=self.color)

        rect = self.canvas.create_rectangle(self.sensor.r[0] - self._EDGE_LENGTH / 2.,
                                            self.sensor.r[1] - self._EDGE_LENGTH / 2.,
                                            self.sensor.r[0] + self._EDGE_LENGTH / 2.,
                                            self.sensor.r[1] + self._EDGE_LENGTH / 2.,
                                            fill=self.color, tag="{:x}".format(id(self.sensor)))
        self.canvas.create_text(self.sensor.r[0], self.sensor.r[1], text=self.sensor.name, anchor=tk.CENTER,
                                tag="{:x}".format(id(self.sensor)))

        self.canvas.tag_bind("{:x}".format(id(self.sensor)), '<Enter>',
                             lambda event, item=rect: cb_mouse_enter(event, item))
        self.canvas.tag_bind("{:x}".format(id(self.sensor)), '<Leave>', lambda event, item=rect: cb_mouse_leave(event, item))

        # The covariance ellipses
        handled_vehicles = []
        for m in range(len(self.sensor.measurements) - 1, 0, -1):
            meas = self.sensor.measurements[m]
            if meas.vehicle not in handled_vehicles:  # XXX This only works, if all sensors have the same frequency, otherwise it can stop before all sensors got handled - change logic!
                handled_vehicles.append(meas.vehicle)

                for sigma in range(1, self.cov_ell_cnt + 1):
                    self.canvas.create_oval_rotated(meas.r_mean[0], meas.r_mean[1],  self.sensor.cov_r_r1 * sigma, self.sensor.cov_r_r2 * sigma, self.sensor.cov_r_theta, n_segments=20, fill="", width=3, outline="black")
                    self.canvas.create_oval_rotated(meas.r_mean[0], meas.r_mean[1],  self.sensor.cov_r_r1 * sigma, self.sensor.cov_r_r2 * sigma, self.sensor.cov_r_theta, n_segments=20, fill="", width=1, outline=self.color)
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
                    self.canvas.create_line(meas.r[0] - x, meas.r[1] - x, meas.r[0] + x, meas.r[1] + x, width=3, fill="black")
                    self.canvas.create_line(meas.r[0] - x, meas.r[1] + x, meas.r[0] + x, meas.r[1] - x, width=3, fill="black")

                    self.canvas.create_line(meas.r[0] - x, meas.r[1] - x, meas.r[0] + x, meas.r[1] + x, width=1, fill=self.color)
                    self.canvas.create_line(meas.r[0] - x, meas.r[1] + x, meas.r[0] + x, meas.r[1] - x, width=1, fill=self.color)
                else:  # ❌
                    self.canvas.create_text(meas.r[0], meas.r[1], text="❌", anchor=tk.CENTER, font=(None, 12), fill="black")
                    self.canvas.create_text(meas.r[0], meas.r[1], text="❌", anchor=tk.CENTER, font=(None, 8), fill=self.color)
                # end if
            # end for
        # end if

    def clear(self):
        self.canvas.delete(tk.ALL)
