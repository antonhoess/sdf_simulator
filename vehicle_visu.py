import tkinter as tk


class VehicleVisu:
    def __init__(self, vehicle, canvas, color=None, trace_length_max=10):
        self.vehicle = vehicle
        self.canvas = canvas
        self.color = color
        self.trace_length_max = trace_length_max

        self._trace_pos = []
        self._trace_vel = []
        self._trace_acc = []
        self._trace_tangent = []
        self._trace_normal = []
        self._trace_acc_times_tangent = []
        self._trace_acc_times_normal = []

    # Upodate trace array
    def add_cur_val_to_trace(self, trace, val):
        trace.append(val)

        if len(trace) > self.trace_length_max:  # Limit trace array length
            trace.pop(0)

    # Update pos trace array
    def add_cur_pos_to_trace(self):
        self.add_cur_val_to_trace(self._trace_pos, self.vehicle.r)

    # Update vel trace array
    def add_cur_vel_to_trace(self):
        self.add_cur_val_to_trace(self._trace_vel, self.vehicle.rd * 20.0)

    # Update acc trace array
    def add_cur_acc_to_trace(self):
        self.add_cur_val_to_trace(self._trace_acc, self.vehicle.rdd * 1000.0)

    # Update tangent trace array
    def add_cur_tangent_to_trace(self):
        self.add_cur_val_to_trace(self._trace_tangent, self.vehicle.rdt * 10000.0)

    # Update normal trace array
    def add_cur_normal_to_trace(self):
        self.add_cur_val_to_trace(self._trace_normal, self.vehicle.rdn * 10000.0)

    # Update acc times tangent trace array
    def add_cur_acc_times_tangent_to_trace(self):
        self.add_cur_val_to_trace(self._trace_acc_times_tangent, self.vehicle.rddxrdt * 1000.0)

    # Update acc times normal trace array
    def add_cur_acc_times_normal_to_trace(self):
        self.add_cur_val_to_trace(self._trace_acc_times_normal, self.vehicle.rddxrdn * 1000.0)

    def draw(self, omit_clear=False, draw_pos_trace=True, draw_vel_trace=True, draw_acc_trace=True,
             draw_tangent_trace=True,
             draw_normal_trace=True, draw_acc_times_tangent_trace=True, draw_acc_times_normal_trace=True,
             draw_vel_vec=True, draw_acc_vec=True, draw_tangent=True, draw_normal=True):

        # Clear canvas
        if not omit_clear:
            self.clear()

        # Draw trace arrays
        # -----------------
        if draw_pos_trace:
            self._draw_trace(self._trace_pos, draw_arrow=True, fill_format="#{0:02x}00{1:02x}", width=5.0,
                             arrowshape=(16, 20, 6))

        if draw_vel_trace:
            self._draw_trace(self._trace_vel, draw_arrow=True, fill_format="#{0:02x}{1:02x}{1:02x}", width=2.0)

        if draw_acc_trace:
            self._draw_trace(self._trace_acc, draw_arrow=True, fill_format="#{0:02x}0000", width=2.0)

        if draw_tangent_trace:
            self._draw_trace(self._trace_tangent, draw_arrow=True, fill_format="#{0:02x}{0:02x}{0:02x}", width=2.0)

        if draw_normal_trace:
            self._draw_trace(self._trace_normal, draw_arrow=True, fill_format="#{1:02x}{1:02x}{1:02x}", width=2.0)

        if draw_acc_times_tangent_trace:
            self._draw_trace(self._trace_acc_times_tangent, draw_arrow=True, fill_format="#{0:02x}{0:02x}{1:02x}",
                             width=2.0)

        if draw_acc_times_normal_trace:
            self._draw_trace(self._trace_acc_times_normal, draw_arrow=True, fill_format="#{1:02x}{1:02x}{0:02x}",
                             width=2.0)

        # Draw vectors
        # ------------
        if len(self._trace_pos) > 0:
            r = self._trace_pos[-1]
            rd = self._trace_vel[-1]
            rdd = self._trace_acc[-1]
            rdt = self._trace_tangent[-1]
            rdn = self._trace_normal[-1]

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
        # end if

    def clear(self):
        self.canvas.delete(tk.ALL)

    def _reset_traces(self):
        self._trace_pos.clear()
        self._trace_vel.clear()
        self._trace_acc.clear()
        self._trace_tangent.clear()
        self._trace_normal.clear()
        self._trace_acc_times_tangent.clear()
        self._trace_acc_times_normal.clear()

    # Draw pos trace array
    def _draw_trace(self, trace, draw_arrow=True, fill_format="#000000", **kwargs):
        num_steps = len(trace)
        for step in range(1, num_steps):
            x = step / float(self.trace_length_max - 1)

            fill = fill_format.format(int(x * 255), int((1 - x) * 255))

            if draw_arrow and step == num_steps - 1:
                arrow = tk.LAST

                if self.color is not None:
                    fill = self.color
            else:
                arrow = None

            self.canvas.create_line(trace[step - 1][0],
                                    trace[step - 1][1],
                                    trace[step][0],
                                    trace[step][1],
                                    fill=fill, capstyle=tk.ROUND, arrow=arrow, **kwargs)
        # end for
