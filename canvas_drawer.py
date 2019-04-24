from tkinter import *
import numpy as np


class CanvasDrawer:

    def __init__(self, vehicle, canvas, canvas_width, canvas_height, scale_factor, trace_length_max=10):
        self.vehicle = vehicle
        self.canvas = canvas
        self.canvas_width = canvas_width
        self.canvas_height = canvas_height
        self.scale_factor = scale_factor
        self.trace_length_max = trace_length_max

        self.trace_pos = []
        self.trace_vel = []
        self.trace_acc = []
        self.trace_tangent = []
        self.trace_normal = []
        self.trace_acc_times_tangent = []
        self.trace_acc_times_normal = []

    def set_canvas_width(self, canvas_width):
        self.canvas_width = canvas_width

    def set_canvas_height(self, canvas_height):
        self.canvas_height = canvas_height

    def scale_for_canvas(self, v):
        return v * self.scale_factor * np.asarray([1.0, -1.0]) +\
               np.asarray([self.canvas_width / 2, self.canvas_height / 2])

    # Update pos trace array
    def add_cur_pos_to_trace(self):
        self.trace_pos.append(self.scale_for_canvas(self.vehicle.r))

        if len(self.trace_pos) > self.trace_length_max:  # Limit trace array length
            self.trace_pos.pop(0)

    # Update vel trace array
    def add_cur_vel_to_trace(self):
        self.trace_vel.append(self.scale_for_canvas(self.vehicle.rd * 20.0))

        if len(self.trace_vel) > self.trace_length_max:  # Limit trace array length
            self.trace_vel.pop(0)

    # Update acc trace array
    def add_cur_acc_to_trace(self):
        self.trace_acc.append(self.scale_for_canvas(self.vehicle.rdd * 1000.0))

        if len(self.trace_acc) > self.trace_length_max:  # Limit trace array length
            self.trace_acc.pop(0)

    # Update tangent trace array
    def add_cur_tangent_to_trace(self):
        self.trace_tangent.append(self.scale_for_canvas(self.vehicle.rdt * 10000.0))

        if len(self.trace_tangent) > self.trace_length_max:  # Limit trace array length
            self.trace_tangent.pop(0)

    # Update normal trace array
    def add_cur_normal_to_trace(self):
        self.trace_normal.append(self.scale_for_canvas(self.vehicle.rdn * 10000.0))

        if len(self.trace_normal) > self.trace_length_max:  # Limit trace array length
            self.trace_normal.pop(0)

    # Update acc times tangent trace array
    def add_cur_acc_times_tangent_to_trace(self):
        self.trace_acc_times_tangent.append(self.scale_for_canvas(self.vehicle.rddxrdt * 1000.0))

        if len(self.trace_acc_times_tangent) > self.trace_length_max:  # Limit trace array length
            self.trace_acc_times_tangent.pop(0)

    # Update acc times normal trace array
    def add_cur_acc_times_normal_to_trace(self):
        self.trace_acc_times_normal.append(self.scale_for_canvas(self.vehicle.rddxrdn * 1000.0))

        if len(self.trace_acc_times_normal) > self.trace_length_max:  # Limit trace array length
            self.trace_acc_times_normal.pop(0)

    def reset_traces(self):
        self.trace_pos.clear()
        self.trace_vel.clear()
        self.trace_acc.clear()
        self.trace_tangent.clear()
        self.trace_normal.clear()
        self.trace_acc_times_tangent.clear()
        self.trace_acc_times_normal.clear()

    def clear(self):
        self.canvas.delete("all")

    def draw(self, draw_pos_trace=True, draw_vel_trace=True, draw_acc_trace=True, draw_tangent_trace=True,
             draw_normal_trace=True, draw_acc_times_tangent_trace=True, draw_acc_times_normal_trace=True,
             draw_vel_vec=True, draw_acc_vec=True, draw_tangent=True, draw_normal=True):

        # Clear canvas
        self.canvas.delete("all")

        # Draw trace arrays
        # -----------------
        # Draw pos trace array
        if draw_pos_trace:
            num_steps = len(self.trace_pos)
            for step in range(1, num_steps):
                x = step / float(self.trace_length_max - 1)
                self.canvas.create_line(self.trace_pos[step - 1][0],
                                        self.trace_pos[step - 1][1],
                                        self.trace_pos[step][0],
                                        self.trace_pos[step][1],
                                        width=5.0, capstyle=ROUND,
                                        fill="#{0:02x}00{1:02x}".format(int(x * 255), int((1 - x) * 255)),
                                        arrow=(LAST if step == num_steps-1 else None),
                                        arrowshape=(16, 20, 6))
            # end for
        # end if

        # Draw vel trace array
        if draw_vel_trace:
            num_steps = len(self.trace_vel)
            for step in range(1, num_steps):
                x = step / float(self.trace_length_max - 1)
                self.canvas.create_line(self.trace_vel[step - 1][0],
                                        self.trace_vel[step - 1][1],
                                        self.trace_vel[step][0],
                                        self.trace_vel[step][1],
                                        width=2.0, capstyle=ROUND,
                                        fill="#{0:02x}{1:02x}{1:02x}".format(int(x * 255), int((1 - x) * 255)),
                                        arrow=(LAST if step == num_steps-1 else None))
            # end for
        # end if

        # Draw acc trace array
        if draw_acc_trace:
            num_steps = len(self.trace_acc)
            for step in range(1, num_steps):
                x = step / float(self.trace_length_max - 1)
                self.canvas.create_line(self.trace_acc[step - 1][0],
                                        self.trace_acc[step - 1][1],
                                        self.trace_acc[step][0],
                                        self.trace_acc[step][1],
                                        width=2.0, capstyle=ROUND,
                                        fill="#{0:02x}0000".format(int(x * 255), int((1 - x) * 255)),
                                        arrow=(LAST if step == num_steps-1 else None))
            # end for
        # end if

        # Draw tangent trace array
        if draw_tangent_trace:
            num_steps = len(self.trace_tangent)
            for step in range(1, num_steps):
                x = step / float(self.trace_length_max - 1)
                self.canvas.create_line(self.trace_tangent[step - 1][0],
                                        self.trace_tangent[step - 1][1],
                                        self.trace_tangent[step][0],
                                        self.trace_tangent[step][1],
                                        width=2.0, capstyle=ROUND,
                                        fill="#{0:02x}{0:02x}{0:02x}".format(int(x * 255), int((1 - x) * 255)),
                                        arrow=(LAST if step == num_steps-1 else None))
            # end for
        # end if

        # Draw normal trace array
        if draw_normal_trace:
            num_steps = len(self.trace_normal)
            for step in range(1, num_steps):
                x = step / float(self.trace_length_max - 1)
                self.canvas.create_line(self.trace_normal[step - 1][0],
                                        self.trace_normal[step - 1][1],
                                        self.trace_normal[step][0],
                                        self.trace_normal[step][1],
                                        width=2.0, capstyle=ROUND,
                                        fill="#{1:02x}{1:02x}{1:02x}".format(int(x * 255), int((1 - x) * 255)),
                                        arrow=(LAST if step == num_steps-1 else None))
            # end for
        # end if

        # Draw acc times tangent trace array
        if draw_acc_times_tangent_trace:
            num_steps = len(self.trace_acc_times_tangent)
            for step in range(1, num_steps):
                x = step / float(self.trace_length_max - 1)
                self.canvas.create_line(self.trace_acc_times_tangent[step - 1][0],
                                        self.trace_acc_times_tangent[step - 1][1],
                                        self.trace_acc_times_tangent[step][0],
                                        self.trace_acc_times_tangent[step][1],
                                        width=2.0, capstyle=ROUND,
                                        fill="#{0:02x}{0:02x}{1:02x}".format(int(x * 255), int((1 - x) * 255)),
                                        arrow=(LAST if step == num_steps-1 else None))
            # end for
        # end if

        # Draw acc times normal trace array
        if draw_acc_times_normal_trace:
            num_steps = len(self.trace_acc_times_normal)
            for step in range(1, num_steps):
                x = step / float(self.trace_length_max - 1)
                self.canvas.create_line(self.trace_acc_times_normal[step - 1][0],
                                        self.trace_acc_times_normal[step - 1][1],
                                        self.trace_acc_times_normal[step][0],
                                        self.trace_acc_times_normal[step][1],
                                        width=2.0, capstyle=ROUND,
                                        fill="#{1:02x}{1:02x}{0:02x}".format(int(x * 255), int((1 - x) * 255)),
                                        arrow=(LAST if step == num_steps-1 else None))
            # end for
        # end if

        # Draw vectors
        # ------------
        v = self.vehicle
        r = self.scale_for_canvas(v.r)

        # Draw velocity vector
        if draw_vel_vec:
            rd = v.rd * np.asarray([1.0, -1.0]) * 0.5
            self.canvas.create_line(r[0], r[1], r[0] + rd[0], r[1] + rd[1],
                                    width=2.0, capstyle=ROUND, fill="#000000", arrow=LAST)
        # end if

        # Draw acceleration vector
        if draw_acc_vec:
            rdd = v.rdd * np.asarray([1.0, -1.0]) * 5.0
            self.canvas.create_line(r[0], r[1], r[0] + rdd[0], r[1] + rdd[1],
                                    width=2.0, capstyle=ROUND, fill="#00FF00", arrow=LAST)
        # end if

        # Draw tangent vector
        if draw_tangent:
            rdt = v.rdt * np.asarray([1.0, -1.0]) * 100.0
            self.canvas.create_line(r[0] - rdt[0] / 2.0, r[1] - rdt[1] / 2.0,
                                    r[0] + rdt[0] / 2.0, r[1] + rdt[1] / 2.0,
                                    width=2.0, capstyle=ROUND, fill="#7777FF", arrow=LAST)
        # end if

        # Draw normal vector
        if draw_normal:
            rdn = v.rdn * np.asarray([1.0, -1.0]) * 100.0
            self.canvas.create_line(r[0] - rdn[0] / 2.0, r[1] - rdn[1] / 2.0,
                                    r[0] + rdn[0] / 2.0, r[1] + rdn[1] / 2.0,
                                    width=2.0, capstyle=ROUND, fill="#000000", arrow=LAST)
        # end if
