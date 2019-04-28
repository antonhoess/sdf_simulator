import tkinter as tk
from vehicle_visu import VehicleVisu
from sensor_visu import SensorVisu
from scalable_canvas import ScalableCanvas
from time import sleep
from enum import Enum


class Gui:
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

        self._vv = []  # Vehicle visualizations
        self._sv = []  # Sensor visualizations

        self._t = 0.0       # Absolute time
        self._t_incr = 1.   # Time increase per tick
        self._t_tick = .01  # Sleep [s] per tick

        self._trace_length_max = int(trace_length_max / self._t_incr)  # Max. length of the trace
        self._meas_buf_max = meas_buf_max  # Max. size of measurements

        self._is_running = False

        self._play = False
        self._enter_command = False

        # For shift the objects on the canvas
        self._move_mode = False
        self._move_origin = [-1, -1]
        self._move_origin_canvas = [-1, -1]

        # Place GUI elements
        self.master = tk.Tk()
        self.master.title("Ground Truth Simulator")

        root = tk.Frame(self.master)
        root.pack(expand=True, fill=tk.BOTH)

        # The view tk.Frame on top
        # ---------------------
        frm_view = tk.Frame(root)
        frm_view.pack(expand=False, fill=tk.X, side=tk.TOP, pady=5)

        # Position
        frm_pos = tk.Frame(frm_view)
        frm_pos.pack(fill=tk.X, side=tk.LEFT, padx=5)

        frm_pos_x = tk.Frame(frm_pos)
        frm_pos_x.pack(side=tk.TOP, padx=5)
        lbl_pos_x = tk.Label(frm_pos_x, text="pos x [m]:", width=9, anchor=tk.W)
        lbl_pos_x.pack(side=tk.LEFT)
        self.lbl_pos_x_val = tk.Label(frm_pos_x, text="", width=10, bg="yellow", anchor=tk.E)
        self.lbl_pos_x_val.pack(side=tk.LEFT)

        frm_pos_y = tk.Frame(frm_pos)
        frm_pos_y.pack(side=tk.TOP, padx=5)
        lbl_pos_y = tk.Label(frm_pos_y, text="pos y [m]:", width=9, anchor=tk.W)
        lbl_pos_y.pack(side=tk.LEFT)
        self.lbl_pos_y_val = tk.Label(frm_pos_y, text="", width=10, bg="yellow", anchor=tk.E)
        self.lbl_pos_y_val.pack(side=tk.LEFT)

        # Velocity
        sep_ver = tk.Frame(frm_view, width=2, bd=1, relief=tk.SUNKEN)
        sep_ver.pack(fill=tk.Y, side=tk.LEFT, padx=0)

        frm_vel = tk.Frame(frm_view)
        frm_vel.pack(fill=tk.X, side=tk.LEFT, padx=5)

        frm_vel_x = tk.Frame(frm_vel)
        frm_vel_x.pack(side=tk.TOP, padx=5)
        lbl_vel_x = tk.Label(frm_vel_x, text="vel. x [m/s]:", width=10, anchor=tk.W)
        lbl_vel_x.pack(side=tk.LEFT)
        self.lbl_vel_x_val = tk.Label(frm_vel_x, text="", width=10, bg="orange", anchor=tk.E)
        self.lbl_vel_x_val.pack(side=tk.LEFT)

        frm_vel_y = tk.Frame(frm_vel)
        frm_vel_y.pack(side=tk.TOP, padx=5)
        lbl_vel_y = tk.Label(frm_vel_y, text="vel. y [m/s]:", width=10, anchor=tk.W)
        lbl_vel_y.pack(side=tk.LEFT)
        self.lbl_vel_y_val = tk.Label(frm_vel_y, text="", width=10, bg="orange", anchor=tk.E)
        self.lbl_vel_y_val.pack(side=tk.LEFT)

        # Acceleration
        sep_ver = tk.Frame(frm_view, width=2, bd=1, relief=tk.SUNKEN)
        sep_ver.pack(fill=tk.Y, side=tk.LEFT, padx=0)

        frm_acc = tk.Frame(frm_view)
        frm_acc.pack(side=tk.LEFT, padx=5)

        frm_acc_x = tk.Frame(frm_acc)
        frm_acc_x.pack(side=tk.TOP, padx=5)
        lbl_acc_x = tk.Label(frm_acc_x, text="accel. x [m/s²]:", width=13, anchor=tk.W)
        lbl_acc_x.pack(side=tk.LEFT)
        self.lbl_acc_x_val = tk.Label(frm_acc_x, text="", width=10, bg="red", anchor=tk.E)
        self.lbl_acc_x_val.pack(side=tk.LEFT)

        frm_acc_y = tk.Frame(frm_acc)
        frm_acc_y.pack(side=tk.TOP, padx=5)
        lbl_acc_y = tk.Label(frm_acc_y, text="accel. y [m/s²]:", width=13, anchor=tk.W)
        lbl_acc_y.pack(side=tk.LEFT)
        self.lbl_acc_y_val = tk.Label(frm_acc_y, text="", width=10, bg="red", anchor=tk.E)
        self.lbl_acc_y_val.pack(side=tk.LEFT)

        sep_hor = tk.Frame(root, height=2, bd=1, relief=tk.SUNKEN)
        sep_hor.pack(fill=tk.X, padx=5, pady=5)

        # Status bar at the bottom
        frm_status = tk.Frame(root)
        frm_status.pack(expand=False, fill=tk.X, side=tk.BOTTOM)

        sep_hor = tk.Frame(root, height=2, bd=1, relief=tk.SUNKEN)
        sep_hor.pack(fill=tk.X, padx=5, pady=5, side=tk.BOTTOM)

        # Cursor position (scaled)
        frm_cursor_pos = tk.Frame(frm_status)
        frm_cursor_pos.pack(fill=tk.X, side=tk.LEFT, pady=5)
        lbl_cursor_pos = tk.Label(frm_cursor_pos, text="cursor pos (x, y):", width=14, anchor=tk.W)
        lbl_cursor_pos.pack(fill=tk.X, side=tk.LEFT)
        self.lbl_cursor_pos_val = tk.Label(frm_cursor_pos, text="0; 0", width=20, bg="yellow")
        self.lbl_cursor_pos_val.pack(fill=tk.X, side=tk.LEFT)

        # Elapsed time
        sep_ver = tk.Frame(frm_status, width=2, bd=1, relief=tk.SUNKEN)
        sep_ver.pack(fill=tk.Y, side=tk.LEFT, padx=5)

        frm_time = tk.Frame(frm_status)
        frm_time.pack(fill=tk.X, side=tk.LEFT, pady=5)
        lbl_time = tk.Label(frm_time, text="t =", width=3, anchor=tk.W)
        lbl_time.pack(fill=tk.X, side=tk.LEFT)
        self.lbl_time_val = tk.Label(frm_time, text="0.0", width=8, bg="yellow", anchor=tk.E)
        self.lbl_time_val.pack(fill=tk.X, side=tk.LEFT)

        # The control tk.Frame on the left
        # -----------------------------
        frm_control = tk.Frame(root)
        frm_control.pack(expand=False, fill=tk.Y, side=tk.LEFT)

        self.btn_play_pause = tk.Button(frm_control, text="Play", width=10, bg="lightblue", command=self.cb_play_pause)
        self.btn_play_pause.pack(fill=tk.X, side=tk.TOP)
        self.btn_play_pause.bind('<Shift-Button-1>', self.cb_command_callback)

        self.btn_single_step = tk.Button(frm_control, text="Step", width=10, bg="lightgreen",
                                         command=self.cb_single_step)
        self.btn_single_step.pack(fill=tk.X, side=tk.TOP)

        btn_reset_transformations = tk.Button(frm_control, text="Reset\nTransformations", width=10, bg="orange",
                                              command=self.cb_reset_transformations)
        btn_reset_transformations.pack(fill=tk.X, side=tk.TOP)

        sep_hor = tk.Frame(frm_control, height=2, bd=1, relief=tk.SUNKEN)
        sep_hor.pack(fill=tk.X, padx=5, pady=5)

        self.draw_pos_trace = tk.IntVar()
        self.draw_pos_trace.set(1)
        chk_draw_pos_trace = tk.Checkbutton(frm_control, text="Draw Pos. Trace", variable=self.draw_pos_trace,
                                            command=self.cb_draw)
        chk_draw_pos_trace.pack(side=tk.TOP, anchor=tk.W)

        self.draw_vel_trace = tk.IntVar()
        chk_draw_vel_trace = tk.Checkbutton(frm_control, text="Draw Vel. Trace", variable=self.draw_vel_trace,
                                            command=self.cb_draw)
        chk_draw_vel_trace.pack(side=tk.TOP, anchor=tk.W)

        self.draw_acc_trace = tk.IntVar()
        chk_draw_acc_trace = tk.Checkbutton(frm_control, text="Draw Accel. Trace", variable=self.draw_acc_trace,
                                            command=self.cb_draw)
        chk_draw_acc_trace.pack(side=tk.TOP, anchor=tk.W)

        self.draw_tangent_trace = tk.IntVar()
        chk_draw_tangent_trace = tk.Checkbutton(frm_control, text="Draw Tangent Trace",
                                                variable=self.draw_tangent_trace,
                                                command=self.cb_draw)
        chk_draw_tangent_trace.pack(side=tk.TOP, anchor=tk.W)

        self.draw_normal_trace = tk.IntVar()
        chk_draw_normal_trace = tk.Checkbutton(frm_control, text="Draw Normal Trace", variable=self.draw_normal_trace,
                                               command=self.cb_draw)
        chk_draw_normal_trace.pack(side=tk.TOP, anchor=tk.W)

        self.draw_acc_times_tangent_trace = tk.IntVar()
        chk_draw_acc_times_tangent_trace = tk.Checkbutton(frm_control, text="Draw Acc. x Tangent Trace",
                                                          variable=self.draw_acc_times_tangent_trace,
                                                          command=self.cb_draw)
        chk_draw_acc_times_tangent_trace.pack(side=tk.TOP, anchor=tk.W)

        self.draw_acc_times_normal_trace = tk.IntVar()
        chk_draw_acc_times_normal_trace = tk.Checkbutton(frm_control, text="Draw Acc. x Normal Trace",
                                                         variable=self.draw_acc_times_normal_trace,
                                                         command=self.cb_draw)
        chk_draw_acc_times_normal_trace.pack(side=tk.TOP, anchor=tk.W)

        # Vectors
        sep_hor = tk.Frame(frm_control, height=2, bd=1, relief=tk.SUNKEN)
        sep_hor.pack(fill=tk.X, padx=5, pady=5)

        self.draw_vel_vec = tk.IntVar()
        chk_draw_vel_vec = tk.Checkbutton(frm_control, text="Draw Vel. Vec.", variable=self.draw_vel_vec,
                                          command=self.cb_draw)
        chk_draw_vel_vec.pack(side=tk.TOP, anchor=tk.W)

        self.draw_acc_vec = tk.IntVar()
        chk_draw_acc_vec = tk.Checkbutton(frm_control, text="Draw Accel. Vec.", variable=self.draw_acc_vec,
                                          command=self.cb_draw)
        chk_draw_acc_vec.pack(side=tk.TOP, anchor=tk.W)

        # Tangent and normal
        sep_hor = tk.Frame(frm_control, height=2, bd=1, relief=tk.SUNKEN)
        sep_hor.pack(fill=tk.X, padx=5, pady=5)

        self.draw_tangent = tk.IntVar()
        chk_draw_tangent = tk.Checkbutton(frm_control, text="Draw Tangent", variable=self.draw_tangent,
                                          command=self.cb_draw)
        chk_draw_tangent.pack(side=tk.TOP, anchor=tk.W)

        self.draw_normal = tk.IntVar()
        chk_draw_normal = tk.Checkbutton(frm_control, text="Draw Normal", variable=self.draw_normal,
                                         command=self.cb_draw)
        chk_draw_normal.pack(side=tk.TOP, anchor=tk.W)

        # Zoom
        sep_hor = tk.Frame(frm_control, height=2, bd=1, relief=tk.SUNKEN)
        sep_hor.pack(fill=tk.X, padx=5, pady=5)

        frm_zoom = tk.Frame(frm_control)
        frm_zoom.pack(fill=tk.X, side=tk.TOP, padx=5)
        lbl_zoom = tk.Label(frm_zoom, text="Zoom [%]:", width=9, anchor=tk.W)
        lbl_zoom.pack(fill=tk.X, side=tk.LEFT)
        self.lbl_zoom_val = tk.Label(frm_zoom, text="{:.2f}".format(1. * 100.), bg="white", anchor=tk.E)
        self.lbl_zoom_val.pack(expand=True, fill=tk.X, side=tk.LEFT)

        btn_zoom_out = tk.Button(frm_zoom, text="-", width=2, bg="lightblue")
        btn_zoom_out.pack(fill=None, side=tk.LEFT)
        btn_zoom_out.bind('<Button-1>', lambda event, dir=self.ZoomDir.OUT: self.cb_zoom(event, dir))

        btn_zoom_in = tk.Button(frm_zoom, text="+", width=2, bg="blue")
        btn_zoom_in.pack(fill=None, side=tk.LEFT)
        btn_zoom_in.bind('<Button-1>', lambda event, dir=self.ZoomDir.IN: self.cb_zoom(event, dir))

        # The canvas tk.Frame on the bottom right
        # ------------------------------------
        frm_canvas = tk.Frame(root)
        frm_canvas.pack(expand=True, fill=tk.BOTH, side=tk.TOP)

        self.canvas = ScalableCanvas(frm_canvas, width=canvas_width, height=canvas_height,
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
        self.canvas.bind('<<MotionScaled>>', self.cb_motion_scaled)
        self.canvas.bind_all('<Control-plus>', lambda event, dir=self.ZoomDir.IN: self.cb_zoom(event, dir))
        self.canvas.bind_all('<Control-minus>', lambda event, dir=self.ZoomDir.OUT: self.cb_zoom(event, dir))
        self.canvas.bind_all('<Shift-Left>', lambda event, dir=self.MoveDir.LEFT: self.cb_move(event, dir))
        self.canvas.bind_all('<Shift-Right>', lambda event, dir=self.MoveDir.RIGHT: self.cb_move(event, dir))
        self.canvas.bind_all('<Shift-Up>', lambda event, dir=self.MoveDir.UP: self.cb_move(event, dir))
        self.canvas.bind_all('<Shift-Down>', lambda event, dir=self.MoveDir.DOWN: self.cb_move(event, dir))

    # Play / pause button
    def cb_play_pause(self, _event=None):
        self._play = not self._play

        if self._play:
            self.btn_single_step.config(state=tk.DISABLED)
            self.btn_play_pause.config(text="Pause")
        else:
            self.btn_play_pause.config(text="Play")
            self.btn_single_step.config(state=tk.NORMAL)

    def cb_command_callback(self, event):
        self.cb_play_pause()
        self._enter_command = True

    # Single step button
    def cb_single_step(self):
        self.step()

    def cb_reset_transformations(self):
        self.canvas.zoom = 1.
        self.update_zoom_label()
        self.canvas.set_offset(0, 0)
        self.draw()

    def cb_canvas_configure(self, event):
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
        # XXX remove the following lines
#        self.clear()
#        self.draw()
#        self.canvas.create_oval_rotated(5000, 1000, 8000, 4000, self.canvas.winfo_pointerx()/100., n_segments=100, fill="", outline="blue",)

    def cb_left_click_release(self, event):
        self._move_mode = False

    def do_zoom(self, dir):
        if dir == self.ZoomDir.IN:
            self.canvas.zoom_in()
        else:
            self.canvas.zoom_out()

        self.update_zoom_label()
        self.draw()

    def cb_zoom(self, _event=None, dir=None):
        if dir == self.ZoomDir.IN:
            self.do_zoom(self.ZoomDir.IN)

        elif dir == self.ZoomDir.OUT:
            self.do_zoom(self.ZoomDir.OUT)

    def cb_move(self, _event=None, dir=None):
        offset_x, offset_y = self.canvas.get_offset()

        if dir == self.MoveDir.LEFT:
            self.canvas.set_offset(offset_x - self.canvas.winfo_width() / 10., offset_y)

        elif dir == self.MoveDir.RIGHT:
            self.canvas.set_offset(offset_x + self.canvas.winfo_width() / 10., offset_y)

        elif dir == self.MoveDir.UP:
            self.canvas.set_offset(offset_x, offset_y - self.canvas.winfo_height() / 10.)

        elif dir == self.MoveDir.DOWN:
            self.canvas.set_offset(offset_x, offset_y + self.canvas.winfo_height() / 10.)

        else:
            raise Exception("Invalid movement direction.")

        self.draw()

    def cb_draw(self):
        self.draw()

    def clear(self):
        self.canvas.delete(tk.ALL)

    def draw(self):
        if len(self._vv) > 0 or len(self._sv) > 0:
            self.clear()

        self._draw_vehicles()
        self._draw_sensors()

    def _draw_vehicles(self):
        for vv in self._vv:
            vv.draw(omit_clear=True, draw_pos_trace=self.draw_pos_trace.get(), draw_vel_trace=self.draw_vel_trace.get(),
                    draw_acc_trace=self.draw_acc_trace.get(), draw_tangent_trace=self.draw_tangent_trace.get(),
                    draw_normal_trace=self.draw_normal_trace.get(),
                    draw_acc_times_tangent_trace=self.draw_acc_times_tangent_trace.get(),
                    draw_acc_times_normal_trace=self.draw_acc_times_normal_trace.get(),
                    draw_vel_vec=self.draw_vel_vec.get(),
                    draw_acc_vec=self.draw_acc_vec.get(), draw_tangent=self.draw_tangent.get(),
                    draw_normal=self.draw_normal.get())

    def _draw_sensors(self):
        for sv in self._sv:
            sv.draw(omit_clear=True)

    def step(self):
        draw = False
        # Update vehicle positions
        for vv in self._vv:
            v = vv.vehicle
            v.update(self._t)

            # Visualization in canvas
            # -----------------------
            vv.add_cur_pos_to_trace()
            vv.add_cur_vel_to_trace()
            vv.add_cur_acc_to_trace()
            vv.add_cur_tangent_to_trace()
            vv.add_cur_normal_to_trace()
            vv.add_cur_acc_times_tangent_to_trace()
            vv.add_cur_acc_times_normal_to_trace()
        # end if

        # Update gui elements with current values
        if len(self._vv) > 0:
            v = self._vv[0].vehicle

            self.lbl_pos_x_val.config(text="{:.4f}".format(v.r[0]))
            self.lbl_pos_y_val.config(text="{:.4f}".format(v.r[1]))

            self.lbl_vel_x_val.config(text="{:.4f}".format(v.rd[0]))
            self.lbl_vel_y_val.config(text="{:.4f}".format(v.rd[1]))

            self.lbl_acc_x_val.config(text="{:.4f}".format(v.rdd[0]))
            self.lbl_acc_y_val.config(text="{:.4f}".format(v.rdd[1]))

            draw = True
        # end if

        # Make sensor measurements
        for sv in self._sv:
            s = sv.sensor

            if self._t >= s.last_meas_time + s.meas_interval:
                s.last_meas_time += s.meas_interval  # Don't loose the modulo rest

                for vv in self._vv:
                    v = vv.vehicle
                    s.measure(v)
                # end for

                draw = True
            # end if
        # end if

        self.lbl_time_val.config(text="{:.1f}".format(self._t))
        self._t += self._t_incr

        if draw:
            self.draw()

    def add_vehicle(self, v, color=None):
        self._vv.append(VehicleVisu(v, self.canvas, color, trace_length_max=self._trace_length_max))  # Vehicle visu

    def add_sensor(self, s, color=None):
        self._sv.append(SensorVisu(s, self.canvas, color, meas_buf_max=self._meas_buf_max))  # Sensor visu

    # This function accepts a callback, since it's not possible to run tkinter in a non-main thread,
    # but we want to handle inputs from the console
    def run(self, auto_play=False, cb_main_loop=None):
        if not self._is_running:  # Prevent multiple executions
            if auto_play:
                self.cb_play_pause()

            while True:
                if self._play:
                    self.step()

                # Handle GUI events - used instead of mainloop(),
                # since latter is blocking and we need to update our stuff
                self.master.update()
                if cb_main_loop is not None:
                    if self._enter_command:
                        if cb_main_loop():
                            break

                        self._enter_command = False
                    # end if
                # end if
                sleep(self._t_tick)
            # end while
        # end if
