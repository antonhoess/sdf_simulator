from base_visu import *


__author__ = "Anton Höß"
__copyright__ = "Copyright 2020"


class SensorGroupVisu(BaseVisu, TraceVisu):
    """A sensor-group's visualization.

    Parameters
    ----------
    sensor_group
        The sensor group to draw.
    canvas
        The canvas to draw the sensors of the sensor group on.
    fill : str, optional
        The polygon's fill color.
    trace_length_max : int, optional
        The max. trace length for drawing the trace.
    """

    def __init__(self, sensor_group, canvas, fill=None, trace_length_max=10):
        BaseVisu.__init__(self, canvas)
        TraceVisu.__init__(self, trace_length_max)

        self.sensor_group = sensor_group
        self.canvas = canvas
        self.fill = fill
        self.cov_ell_cnt = 0

        self._trace_pos_filtered = dict()
    # end def

    def add_cur_vals_to_traces(self, vehicle):
        """Adds the current measurement of the vehicle to its corresponding trace.

        Parameters
        ----------
        vehicle
            The vehicle who's trace to add the position to.
        """

        self.add_cur_pos_filtered_to_trace(vehicle)
    # end def

    # Update filtered pos trace array
    def add_cur_pos_filtered_to_trace(self, vehicle):
        """Adds the current measurement of the vehicle to its corresponding trace.

        Parameters
        ----------
        vehicle
            The vehicle who's trace to add the position to.
        """
        if vehicle not in self._trace_pos_filtered:
            self._trace_pos_filtered[vehicle] = list()

        self.add_cur_val_to_trace(self._trace_pos_filtered[vehicle], self.sensor_group.measurements[vehicle][-1].get_abs_cartesian())
    # end def

    def _draw_trace(self, trace, draw_arrow=True, fill_format="#000000", **kwargs):
        """Draws a trace onto the SensorVisu's canvas.

        Parameters
        ----------
        trace
            The trace to be drawn.
        draw_arrow : bool, optional
            Indicates if the trace's arrow shall be drawn.
        fill_format : str, optional
            Defines the format string for creating the color gradient depending on the relative trace position.
        **kwargs : dict, optional
            Keyword arguments passed to tkinter.Canvas.create_line().
        """

        BaseVisu.draw_trace(self.canvas, trace=trace, draw_arrow=draw_arrow, fill_format=fill_format, color=self.fill, trace_length_max=self.trace_length_max, **kwargs)
    # end def

    def draw(self, draw_meas_filtered=True, vehicles=None):
        """
        Draws the sensor group, the measurement lines to each vehicle, and the measurements (confidence ellipses) the SensorVisu's canvas.
        When hovering the sensor with the mouse cursor, it's color changes to red.

        Parameters
        ----------
        draw_meas_filtered : bool, optional
            Indicates if the Kalman-filtered measurements shall be drawn.
        vehicles, optional
            List of vehicles to draw the measurement information for.
        """

        if not isinstance(vehicles, list):
            vehicles = [vehicles]

        # For each vehicle draw the measurement information
        for vehicle in vehicles:
            # The covariance ellipses
            if self.sensor_group.cov_mat_draw:
                self.draw_cov_mat_ell(None, vehicle, self.sensor_group.cov_mat, self.cov_ell_cnt, self.fill, orient=False)
        # end for

        # For each vehicle draw the Kalman filtered measurement information
        if draw_meas_filtered:
            for vehicle in self._trace_pos_filtered:
                if vehicle in vehicles and vehicle.active:
                    self._draw_trace(self._trace_pos_filtered[vehicle], draw_arrow=True, fill_format="#000000",
                                     width=1.0)
                # end if
            # end for
        # end if
    # end def
# end class
