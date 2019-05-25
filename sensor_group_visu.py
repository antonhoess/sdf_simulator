from base_visu import BaseVisu, TraceVisu


class SensorGroupVisu(BaseVisu, TraceVisu):
    def __init__(self, sensor_group, canvas, fill=None, trace_length_max=10):
        BaseVisu.__init__(self, canvas)
        TraceVisu.__init__(self, trace_length_max)

        self.sensor_group = sensor_group
        self.canvas = canvas
        self.fill = fill

        self.trace_length_max = trace_length_max

        self._trace_pos_filtered = {}

    def add_cur_vals_to_traces(self):
        self.add_cur_pos_filtered_to_trace()

    # Update filtered pos trace array
    def add_cur_pos_filtered_to_trace(self):
        for vehicle in self.sensor_group.kalman_filter:
            if vehicle not in self._trace_pos_filtered:
                self._trace_pos_filtered[vehicle] = []

            self.add_cur_val_to_trace(self._trace_pos_filtered[vehicle], self.sensor_group.kalman_filter[vehicle].get_current_state_estimate())
        # end for

    def _draw_trace(self, trace, draw_arrow=True, fill_format="#000000", **kwargs):
        BaseVisu.draw_trace(self.canvas, trace=trace, draw_arrow=draw_arrow, fill_format=fill_format, color=self.fill, trace_length_max=self.trace_length_max, **kwargs)

    def draw(self, draw_meas_filtered=True, vehicles=None):
        if not isinstance(vehicles, list):
            vehicles = [vehicles]

        # For each vehicle draw the Kalman filtered measurement information
        if draw_meas_filtered:
            for vehicle in self._trace_pos_filtered:
                if vehicle in vehicles and vehicle.active:
                    self._draw_trace(self._trace_pos_filtered[vehicle], draw_arrow=True, fill_format="#000000",
                                     width=1.0)
                # end if
            # end for
        # end if
