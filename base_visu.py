import tkinter as tk
import numpy as np
import abc


class BaseVisu:
    def __init__(self, canvas):
        self.canvas = canvas

    def draw(self, omit_clear=False, draw_origin_cross=True):
        # Clear canvas
        if not omit_clear:
            self.clear()

        # Draw cross
        if draw_origin_cross:
            x0, y0 = self.canvas.scale_point(0, 0)
            x1, y1 = self.canvas.scale_point(self.canvas.winfo_width(), self.canvas.winfo_height())

            self.canvas.create_line(0, y0, 0, y1, dash=(3, 5))
            self.canvas.create_line(x0, 0, x1, 0, dash=(3, 5))

    def clear(self):
        self.canvas.delete(tk.ALL)

    # proj_dim = projection dimension: 0 = No projection, 1 = X-axis, 2 = Y-axis
    @staticmethod
    def draw_trace(canvas, trace, draw_arrow=True, proj_dim=0, proj_scale=1., fill_format="#000000", color="black", trace_length_max=100, **kwargs):
        num_steps = len(trace)

        for step in range(1, num_steps):
            x = step / float(trace_length_max - 1)

            fill = fill_format.format(int(x * 255), int((1 - x) * 255))

            if draw_arrow and step == num_steps - 1:
                arrow = tk.LAST
                capstyle = None

                if color is not None:
                    fill = color
            else:
                arrow = None
                capstyle = tk.ROUND

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


class TraceVisu(abc.ABC):
    def __init__(self, trace_length_max=10):
        self.trace_length_max = trace_length_max

    # Update trace array
    def add_cur_val_to_trace(self, trace, val):
        trace.append(val)

        while len(trace) > self.trace_length_max:  # Limit trace array length
            trace.pop(0)

    @abc.abstractmethod
    def add_cur_vals_to_traces(self, **kwargs):
        pass
