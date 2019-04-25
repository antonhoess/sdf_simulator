import tkinter as tk


class CanvasDrawer:

    def __init__(self, vehicle, canvas, trace_length_max=10):
        self.vehicle = vehicle
        self.canvas = canvas
        self.trace_length_max = trace_length_max

        self.trace_pos = []
        self.trace_vel = []
        self.trace_acc = []
        self.trace_tangent = []
        self.trace_normal = []
        self.trace_acc_times_tangent = []
        self.trace_acc_times_normal = []

    # Upodate trace array
    def add_cur_val_to_trace(self, trace, val):
        trace.append(val)

        if len(trace) > self.trace_length_max:  # Limit trace array length
            trace.pop(0)

    # Update pos trace array
    def add_cur_pos_to_trace(self):
        self.add_cur_val_to_trace(self.trace_pos, self.vehicle.r)

    # Update vel trace array
    def add_cur_vel_to_trace(self):
        self.add_cur_val_to_trace(self.trace_vel, self.vehicle.rd * 20.0)

    # Update acc trace array
    def add_cur_acc_to_trace(self):
        self.add_cur_val_to_trace(self.trace_acc, self.vehicle.rdd * 1000.0)

    # Update tangent trace array
    def add_cur_tangent_to_trace(self):
        self.add_cur_val_to_trace(self.trace_tangent, self.vehicle.rdt * 10000.0)

    # Update normal trace array
    def add_cur_normal_to_trace(self):
        self.add_cur_val_to_trace(self.trace_normal, self.vehicle.rdn * 10000.0)

    # Update acc times tangent trace array
    def add_cur_acc_times_tangent_to_trace(self):
        self.add_cur_val_to_trace(self.trace_acc_times_tangent, self.vehicle.rddxrdt * 1000.0)

    # Update acc times normal trace array
    def add_cur_acc_times_normal_to_trace(self):
        self.add_cur_val_to_trace(self.trace_acc_times_normal, self.vehicle.rddxrdn * 1000.0)

    def reset_traces(self):
        self.trace_pos.clear()
        self.trace_vel.clear()
        self.trace_acc.clear()
        self.trace_tangent.clear()
        self.trace_normal.clear()
        self.trace_acc_times_tangent.clear()
        self.trace_acc_times_normal.clear()

    def clear(self):
        self.canvas.delete(tk.ALL)

    # Draw pos trace array
    def draw_trace(self, trace, draw_arrow=True, fill_format="#000000", **kwargs):
        num_steps = len(trace)
        for step in range(1, num_steps):
            x = step / float(self.trace_length_max - 1)
            self.canvas.create_line(trace[step - 1][0],
                                    trace[step - 1][1],
                                    trace[step][0],
                                    trace[step][1],
                                    fill=fill_format.format(int(x * 255), int((1 - x) * 255)), capstyle=tk.ROUND,
                                    arrow=(tk.LAST if draw_arrow and step == num_steps-1 else None), **kwargs)
        # end for

    def draw(self, draw_pos_trace=True, draw_vel_trace=True, draw_acc_trace=True, draw_tangent_trace=True,
             draw_normal_trace=True, draw_acc_times_tangent_trace=True, draw_acc_times_normal_trace=True,
             draw_vel_vec=True, draw_acc_vec=True, draw_tangent=True, draw_normal=True):

        # Clear canvas
        self.clear()

        # Draw trace arrays
        # -----------------
        if draw_pos_trace:
            self.draw_trace(self.trace_pos, draw_arrow=True, fill_format="#{0:02x}00{1:02x}", width=5.0, arrowshape=(16, 20, 6))

        if draw_vel_trace:
            self.draw_trace(self.trace_vel, draw_arrow=True, fill_format="#{0:02x}{1:02x}{1:02x}", width=2.0)

        if draw_acc_trace:
            self.draw_trace(self.trace_acc, draw_arrow=True, fill_format="#{0:02x}0000", width=2.0)

        if draw_tangent_trace:
            self.draw_trace(self.trace_tangent, draw_arrow=True, fill_format="#{0:02x}{0:02x}{0:02x}", width=2.0)

        if draw_normal_trace:
            self.draw_trace(self.trace_normal, draw_arrow=True, fill_format="#{1:02x}{1:02x}{1:02x}", width=2.0)

        if draw_acc_times_tangent_trace:
            self.draw_trace(self.trace_acc_times_tangent, draw_arrow=True, fill_format="#{0:02x}{0:02x}{1:02x}", width=2.0)

        if draw_acc_times_normal_trace:
            self.draw_trace(self.trace_acc_times_normal, draw_arrow=True, fill_format="#{1:02x}{1:02x}{0:02x}", width=2.0)

        # Draw vectors
        # ------------
        v = self.vehicle
        r = self.trace_pos[-1]
        rd = self.trace_vel[-1]
        rdd = self.trace_acc[-1]
        rdt = self.trace_tangent[-1]
        rdn = self.trace_normal[-1]

        # Draw velocity vector
        if draw_vel_vec:
            self.canvas.create_line(r[0], r[1], r[0] + rd[0], r[1] + rd[1],
                                    width=2.0, capstyle=tk.ROUND, fill="#000000", arrow=tk.LAST)
        # end if

        # Draw acceleration vector
        if draw_acc_vec:
            self.canvas.create_line(r[0], r[1], r[0] + rdd[0], r[1] + rdd[1],
                                    width=2.0, capstyle=tk.ROUND, fill="#00FF00", arrow=tk.LAST)
        # end if

        # Draw tangent vector
        if draw_tangent:
            self.canvas.create_line(r[0] - rdt[0] / 2.0, r[1] - rdt[1] / 2.0,
                                    r[0] + rdt[0] / 2.0, r[1] + rdt[1] / 2.0,
                                    width=2.0, capstyle=tk.ROUND, fill="#7777FF", arrow=tk.LAST)
        # end if

        # Draw normal vector
        if draw_normal:
            self.canvas.create_line(r[0] - rdn[0] / 2.0, r[1] - rdn[1] / 2.0,
                                    r[0] + rdn[0] / 2.0, r[1] + rdn[1] / 2.0,
                                    width=2.0, capstyle=tk.ROUND, fill="#000000", arrow=tk.LAST)
        # end if
