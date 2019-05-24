import tkinter as tk
from base_visu import BaseVisu
from vehicle_visu import VehicleVisu
from sensor_visu import SensorVisu
from sensor_group_visu import SensorGroupVisu
from scale_trans_canvas import ScaleTransCanvas
from scroll_frame import ScrollFrame
from popup_menu import PopupMenu
import time
from enum import Enum


class Gui:
    class Frame(tk.Frame):
        def __init__(self, parent_frame, **kwargs):
            super().__init__(parent_frame, **kwargs)
            self._parent_frame = parent_frame

        def __enter__(self):
            return self

        def __exit__(self, type, value, traceback):
            return True

        @property
        def parent(self):
            return self._parent_frame
    # end class

    class ZoomDir(Enum):
        IN = 1
        OUT = 2
    # end class

    class MoveDir(Enum):
        LEFT = 1
        RIGHT = 2
        UP = 3
        DOWN = 4
    # end class

    def __init__(self, canvas_width=500, canvas_height=500, base_scale_factor=1.e-2, zoom_factor=1.1,
                 trace_length_max=100, meas_buf_max=100):
        self._BASE_SCALE_FACTOR = base_scale_factor  # Set to a fixed value that is good for zoom == 1.0
        self._ZOOM_FACTOR = zoom_factor

        self._bv = None  # Base visualizations
        self._vv = []  # Vehicle visualizations
        self._sv = []  # Sensor visualizations
        self._sgv = []  # Sensor group visualizations

        self._sg = []  # Sensor groups

        self._t = 0.0       # Absolute time
        self._t_incr = 1.   # Time increase per tick
        self._t_tick = .01  # Sleep [s] per tick

        self._trace_length_max = int(trace_length_max / self._t_incr)  # Max. length of the trace
        self._meas_buf_max = meas_buf_max  # Max. size of measurements

        self._gui_inited = False
        self._is_running = False

        self._play = False
        self._enter_command = False

        self._show_trace_settings = True
        self._show_vector_settings = True
        self._show_projection_settings = True
        self._show_vehicle_settings = True
        self._show_sensor_settings = True

        # For shift the objects on the canvas
        self._move_mode = False
        self._move_origin = [-1, -1]
        self._move_origin_canvas = [-1, -1]

        # Place GUI elements
        self.master = tk.Tk()
        self.master.title("SDF Simulator")

        root = tk.Frame(self.master)
        root.pack(expand=True, fill=tk.BOTH)
        frm = root

        # View panel on top
        # -----------------
        with self.Frame(frm) as frm:
            frm.pack(expand=False, fill=tk.X, side=tk.TOP, pady=5)

            # Position
            with self.Frame(frm) as frm:
                frm.pack(fill=tk.X, side=tk.LEFT, padx=5)
                with self.Frame(frm) as frm:
                    frm.pack(side=tk.TOP, padx=5)
                    lbl_pos_x = tk.Label(frm, text="pos x [m]:", width=9, anchor=tk.W)
                    lbl_pos_x.pack(side=tk.LEFT)
                    self.lbl_pos_x_val = tk.Label(frm, text="", width=10, bg="yellow", anchor=tk.E)
                    self.lbl_pos_x_val.pack(side=tk.LEFT)
                    frm = frm.parent
                with self.Frame(frm) as frm:
                    frm.pack(side=tk.TOP, padx=5)
                    lbl_pos_y = tk.Label(frm, text="pos y [m]:", width=9, anchor=tk.W)
                    lbl_pos_y.pack(side=tk.LEFT)
                    self.lbl_pos_y_val = tk.Label(frm, text="", width=10, bg="yellow", anchor=tk.E)
                    self.lbl_pos_y_val.pack(side=tk.LEFT)
                    frm = frm.parent
                frm = frm.parent
            # Velocity
            with self.Frame(frm) as frm:
                frm.pack(fill=tk.X, side=tk.LEFT, padx=5)
                with self.Frame(frm) as frm:
                    frm.pack(side=tk.TOP, padx=5)
                    lbl_pos_x = tk.Label(frm, text="vel. x [m/s]:", width=10, anchor=tk.W)
                    lbl_pos_x.pack(side=tk.LEFT)
                    self.lbl_vel_x_val = tk.Label(frm, text="", width=10, bg="orange", anchor=tk.E)
                    self.lbl_vel_x_val.pack(side=tk.LEFT)
                    frm = frm.parent
                with self.Frame(frm) as frm:
                    frm.pack(side=tk.TOP, padx=5)
                    lbl_pos_y = tk.Label(frm, text="vel. y [m/s]:", width=10, anchor=tk.W)
                    lbl_pos_y.pack(side=tk.LEFT)
                    self.lbl_vel_y_val = tk.Label(frm, text="", width=10, bg="orange", anchor=tk.E)
                    self.lbl_vel_y_val.pack(side=tk.LEFT)
                    frm = frm.parent
                frm = frm.parent
            # Acceleration
            with self.Frame(frm) as frm:
                frm.pack(fill=tk.X, side=tk.LEFT, padx=5)
                with self.Frame(frm) as frm:
                    frm.pack(side=tk.TOP, padx=5)
                    lbl_pos_x = tk.Label(frm, text="accel. x [m/s²]:", width=13, anchor=tk.W)
                    lbl_pos_x.pack(side=tk.LEFT)
                    self.lbl_acc_x_val = tk.Label(frm, text="", width=10, bg="red", anchor=tk.E)
                    self.lbl_acc_x_val.pack(side=tk.LEFT)
                    frm = frm.parent
                with self.Frame(frm) as frm:
                    frm.pack(side=tk.TOP, padx=5)
                    lbl_pos_y = tk.Label(frm, text="accel. y [m/s²]:", width=13, anchor=tk.W)
                    lbl_pos_y.pack(side=tk.LEFT)
                    self.lbl_acc_y_val = tk.Label(frm, text="", width=10, bg="red", anchor=tk.E)
                    self.lbl_acc_y_val.pack(side=tk.LEFT)
                    frm = frm.parent
                frm = frm.parent
            frm = frm.parent

        # Status bar at the bottom
        with self.Frame(frm) as frm:
            frm.pack(expand=False, fill=tk.X, side=tk.BOTTOM)
            # Cursor position (scaled)
            with self.Frame(frm) as frm:
                frm.pack(fill=tk.X, side=tk.LEFT, pady=5)
                lbl_cursor_pos = tk.Label(frm, text="cursor pos (x, y):", width=14, anchor=tk.W)
                lbl_cursor_pos.pack(fill=tk.X, side=tk.LEFT)
                self.lbl_cursor_pos_val = tk.Label(frm, text="0; 0", width=20, bg="yellow")
                self.lbl_cursor_pos_val.pack(fill=tk.X, side=tk.LEFT)
                frm = frm.parent
            # Elapsed time
            sep_ver = tk.Frame(frm, width=2, bd=1, relief=tk.SUNKEN)
            sep_ver.pack(fill=tk.Y, side=tk.LEFT, padx=5)
            with self.Frame(frm) as frm:
                frm.pack(fill=tk.X, side=tk.LEFT, pady=5)
                lbl_time = tk.Label(frm, text="t =", width=3, anchor=tk.W)
                lbl_time.pack(fill=tk.X, side=tk.LEFT)
                self.lbl_time_val = tk.Label(frm, text="0.0", width=8, bg="yellow", anchor=tk.E)
                self.lbl_time_val.pack(fill=tk.X, side=tk.LEFT)
                frm = frm.parent
            frm = frm.parent

        sep_hor = tk.Frame(frm, height=2, bd=1, relief=tk.SUNKEN)
        sep_hor.pack(fill=tk.X, padx=5, pady=5, side=tk.BOTTOM)

        # The control panel on the left
        # -----------------------------
        with self.Frame(frm) as frm:
            frm.pack(expand=False, fill=tk.BOTH, side=tk.LEFT)

            # Run controls
            self.btn_play_pause = tk.Button(frm, text="Play", width=10, bg="lightblue", command=self.cb_play_pause)
            self.btn_play_pause.pack(fill=tk.X, side=tk.TOP)
            self.btn_play_pause.bind('<Shift-Button-1>', self.cb_command_callback)

            self.btn_single_step = tk.Button(frm, text="Step", width=10, bg="lightgreen",
                                             command=self.cb_single_step)
            self.btn_single_step.pack(fill=tk.X, side=tk.TOP)

            sep_hor = tk.Frame(frm, height=2, bd=1, relief=tk.SUNKEN)
            sep_hor.pack(fill=tk.X, padx=5, pady=5)

            # Trace settings
            with self.Frame(frm) as frm:
                frm.pack(fill=tk.X)

                self.btn_toggle_trace_settings = tk.Button(frm, command=self.cb_toggle_trace_settings)
                self.btn_toggle_trace_settings.pack(fill=tk.X)

                with self.Frame(frm) as frm:
                    frm.pack(fill=tk.X)
                    self.frm_trace_settings_content = frm

                    self.draw_origin_cross = tk.IntVar()
                    self.draw_origin_cross.set(1)
                    chk_draw_origin_cross = tk.Checkbutton(frm, text="Draw Origin Cross", variable=self.draw_origin_cross,
                                                           command=self.cb_draw)
                    chk_draw_origin_cross.pack(side=tk.TOP, anchor=tk.W)

                    self.draw_pos_trace = tk.IntVar()
                    self.draw_pos_trace.set(1)
                    chk_draw_pos_trace = tk.Checkbutton(frm, text="Draw Pos. Trace", variable=self.draw_pos_trace,
                                                        command=self.cb_draw)
                    chk_draw_pos_trace.pack(side=tk.TOP, anchor=tk.W)

                    self.draw_vel_trace = tk.IntVar()
                    chk_draw_vel_trace = tk.Checkbutton(frm, text="Draw Vel. Trace", variable=self.draw_vel_trace,
                                                        command=self.cb_draw)
                    chk_draw_vel_trace.pack(side=tk.TOP, anchor=tk.W)

                    self.draw_acc_trace = tk.IntVar()
                    chk_draw_acc_trace = tk.Checkbutton(frm, text="Draw Accel. Trace", variable=self.draw_acc_trace,
                                                        command=self.cb_draw)
                    chk_draw_acc_trace.pack(side=tk.TOP, anchor=tk.W)

                    self.draw_tangent_trace = tk.IntVar()
                    chk_draw_tangent_trace = tk.Checkbutton(frm, text="Draw Tangent Trace",
                                                            variable=self.draw_tangent_trace,
                                                            command=self.cb_draw)
                    chk_draw_tangent_trace.pack(side=tk.TOP, anchor=tk.W)

                    self.draw_normal_trace = tk.IntVar()
                    chk_draw_normal_trace = tk.Checkbutton(frm, text="Draw Normal Trace", variable=self.draw_normal_trace,
                                                           command=self.cb_draw)
                    chk_draw_normal_trace.pack(side=tk.TOP, anchor=tk.W)

                    self.draw_acc_times_tangent_trace = tk.IntVar()
                    chk_draw_acc_times_tangent_trace = tk.Checkbutton(frm, text="Draw Acc. x Tangent Trace",
                                                                      variable=self.draw_acc_times_tangent_trace,
                                                                      command=self.cb_draw)
                    chk_draw_acc_times_tangent_trace.pack(side=tk.TOP, anchor=tk.W)

                    self.draw_acc_times_normal_trace = tk.IntVar()
                    chk_draw_acc_times_normal_trace = tk.Checkbutton(frm, text="Draw Acc. x Normal Trace",
                                                                     variable=self.draw_acc_times_normal_trace,
                                                                     command=self.cb_draw)
                    chk_draw_acc_times_normal_trace.pack(side=tk.TOP, anchor=tk.W)

                    self.draw_meas_filtered = tk.IntVar()
                    self.draw_meas_filtered.set(1)
                    chk_draw_meas_filtered = tk.Checkbutton(frm, text="Draw Kalman filtered Trace", variable=self.draw_meas_filtered,
                                                     command=self.cb_draw)
                    chk_draw_meas_filtered.pack(side=tk.TOP, anchor=tk.W)

                    frm = frm.parent

                self.btn_toggle_trace_settings.invoke()
                frm = frm.parent

            # Vectors
            sep_hor = tk.Frame(frm, height=2, bd=1, relief=tk.SUNKEN)
            sep_hor.pack(fill=tk.X, padx=5, pady=5)

            # Vectors
            with self.Frame(frm) as frm:
                frm.pack(fill=tk.X)

                self.btn_toggle_vector_settings = tk.Button(frm, command=self.cb_toggle_vector_settings)
                self.btn_toggle_vector_settings.pack(fill=tk.X)

                with self.Frame(frm) as frm:
                    frm.pack(fill=tk.X)
                    self.frm_vector_settings_content = frm

                    self.draw_vel_vec = tk.IntVar()
                    chk_draw_vel_vec = tk.Checkbutton(frm, text="Draw Vel. Vec.", variable=self.draw_vel_vec,
                                                      command=self.cb_draw)
                    chk_draw_vel_vec.pack(side=tk.TOP, anchor=tk.W)

                    self.draw_acc_vec = tk.IntVar()
                    chk_draw_acc_vec = tk.Checkbutton(frm, text="Draw Accel. Vec.", variable=self.draw_acc_vec,
                                                      command=self.cb_draw)
                    chk_draw_acc_vec.pack(side=tk.TOP, anchor=tk.W)

                    # Tangent and normal
                    sep_hor = tk.Frame(frm, height=2, bd=1, relief=tk.SUNKEN)
                    sep_hor.pack(fill=tk.X, padx=5, pady=5)

                    self.draw_tangent = tk.IntVar()
                    chk_draw_tangent = tk.Checkbutton(frm, text="Draw Tangent Vec.", variable=self.draw_tangent,
                                                      command=self.cb_draw)
                    chk_draw_tangent.pack(side=tk.TOP, anchor=tk.W)

                    self.draw_normal = tk.IntVar()
                    chk_draw_normal = tk.Checkbutton(frm, text="Draw Normal Vec.", variable=self.draw_normal,
                                                     command=self.cb_draw)
                    chk_draw_normal.pack(side=tk.TOP, anchor=tk.W)
                    frm = frm.parent
                self.btn_toggle_vector_settings.invoke()
                frm = frm.parent

            # Projection
            sep_hor = tk.Frame(frm, height=2, bd=1, relief=tk.SUNKEN)
            sep_hor.pack(fill=tk.X, padx=5, pady=5)

            with self.Frame(frm) as frm:
                frm.pack(fill=tk.X)

                self.btn_toggle_projection_settings = tk.Button(frm, command=self.cb_toggle_projection_settings)
                self.btn_toggle_projection_settings.pack(fill=tk.X)

                with self.Frame(frm) as frm:
                    frm.pack(fill=tk.X)
                    self.frm_projection_settings_content = frm

                    self.proj_dim = tk.IntVar()
                    self.proj_dim.set(0)
                    rad_proj_dim_none = tk.Radiobutton(frm, text="No projection", variable=self.proj_dim, value=0,
                                                       command=self.cb_draw)
                    rad_proj_dim_none.pack(side=tk.TOP, anchor=tk.W)
                    rad_proj_dim_x_axis = tk.Radiobutton(frm, text="Proj. X-axis", variable=self.proj_dim, value=1,
                                                         command=self.cb_draw)
                    rad_proj_dim_x_axis.pack(side=tk.TOP, anchor=tk.W)
                    rad_proj_dim_y_axis = tk.Radiobutton(frm, text="Proj. Y-axis", variable=self.proj_dim, value=2,
                                                         command=self.cb_draw)
                    rad_proj_dim_y_axis.pack(side=tk.TOP, anchor=tk.W)

                    frm_proj_scale = tk.Frame(frm)
                    frm_proj_scale.pack(fill=tk.X, side=tk.TOP, padx=5)
                    lbl_proj_scale = tk.Label(frm_proj_scale, text="Proj. Scale", width=9, anchor=tk.W)
                    lbl_proj_scale.pack(fill=tk.X, side=tk.LEFT)
                    self.lbl_proj_scale_val = tk.Label(frm_proj_scale, text="", bg="white", anchor=tk.E)
                    self.lbl_proj_scale_val.pack(expand=True, fill=tk.X, side=tk.LEFT)

                    self.proj_scale = tk.IntVar()
                    self.proj_scale.set(100)
                    scl_proj_scale = tk.Scale(frm_proj_scale, orient=tk.HORIZONTAL, showvalue=False, from_=1, to=1000,
                                              resolution=1, variable=self.proj_scale, command=self.cb_proj_scale)
                    scl_proj_scale.pack(expand=True, fill=tk.X, side=tk.LEFT)
                    frm = frm.parent
                self.btn_toggle_projection_settings.invoke()
                frm = frm.parent

            # Measurements and covariance ellipses
            sep_hor = tk.Frame(frm, height=2, bd=1, relief=tk.SUNKEN)
            sep_hor.pack(fill=tk.X, padx=5, pady=5)

            self.draw_meas = tk.IntVar()
            chk_draw_meas = tk.Checkbutton(frm, text="Draw Measurements", variable=self.draw_meas,
                                           command=self.cb_draw)
            chk_draw_meas.pack(side=tk.TOP, anchor=tk.W)

            with self.Frame(frm) as frm:
                frm.pack(fill=tk.X, side=tk.TOP)
                lbl_cov_ell_cnt = tk.Label(frm, text="# Cov. Ell.:", width=9, anchor=tk.W)
                lbl_cov_ell_cnt.pack(fill=tk.X, side=tk.LEFT)
                self.lbl_cov_ell_cnt_val = tk.Label(frm, text="", bg="white", anchor=tk.E)
                self.lbl_cov_ell_cnt_val.pack(expand=True, fill=tk.X, side=tk.LEFT)

                self.cov_ell_cnt = tk.IntVar()
                self.cov_ell_cnt.set(0)
                scl_cov_ell_cnt = tk.Scale(frm, orient=tk.HORIZONTAL, showvalue=False, from_=0, to=5, resolution=1,
                                           length=70, variable=self.cov_ell_cnt, command=self.cb_cov_ell_cnt)
                scl_cov_ell_cnt.pack(expand=True, fill=tk.X, side=tk.LEFT)
                frm = frm.parent

            # Zoom
            sep_hor = tk.Frame(frm, height=2, bd=1, relief=tk.SUNKEN)
            sep_hor.pack(fill=tk.X, padx=5, pady=5)

            with self.Frame(frm) as frm:
                frm.pack(fill=tk.X, side=tk.TOP)

                lbl_zoom = tk.Label(frm, text="Zoom [%]:", width=9, anchor=tk.W)
                lbl_zoom.pack(fill=tk.X, side=tk.LEFT)
                self.lbl_zoom_val = tk.Label(frm, text="{:.2f}".format(1. * 100.), bg="white", anchor=tk.E)
                self.lbl_zoom_val.pack(expand=True, fill=tk.X, side=tk.LEFT)

                btn_zoom_out = tk.Button(frm, text="-", bg="lightblue", width=2)
                btn_zoom_out.pack(fill=None, side=tk.LEFT)
                btn_zoom_out.bind('<Button-1>', lambda event, direction=self.ZoomDir.OUT: self.cb_zoom(event, direction))

                btn_zoom_in = tk.Button(frm, text="+", bg="dodgerblue", width=2)
                btn_zoom_in.pack(fill=None, side=tk.LEFT)
                btn_zoom_in.bind('<Button-1>', lambda event, direction=self.ZoomDir.IN: self.cb_zoom(event, direction))
                frm = frm.parent

            # Time increment (per step)
            sep_hor = tk.Frame(frm, height=2, bd=1, relief=tk.SUNKEN)
            sep_hor.pack(fill=tk.X, padx=5, pady=5)

            with self.Frame(frm) as frm:
                frm.pack(fill=tk.X, side=tk.TOP)
                lbl_time_incr = tk.Label(frm, text="Time incr.:", width=9, anchor=tk.W)
                lbl_time_incr.pack(fill=tk.X, side=tk.LEFT)
                self.lbl_time_incr_val = tk.Label(frm, text="1.0", bg="white", anchor=tk.E)
                self.lbl_time_incr_val.pack(expand=True, fill=tk.X, side=tk.LEFT)

                self.time_incr = tk.DoubleVar()
                scl_time_incr = tk.Scale(frm, orient=tk.HORIZONTAL, showvalue=False, from_=0.1, to=10.0,
                                         resolution=0.1, length=70, variable=self.time_incr, command=self.cb_time_incr)
                scl_time_incr.set(1.0)
                scl_time_incr.pack(expand=True, fill=tk.X, side=tk.LEFT)
                frm = frm.parent

            # Time tick (sleep duration)
            with self.Frame(frm) as frm:
                frm.pack(fill=tk.X, side=tk.TOP)
                lbl_time_tick = tk.Label(frm, text="Time tick. [s]:", width=11, anchor=tk.W)
                lbl_time_tick.pack(fill=tk.X, side=tk.LEFT)
                self.lbl_time_tick_val = tk.Label(frm, text="0.00", bg="white", anchor=tk.E)
                self.lbl_time_tick_val.pack(expand=True, fill=tk.X, side=tk.LEFT)

                self.time_tick = tk.DoubleVar()
                scl_time_tick = tk.Scale(frm, orient=tk.HORIZONTAL, showvalue=False, from_=0.01, to=1.00,
                                         resolution=0.01, length=70, variable=self.time_tick, command=self.cb_time_tick)
                scl_time_tick.pack(expand=True, fill=tk.X, side=tk.LEFT)
                frm = frm.parent

            # Trace length max.
            sep_hor = tk.Frame(frm, height=2, bd=1, relief=tk.SUNKEN)
            sep_hor.pack(fill=tk.X, padx=5, pady=5)

            with self.Frame(frm) as frm:
                frm.pack(fill=tk.X, side=tk.TOP)
                lbl_trace_length_max = tk.Label(frm, text="Trace len. max.:", anchor=tk.W)
                lbl_trace_length_max.pack(fill=tk.X, side=tk.LEFT)
                self.lbl_trace_length_max_val = tk.Label(frm, text="100", bg="white", width=4, anchor=tk.E)
                self.lbl_trace_length_max_val.pack(expand=True, fill=tk.X, side=tk.LEFT)

                self.trace_length_max = tk.IntVar()
                scl_trace_length_max = tk.Scale(frm, orient=tk.HORIZONTAL, showvalue=False, from_=2, to=1000,
                                                resolution=1, length=70, variable=self.trace_length_max, command=self.cb_trace_length_max)
                scl_trace_length_max.set(self._trace_length_max)
                scl_trace_length_max.pack(expand=True, fill=tk.X, side=tk.LEFT)
                frm = frm.parent

            # Measurement count
            with self.Frame(frm) as frm:
                frm.pack(fill=tk.X, side=tk.TOP)
                lbl_meas_buf_max = tk.Label(frm, text="Meas. cnt.:", anchor=tk.W)
                lbl_meas_buf_max.pack(fill=tk.X, side=tk.LEFT)
                self.lbl_meas_buf_max_val = tk.Label(frm, text="100", bg="white", width=4, anchor=tk.E)
                self.lbl_meas_buf_max_val.pack(expand=True, fill=tk.X, side=tk.LEFT)

                self.meas_buf_max = tk.IntVar()
                scl_meas_buf_max = tk.Scale(frm, orient=tk.HORIZONTAL, showvalue=False, from_=1, to=100, resolution=1,
                                            length=70, variable=self.meas_buf_max,
                                            command=self.cb_meas_buf_max)
                scl_meas_buf_max.set(self._meas_buf_max)
                scl_meas_buf_max.pack(expand=True, fill=tk.X, side=tk.LEFT)
                frm = frm.parent

            # Vehicles
            sep_hor = tk.Frame(frm, height=2, bd=1, relief=tk.SUNKEN)
            sep_hor.pack(fill=tk.X, padx=5, pady=5)

            with self.Frame(frm) as frm:
                frm.pack(fill=tk.X)

                self.btn_toggle_vehicle_settings = tk.Button(frm, command=self.cb_toggle_vehicle_settings)
                self.btn_toggle_vehicle_settings.pack(fill=tk.X)

                with self.Frame(frm) as frm:
                    frm.pack(fill=tk.X)
                    self.frm_vehicle_settings_content = frm

                    self.scf_vehicle = ScrollFrame(self.frm_vehicle_settings_content, max_width=200, max_height=100)
                    self.scf_vehicle.update()

                    frm = frm.parent
                self.btn_toggle_vehicle_settings.invoke()
                frm = frm.parent

            # Sensors
            sep_hor = tk.Frame(frm, height=2, bd=1, relief=tk.SUNKEN)
            sep_hor.pack(fill=tk.X, padx=5, pady=5)

            with self.Frame(frm) as frm:
                frm.pack(fill=tk.X)

                self.btn_toggle_sensor_settings = tk.Button(frm, command=self.cb_toggle_sensor_settings)
                self.btn_toggle_sensor_settings.pack(fill=tk.X)

                with self.Frame(frm) as frm:
                    frm.pack(fill=tk.X)
                    self.frm_sensor_settings_content = frm

                    self.scf_sensor = ScrollFrame(self.frm_sensor_settings_content, max_width=200, max_height=100)
                    self.scf_sensor.update()

                    frm = frm.parent
                self.btn_toggle_sensor_settings.invoke()
                frm = frm.parent
            frm = frm.parent

        # The canvas on the bottom right
        # ------------------------------
        with self.Frame(frm) as frm:
            frm.pack(expand=True, fill=tk.BOTH, side=tk.TOP)

            self.canvas = ScaleTransCanvas(frm, width=canvas_width, height=canvas_height,
                                           scale_factor=self._BASE_SCALE_FACTOR,
                                           scale_ratio=1., invert_y=True, center_origin=True, offset_x=0, offset_y=0,
                                           zoom_factor=self._ZOOM_FACTOR)
            self.canvas.pack(expand=True, fill=tk.BOTH)
            self.canvas.bind('<Configure>', self.cb_canvas_configure)
            self.canvas.bind("<MouseWheel>", self.cb_mouse_wheel)  # With Windows OS
            self.canvas.bind('<Button-4>', self.cb_mouse_wheel)  # With Linux OS
            self.canvas.bind('<Button-5>', self.cb_mouse_wheel)  # "
            self.canvas.bind('<Shift-Button-1>', self.cb_left_click_shift)
            self.canvas.bind('<B1-Shift-Motion>', self.cb_shift_motion)
            self.canvas.bind('<ButtonRelease-1>', self.cb_left_click_release)
            self.canvas.bind_all('<space>', self.cb_play_pause)
            self.canvas.bind_all('<Shift-space>', self.cb_single_step)
            self.canvas.bind('<<MotionScaled>>', self.cb_motion_scaled)
            self.canvas.bind_all('<Control-plus>', lambda event, direction=self.ZoomDir.IN: self.cb_zoom(event, direction))
            self.canvas.bind_all('<Control-minus>', lambda event, direction=self.ZoomDir.OUT: self.cb_zoom(event, direction))
            self.canvas.bind_all('<Shift-Left>', lambda event, direction=self.MoveDir.LEFT: self.cb_move(event, direction))
            self.canvas.bind_all('<Shift-Right>', lambda event, direction=self.MoveDir.RIGHT: self.cb_move(event, direction))
            self.canvas.bind_all('<Shift-Up>', lambda event, direction=self.MoveDir.UP: self.cb_move(event, direction))
            self.canvas.bind_all('<Shift-Down>', lambda event, direction=self.MoveDir.DOWN: self.cb_move(event, direction))

            # Context menu
            self.pum_context_menu = PopupMenu(self.canvas, tearoff=0)
            self.pum_context_menu.add_command(label="Reset Transformations", background="orange", command=self.cb_reset_transformations)

            self.canvas.bind("<Button-3>", self.pum_context_menu.popup)
            frm = frm.parent

        self._bv = BaseVisu(self.canvas)
        self._gui_inited = True

    # Play / pause button
    def cb_play_pause(self, _event=None):
        self._play = not self._play

        if self._play:
            self.btn_single_step.config(state=tk.DISABLED)
            self.btn_play_pause.config(text="Pause")
        else:
            self.btn_play_pause.config(text="Play")
            self.btn_single_step.config(state=tk.NORMAL)

    def cb_command_callback(self, _event):
        self.cb_play_pause()
        self._enter_command = True

    # Single step button
    def cb_single_step(self, _event=None):
        self.step()

    def cb_reset_transformations(self):
        self.canvas.zoom = 1.
        self.update_zoom_label()
        self.canvas.set_offset(0, 0)
        self.draw()

    def cb_canvas_configure(self, _event):
        self.draw()

    def update_zoom_label(self):
        self.lbl_zoom_val.config(text="{:.2f}".format(self.canvas.zoom * 100.))

    def cb_mouse_wheel(self, event):
        # Respond to Linux or Windows wheel event
        if event.num == 4 or event.delta == 120:
            self.do_zoom(self.ZoomDir.IN)

        elif event.num == 5 or event.delta == -120:
            self.do_zoom(self.ZoomDir.OUT)

    def cb_left_click_shift(self, event):
        self._move_origin = [event.x, event.y]
        self._move_origin_canvas = self.canvas.get_offset()
        self._move_mode = True

    def cb_shift_motion(self, event):
        if self._move_mode:
            self.canvas.set_offset(self._move_origin_canvas[0] + (event.x - self._move_origin[0]),
                                   self._move_origin_canvas[1] + (event.y - self._move_origin[1]))
            self.draw()
        # end if

    def cb_motion_scaled(self, event):
        self.lbl_cursor_pos_val.config(text="{:5.2f}; {:5.2f}".format(event.x, event.y))

    def cb_left_click_release(self, _event):
        self._move_mode = False

    def do_zoom(self, dir):
        if dir == self.ZoomDir.IN:
            self.canvas.zoom_in()
        else:
            self.canvas.zoom_out()

        self.update_zoom_label()
        self.draw()

    def cb_zoom(self, _event=None, direction=None):
        if direction == self.ZoomDir.IN:
            self.do_zoom(self.ZoomDir.IN)

        elif direction == self.ZoomDir.OUT:
            self.do_zoom(self.ZoomDir.OUT)

    def cb_move(self, _event=None, direction=None):
        offset_x, offset_y = self.canvas.get_offset()

        if direction == self.MoveDir.LEFT:
            self.canvas.set_offset(offset_x - self.canvas.winfo_width() / 10., offset_y)

        elif direction == self.MoveDir.RIGHT:
            self.canvas.set_offset(offset_x + self.canvas.winfo_width() / 10., offset_y)

        elif direction == self.MoveDir.UP:
            self.canvas.set_offset(offset_x, offset_y - self.canvas.winfo_height() / 10.)

        elif direction == self.MoveDir.DOWN:
            self.canvas.set_offset(offset_x, offset_y + self.canvas.winfo_height() / 10.)

        else:
            raise Exception("Invalid movement direction.")

        self.draw()

    def cb_cov_ell_cnt(self, _event):
        cnt = self.cov_ell_cnt.get()

        for sv in range(len(self._sv)):
            self._sv[sv].cov_ell_cnt = cnt

        self.lbl_cov_ell_cnt_val.config(text=cnt)

        self.draw()

    def cb_proj_scale(self, _event):
        scale = self.proj_scale.get()

        self.lbl_proj_scale_val.config(text=scale)

        self.draw()

    def cb_time_incr(self, _event):
        self._t_incr = self.time_incr.get()
        self.lbl_time_incr_val.config(text="{:.1f}".format(self._t_incr))

    def cb_time_tick(self, _event):
        self._t_tick = self.time_tick.get()
        self.lbl_time_tick_val.config(text="{:.2f}".format(self._t_tick))

    def cb_trace_length_max(self, _event):
        self._trace_length_max = self.trace_length_max.get()
        self.lbl_trace_length_max_val.config(text=self._trace_length_max)

        for vv in self._vv:
            vv.trace_length_max = self._trace_length_max

        for sv in self._sv:
            sv.trace_length_max = self._trace_length_max

        for sgv in self._sgv:
            sgv.trace_length_max = self._trace_length_max

    def cb_meas_buf_max(self, _event):
        self._meas_buf_max = self.meas_buf_max.get()
        self.lbl_meas_buf_max_val.config(text=self._meas_buf_max)

        for sv in self._sv:
            sv.meas_buf_max = self._meas_buf_max

    def cb_toggle_trace_settings(self, _event=None):
        self._show_trace_settings = not self._show_trace_settings

        if self._show_trace_settings:
            self.frm_trace_settings_content.pack(fill=tk.X)
            self.btn_toggle_trace_settings.config(text="Hide Trace Settings")
            self.btn_toggle_trace_settings.config(bg="dodgerblue")
        else:
            self.btn_toggle_trace_settings.config(text="Show Trace Settings")
            self.btn_toggle_trace_settings.config(bg="lightblue")
            self.frm_trace_settings_content.pack_forget()

        self.btn_toggle_trace_settings.flash()

    def cb_toggle_vector_settings(self, _event=None):
        self._show_vector_settings = not self._show_vector_settings

        if self._show_vector_settings:
            self.frm_vector_settings_content.pack(fill=tk.X)
            self.btn_toggle_vector_settings.config(text="Hide Vector Settings")
            self.btn_toggle_vector_settings.config(bg="dodgerblue")
        else:
            self.btn_toggle_vector_settings.config(text="Show Vector Settings")
            self.btn_toggle_vector_settings.config(bg="lightblue")
            self.frm_vector_settings_content.pack_forget()

        self.btn_toggle_vector_settings.flash()

    def cb_toggle_projection_settings(self, _event=None):
        self._show_projection_settings = not self._show_projection_settings

        if self._show_projection_settings:
            self.frm_projection_settings_content.pack(fill=tk.X)
            self.btn_toggle_projection_settings.config(text="Hide Projection Settings")
            self.btn_toggle_projection_settings.config(bg="dodgerblue")
        else:
            self.btn_toggle_projection_settings.config(text="Show Projection Settings")
            self.btn_toggle_projection_settings.config(bg="lightblue")
            self.frm_projection_settings_content.pack_forget()

        self.btn_toggle_projection_settings.flash()

    def cb_toggle_vehicle_settings(self, _event=None):
        self._show_vehicle_settings = not self._show_vehicle_settings

        if self._show_vehicle_settings:
            self.frm_vehicle_settings_content.pack(fill=tk.X)
            self.btn_toggle_vehicle_settings.config(text="Hide Vehicle Settings")
            self.btn_toggle_vehicle_settings.config(bg="dodgerblue")
        else:
            self.btn_toggle_vehicle_settings.config(text="Show Vehicle Settings")
            self.btn_toggle_vehicle_settings.config(bg="lightblue")
            self.frm_vehicle_settings_content.pack_forget()

        if self._gui_inited:
            self.btn_toggle_vehicle_settings.flash()

    def cb_toggle_sensor_settings(self, _event=None):
        self._show_sensor_settings = not self._show_sensor_settings

        if self._show_sensor_settings:
            self.frm_sensor_settings_content.pack(fill=tk.X)
            self.btn_toggle_sensor_settings.config(text="Hide Sensor Settings")
            self.btn_toggle_sensor_settings.config(bg="dodgerblue")
        else:
            self.btn_toggle_sensor_settings.config(text="Show Sensor Settings")
            self.btn_toggle_sensor_settings.config(bg="lightblue")
            self.frm_sensor_settings_content.pack_forget()

        if self._gui_inited:
            self.btn_toggle_sensor_settings.flash()

    def cb_draw(self):
        self.draw()

    def clear(self):
        self._bv.clear()

    def draw(self):
        self.clear()
        self._bv.draw()
        self._draw_vehicles()
        self._draw_sensors()
        self._draw_sensors_groups()

    def _draw_vehicles(self):
        for vv in self._vv:
            if vv.vehicle.active:
                vv.draw(draw_pos_trace=self.draw_pos_trace.get(), draw_vel_trace=self.draw_vel_trace.get(),
                        draw_acc_trace=self.draw_acc_trace.get(), draw_tangent_trace=self.draw_tangent_trace.get(),
                        draw_normal_trace=self.draw_normal_trace.get(),
                        draw_acc_times_tangent_trace=self.draw_acc_times_tangent_trace.get(),
                        draw_acc_times_normal_trace=self.draw_acc_times_normal_trace.get(),
                        draw_vel_vec=self.draw_vel_vec.get(),
                        draw_acc_vec=self.draw_acc_vec.get(), draw_tangent=self.draw_tangent.get(),
                        draw_normal=self.draw_normal.get(),
                        proj_dim=self.proj_dim.get(), proj_scale=self.proj_scale.get())

    def _draw_sensors(self):
        for sv in self._sv:
            if sv.sensor.active:
                sv.draw(draw_meas=self.draw_meas.get(),
                        vehicles=[self._vv[v].vehicle for v in range(len(self._vv))])

    def _draw_sensors_groups(self):
        for sgv in self._sgv:
            if sgv.sensor_group.active:
                sgv.draw(draw_meas_filtered=self.draw_meas_filtered.get(),
                         vehicles=[self._vv[v].vehicle for v in range(len(self._vv))])

    def _cb_toggle_vehicle_active(self, variable, vehicle):
        vehicle.active = variable.get()
        self.draw()

    def _cb_toggle_sensor_active(self, variable, sensor):
        sensor.active = variable.get()
        self.draw()

    def _get_sensor_visu_from_sensor(self, sensor):
        for sv in self._sv:
            if sv.sensor is sensor:
                return sv

        return None

    def step(self):
        draw = False
        # Update vehicle positions
        for vv in self._vv:
            v = vv.vehicle
            v.update(self._t)

            # Visualization in canvas
            # -----------------------
            vv.add_cur_vals_to_traces()  # add_cur_vals_to_traces in base class?
            draw = True
        # end for

        for sv in self._sv:
            # Visualization in canvas
            # -----------------------
            sv.add_cur_vals_to_traces()
            draw = True
        # end for

        for sgv in self._sgv:
            # Visualization in canvas
            # -----------------------
            sgv.add_cur_vals_to_traces()
            draw = True
        # end for

        # Update gui elements with current values
        for vv in self._vv:
            if vv.vehicle.active:
                v = vv.vehicle

                self.lbl_pos_x_val.config(text="{:.4f}".format(v.r[0]))
                self.lbl_pos_y_val.config(text="{:.4f}".format(v.r[1]))

                self.lbl_vel_x_val.config(text="{:.4f}".format(v.rd[0]))
                self.lbl_vel_y_val.config(text="{:.4f}".format(v.rd[1]))

                self.lbl_acc_x_val.config(text="{:.4f}".format(v.rdd[0]))
                self.lbl_acc_y_val.config(text="{:.4f}".format(v.rdd[1]))

                break
            # end if
        # end for

        # Make sensor measurements
        for sgv in self._sgv:
            if sgv.sensor_group.trigger(self._t):

                results = []
                for vv in self._vv:
                    v = vv.vehicle
                    results.append(sgv.sensor_group.measure(v))
                # end for

                for s in sgv.sensor_group.sensors:
                    sv = self._get_sensor_visu_from_sensor(s)

                    if sv is not None:
                        sv.add_cur_vals_to_traces()
                # end for
                draw = True
            # end if
        # end if

        self.lbl_time_val.config(text="{:.1f}".format(self._t))
        self._t += self._t_incr

        if draw:
            self.draw()

    def add_vehicle(self, v, **kwargs):
        self._vv.append(VehicleVisu(v, self.canvas, trace_length_max=self._trace_length_max, **kwargs))  # Vehicle visu
        var = tk.BooleanVar()
        chk = tk.Checkbutton(self.scf_vehicle.frame, text=v.name, variable=var,
                             command=lambda variable=var, vehicle=v: self._cb_toggle_vehicle_active(variable, vehicle))
        if v.active:
            chk.select()

        chk.pack(anchor=tk.W)
        self.scf_vehicle.update()
        self.draw()

    def add_sensor(self, s, **kwargs):
        self._sv.append(SensorVisu(s, self.canvas, trace_length_max=self._trace_length_max, meas_buf_max=self._meas_buf_max, **kwargs))  # Sensor visu
        var = tk.BooleanVar()
        chk = tk.Checkbutton(self.scf_sensor.frame, text=s.name, variable=var,
                             command=lambda variable=var, sensor=s: self._cb_toggle_sensor_active(variable, sensor))
        if s.active:
            chk.select()

        chk.pack(anchor=tk.W)
        self.scf_sensor.update()
        self.draw()

    def add_sensor_group(self, sg, **kwargs):
        self._sgv.append(SensorGroupVisu(sg, self.canvas, trace_length_max=self._trace_length_max, **kwargs))  # Sensor group visu

    # This function accepts a callback, since it's not possible to run tkinter in a non-main thread,
    # but we want to handle inputs from the console
    def run(self, auto_play=False, cb_main_loop=None):
        if not self._is_running:  # Prevent multiple executions
            if auto_play:
                self.cb_play_pause()

            while True:
                start = time.time()

                if self._play:
                    self.step()

                # Handle callback into the main program
                if cb_main_loop is not None:
                    if self._enter_command:
                        if cb_main_loop():
                            break

                        self._enter_command = False
                    # end if
                # end if

                # With this loop prevent the program to freeze
                # Handle GUI events - used instead of mainloop(),
                # since latter is blocking and we need to update our stuff
                while True:
                    self.master.update()
                    end = time.time()
                    if end - start > self._t_tick:
                        start += self._t_tick
                        break
                    # end if
                    time.sleep(0.01)
                # end while
            # end while
        # end if
