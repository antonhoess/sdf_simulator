import tkinter as tk
from base_visu import BaseVisu, TraceVisu


__author__ = "Anton Höß"
__copyright__ = "Copyright 2020"


class VehicleVisu(BaseVisu, TraceVisu):
    """Visualizes a Vehicle.

    Parameters
    ----------
    vehicle : Vehicle
        The vehicle to visualize.
    canvas : tkinter.Canvas
        The canvas to draw the Vehicle's visualization on.
    color : float
        The trace color.
    trace_length_max : int
        The max. trace length.
    """

    def __init__(self, vehicle, canvas, color=None, trace_length_max=10):
        BaseVisu.__init__(self, canvas)
        TraceVisu.__init__(self, trace_length_max)

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
    # end def

    def add_cur_vals_to_traces(self):
        """Appends the current Vehicle's state values to all trace arrays."""

        self.add_cur_pos_to_trace()
        self.add_cur_vel_to_trace()
        self.add_cur_acc_to_trace()
        self.add_cur_tangent_to_trace()
        self.add_cur_normal_to_trace()
        self.add_cur_acc_times_tangent_to_trace()
        self.add_cur_acc_times_normal_to_trace()
    # end def

    def add_cur_pos_to_trace(self):
        """Updates the pos trace array."""

        self.add_cur_val_to_trace(self._trace_pos, self.vehicle.r)
    # end def

    def add_cur_vel_to_trace(self):
        """Updates the vel trace array."""

        self.add_cur_val_to_trace(self._trace_vel, self.vehicle.rd * 20.0)  # XXX Make these scale factors parameters
    # end def

    def add_cur_acc_to_trace(self):
        """Updates the acc trace array."""

        self.add_cur_val_to_trace(self._trace_acc, self.vehicle.rdd * 1000.0)
    # end def

    def add_cur_tangent_to_trace(self):
        """Updates the tangent trace array."""

        self.add_cur_val_to_trace(self._trace_tangent, self.vehicle.rdt * 10000.0)
    # end def

    def add_cur_normal_to_trace(self):
        """Updates the normal trace array."""

        self.add_cur_val_to_trace(self._trace_normal, self.vehicle.rdn * 10000.0)
    # end def

    def add_cur_acc_times_tangent_to_trace(self):
        """Updates the acc times tangent trace array."""

        self.add_cur_val_to_trace(self._trace_acc_times_tangent, self.vehicle.rddxrdt * 1000.0)
    # end def

    def add_cur_acc_times_normal_to_trace(self):
        """Updates the acc times normal trace array."""

        self.add_cur_val_to_trace(self._trace_acc_times_normal, self.vehicle.rddxrdn * 1000.0)
    # end def

    def draw(self, draw_pos_trace=True, draw_vel_trace=True,
             draw_acc_trace=True, draw_tangent_trace=True,
             draw_normal_trace=True, draw_acc_times_tangent_trace=True, draw_acc_times_normal_trace=True,
             draw_vel_vec=True, draw_acc_vec=True, draw_tangent=True, draw_normal=True, proj_dim=None, proj_scale=1.):
        """Draws the Vehicle's traces and vectors.

        Parameters
        ----------
        draw_pos_trace : bool, optional
            Indicates if the pos trace shall be drawn.
        draw_vel_trace : bool, optional
            Indicates if the pos trace shall be drawn.
        draw_acc_trace : bool, optional
            Indicates if the acc trace shall be drawn.
        draw_tangent_trace : bool, optional
            Indicates if the tangent trace shall be drawn.
        draw_normal_trace : bool, optional
            Indicates if the normal shall be drawn.
        draw_acc_times_tangent_trace : bool, optional
            Indicates if the acc times tangent trace shall be drawn.
        draw_acc_times_normal_trace : bool, optional
            Indicates if the acc times normal trace shall be drawn.
        draw_vel_vec : bool, optional
            Indicates if the vel vector shall be drawn.
        draw_acc_vec : bool, optional
            Indicates if the acc vector shall be drawn.
        draw_tangent : bool, optional
            Indicates if the tangent vector shall be drawn.
        draw_normal : bool, optional
            Indicates if the normal vector shall be drawn.
        proj_dim : int, optional
            Indicates where the traces shall be projected.
            0 / None = No projection.
            1 = Project onto X-axis.
            2 = Project onto Y-axis.
        proj_scale : float, optional
            Defines the scaling of the traces.
        """

        # Draw trace arrays
        # -----------------
        if draw_pos_trace:
            self._draw_trace(self._trace_pos, draw_arrow=True, fill_format="#{0:02x}00{1:02x}", width=5.0,
                             arrowshape=(16, 20, 6))

        if draw_vel_trace:
            self._draw_trace(self._trace_vel, proj_dim=proj_dim, proj_scale=proj_scale, draw_arrow=True,
                             fill_format="#{0:02x}{1:02x}{1:02x}", width=2.0)

        if draw_acc_trace:
            self._draw_trace(self._trace_acc, proj_dim=proj_dim, proj_scale=proj_scale, draw_arrow=True,
                             fill_format="#{0:02x}0000", width=2.0)

        if draw_tangent_trace:
            self._draw_trace(self._trace_tangent, proj_dim=proj_dim, proj_scale=proj_scale, draw_arrow=True,
                             fill_format="#{0:02x}{0:02x}{0:02x}", width=2.0)

        if draw_normal_trace:
            self._draw_trace(self._trace_normal, proj_dim=proj_dim, proj_scale=proj_scale, draw_arrow=True,
                             fill_format="#{1:02x}{1:02x}{1:02x}", width=2.0)

        if draw_acc_times_tangent_trace:
            self._draw_trace(self._trace_acc_times_tangent, proj_dim=proj_dim, proj_scale=proj_scale, draw_arrow=True,
                             fill_format="#{0:02x}{0:02x}{1:02x}", width=2.0)

        if draw_acc_times_normal_trace:
            self._draw_trace(self._trace_acc_times_normal, proj_dim=proj_dim, proj_scale=proj_scale, draw_arrow=True,
                             fill_format="#{1:02x}{1:02x}{0:02x}", width=2.0)

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
    # end def

    def _reset_traces(self):
        """Clears the Vehicle's values of all trace arrays."""

        self._trace_pos.clear()
        self._trace_vel.clear()
        self._trace_acc.clear()
        self._trace_tangent.clear()
        self._trace_normal.clear()
        self._trace_acc_times_tangent.clear()
        self._trace_acc_times_normal.clear()
    # end def

    # Draw pos trace array
    # proj_dim = projection dimension: 0 = No projection, 1 = X-axis, 2 = Y-axis
    def _draw_trace(self, trace, draw_arrow=True, proj_dim=0, proj_scale=1., fill_format="#000000", **kwargs):
        """Draws a trace onto the VehicleVisu's canvas.

        Parameters
        ----------
        trace :
            The trace to be drawn.
        draw_arrow : bool, optional
            Indicates if the trace's arrow shall be drawn.
        proj_dim : int, optional
            Indicates where the traces shall be projected.
            0 / None = No projection.
            1 = Project onto X-axis.
            2 = Project onto Y-axis.
        proj_scale : float, optional
            Defines the scaling of the traces.
        fill_format : str, optional
            Defines the format string for creating the color gradient depending on the relative trace position.
        **kwargs : dict, optional
            Keyword arguments passed to tkinter.Canvas.create_line().
        """

        BaseVisu.draw_trace(self.canvas, trace=trace, draw_arrow=draw_arrow, proj_dim=proj_dim, proj_scale=proj_scale, fill_format=fill_format, color=self.color, trace_length_max=self.trace_length_max, **kwargs)
    # end def
