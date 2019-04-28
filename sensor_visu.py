import tkinter as tk


class SensorVisu:
    def __init__(self, sensor, canvas, color=None, meas_buf_max=100):
        self.sensor = sensor
        self.canvas = canvas
        self.color = color

        self._EDGE_LENGTH = 1500

        self._meas_buf_max = meas_buf_max

    def draw(self, omit_clear=False):
        # Clear canvas
        if not omit_clear:
            self.clear()

        # The sensor itself
        self.canvas.create_rectangle(self.sensor.r[0] - self._EDGE_LENGTH / 2.,
                                     self.sensor.r[1] - self._EDGE_LENGTH / 2.,
                                     self.sensor.r[0] + self._EDGE_LENGTH / 2.,
                                     self.sensor.r[1] + self._EDGE_LENGTH / 2.,
                                     fill=self.color, activefill="red")
        self.canvas.create_text(self.sensor.r[0], self.sensor.r[1], text=self.sensor.name, anchor=tk.CENTER)

        self.sensor.measurements = self.sensor.measurements[-self._meas_buf_max:]

        # The sensor's measurements
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

    def clear(self):
        self.canvas.delete(tk.ALL)
