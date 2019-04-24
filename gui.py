import tkinter as tk
from vehicle import Vehicle
from canvas_drawer import CanvasDrawer
from time import sleep
from scalable_canvas import ScalableCanvas


canvas_width = 800
canvas_height = 400

t_incr = 1.0  # Time increase per tick
t_tick = 0.01  # Sleep [s] per tick
trace_length_max = int(100.0 / t_incr)  # Max. length of the trace

play = True


# Play / pause button
def cb_play_pause():
    global play

    play = not play

    if play:
        btn_play_pause.config(text="Pause")
    else:
        btn_play_pause.config(text="Play")


def cb_canvas_configure(event):
    global play

    cd.reset_traces()
    cd.clear()
    cd.set_canvas_width(event.width)
    cd.set_canvas_height(event.height)

    return


master = tk.Tk()
master.title("Ground Truth Simulator")

root = tk.Frame(master)
root.pack(expand=True, fill=tk.BOTH)

# The view tk.Frame on top
# ---------------------
frm_view = tk.Frame(root)
frm_view.pack(expand=False, fill=tk.X, side=tk.TOP, pady=5)

# Position
frm_pos = tk.Frame(frm_view)
frm_pos.pack(fill=tk.X, side=tk.LEFT, padx=5)

frm_pos_x = tk.Frame(frm_pos)
frm_pos_x.pack(fill=tk.X, side=tk.TOP, padx=5)
lbl_pos_x = tk.Label(frm_pos_x, text="pos x [m]:", width=9, anchor=tk.W)
lbl_pos_x.pack(fill=tk.X, side=tk.LEFT)
lbl_pos_x_val = tk.Label(frm_pos_x, text="", width=10, bg="yellow", anchor=tk.E)
lbl_pos_x_val.pack(fill=tk.X, side=tk.LEFT)

frm_pos_y = tk.Frame(frm_pos)
frm_pos_y.pack(fill=tk.X, side=tk.TOP, padx=5)
lbl_pos_y = tk.Label(frm_pos_y, text="pos y [m]:", width=9, anchor=tk.W)
lbl_pos_y.pack(fill=tk.X, side=tk.LEFT)
lbl_pos_y_val = tk.Label(frm_pos_y, text="", width=10, bg="yellow", anchor=tk.E)
lbl_pos_y_val.pack(fill=tk.X, side=tk.LEFT)

# Velocity
sep_ver_ctrl_1 = tk.Frame(frm_view, width=2, bd=1, relief=tk.SUNKEN)
sep_ver_ctrl_1.pack(fill=tk.Y, side=tk.LEFT, padx=0)

frm_vel = tk.Frame(frm_view)
frm_vel.pack(fill=tk.X, side=tk.LEFT, padx=5)

frm_vel_x = tk.Frame(frm_vel)
frm_vel_x.pack(fill=tk.X, side=tk.TOP, padx=5)
lbl_vel_x = tk.Label(frm_vel_x, text="vel. x [m/s]:", width=10, anchor=tk.W)
lbl_vel_x.pack(fill=tk.X, side=tk.LEFT)
lbl_vel_x_val = tk.Label(frm_vel_x, text="", width=10, bg="orange", anchor=tk.E)
lbl_vel_x_val.pack(fill=tk.X, side=tk.LEFT)

frm_vel_y = tk.Frame(frm_vel)
frm_vel_y.pack(fill=tk.X, side=tk.TOP, padx=5)
lbl_vel_y = tk.Label(frm_vel_y, text="vel. y [m/s]:", width=10, anchor=tk.W)
lbl_vel_y.pack(fill=tk.X, side=tk.LEFT)
lbl_vel_y_val = tk.Label(frm_vel_y, text="", width=10, bg="orange", anchor=tk.E)
lbl_vel_y_val.pack(fill=tk.X, side=tk.LEFT)

# Acceleration
sep_ver_ctrl_2 = tk.Frame(frm_view, width=2, bd=1, relief=tk.SUNKEN)
sep_ver_ctrl_2.pack(fill=tk.Y, side=tk.LEFT, padx=0)

frm_acc = tk.Frame(frm_view)
frm_acc.pack(fill=tk.X, side=tk.LEFT, padx=5)

frm_acc_x = tk.Frame(frm_acc)
frm_acc_x.pack(fill=tk.X, side=tk.TOP, padx=5)
lbl_acc_x = tk.Label(frm_acc_x, text="accel. x [m/s²]:", width=13, anchor=tk.W)
lbl_acc_x.pack(fill=tk.X, side=tk.LEFT)
lbl_acc_x_val = tk.Label(frm_acc_x, text="", width=10, bg="red", anchor=tk.E)
lbl_acc_x_val.pack(fill=tk.X, side=tk.LEFT)

frm_acc_y = tk.Frame(frm_acc)
frm_acc_y.pack(fill=tk.X, side=tk.TOP, padx=5)
lbl_acc_y = tk.Label(frm_acc_y, text="accel. y [m/s²]:", width=13, anchor=tk.W)
lbl_acc_y.pack(fill=tk.X, side=tk.LEFT)
lbl_acc_y_val = tk.Label(frm_acc_y, text="", width=10, bg="red", anchor=tk.E)
lbl_acc_y_val.pack(fill=tk.X, side=tk.LEFT)

sep_hor_1 = tk.Frame(root, height=2, bd=1, relief=tk.SUNKEN)
sep_hor_1.pack(fill=tk.X, padx=5, pady=5)

# The control tk.Frame on the left
# -----------------------------
frm_control = tk.Frame(root)
frm_control.pack(expand=False, fill=tk.Y, side=tk.LEFT)

btn_play_pause = tk.Button(frm_control, text="Pause", width=10, bg="lightblue", command=cb_play_pause)
btn_play_pause.pack(fill=tk.X, side=tk.TOP)

draw_pos_trace = tk.IntVar()
draw_pos_trace.set(1)
chk_draw_pos_trace = tk.Checkbutton(frm_control, text="Draw Pos. Trace", variable=draw_pos_trace)
chk_draw_pos_trace.pack(side=tk.TOP, anchor=tk.W)

draw_vel_trace = tk.IntVar()
chk_draw_vel_trace = tk.Checkbutton(frm_control, text="Draw Vel. Trace", variable=draw_vel_trace)
chk_draw_vel_trace.pack(side=tk.TOP, anchor=tk.W)

draw_acc_trace = tk.IntVar()
chk_draw_acc_trace = tk.Checkbutton(frm_control, text="Draw Accel. Trace", variable=draw_acc_trace)
chk_draw_acc_trace.pack(side=tk.TOP, anchor=tk.W)

draw_tangent_trace = tk.IntVar()
chk_draw_tangent_trace = tk.Checkbutton(frm_control, text="Draw Tangent Trace", variable=draw_tangent_trace)
chk_draw_tangent_trace.pack(side=tk.TOP, anchor=tk.W)

draw_normal_trace = tk.IntVar()
chk_draw_normal_trace = tk.Checkbutton(frm_control, text="Draw Normal Trace", variable=draw_normal_trace)
chk_draw_normal_trace.pack(side=tk.TOP, anchor=tk.W)

draw_acc_times_tangent_trace = tk.IntVar()
chk_draw_acc_times_tangent_trace = tk.Checkbutton(frm_control, text="Draw Acc. x Tangent Trace",
                                                  variable=draw_acc_times_tangent_trace)
chk_draw_acc_times_tangent_trace.pack(side=tk.TOP, anchor=tk.W)

draw_acc_times_normal_trace = tk.IntVar()
chk_draw_acc_times_normal_trace = tk.Checkbutton(frm_control, text="Draw Acc. x Normal Trace",
                                                 variable=draw_acc_times_normal_trace)
chk_draw_acc_times_normal_trace.pack(side=tk.TOP, anchor=tk.W)

sep_hor_2 = tk.Frame(frm_control, height=2, bd=1, relief=tk.SUNKEN)
sep_hor_2.pack(fill=tk.X, padx=5, pady=5)

draw_vel_vec = tk.IntVar()
chk_draw_vel_vec = tk.Checkbutton(frm_control, text="Draw Vel. Vec.", variable=draw_vel_vec)
chk_draw_vel_vec.pack(side=tk.TOP, anchor=tk.W)

draw_acc_vec = tk.IntVar()
chk_draw_acc_vec = tk.Checkbutton(frm_control, text="Draw Accel. Vec.", variable=draw_acc_vec)
chk_draw_acc_vec.pack(side=tk.TOP, anchor=tk.W)

sep_hor_3 = tk.Frame(frm_control, height=2, bd=1, relief=tk.SUNKEN)
sep_hor_3.pack(fill=tk.X, padx=5, pady=5)

draw_tangent = tk.IntVar()
chk_draw_tangent = tk.Checkbutton(frm_control, text="Draw Tangent", variable=draw_tangent)
chk_draw_tangent.pack(side=tk.TOP, anchor=tk.W)

draw_normal = tk.IntVar()
chk_draw_normal = tk.Checkbutton(frm_control, text="Draw Normal", variable=draw_normal)
chk_draw_normal.pack(side=tk.TOP, anchor=tk.W)


# The canvas tk.Frame on the bottom right
# ------------------------------------
frm_canvas = tk.Frame(root)
frm_canvas.pack(expand=True, fill=tk.BOTH, side=tk.TOP)

canvas = ScalableCanvas(frm_canvas, width=canvas_width, height=canvas_height, scale_factor=1.0e-4, scale_ratio=1.0,
                        invert_y=True, center_origin=True, offset_x=0, offset_y=0)
canvas.pack(expand=True, fill=tk.BOTH)
canvas.bind('<Configure>', cb_canvas_configure)


# Non-GUI initialization
# ----------------------
v = Vehicle("Vehicle", 300.0, 9.0)
cd = CanvasDrawer(v, canvas, canvas_width, canvas_height, trace_length_max=trace_length_max)
t = 0.0


while True:
    if play:
        # Update vehicle position
        v.update(t)

        # Update gui elements with current values
        lbl_pos_x_val.config(text="{:.4f}".format(v.r[0]))
        lbl_pos_y_val.config(text="{:.4f}".format(v.r[1]))

        lbl_vel_x_val.config(text="{:.4f}".format(v.rd[0]))
        lbl_vel_y_val.config(text="{:.4f}".format(v.rd[1]))

        lbl_acc_x_val.config(text="{:.4f}".format(v.rdd[0]))
        lbl_acc_y_val.config(text="{:.4f}".format(v.rdd[1]))

        # Visualization in canvas
        # -----------------------
        cd.add_cur_pos_to_trace()
        cd.add_cur_vel_to_trace()
        cd.add_cur_acc_to_trace()
        cd.add_cur_tangent_to_trace()
        cd.add_cur_normal_to_trace()
        cd.add_cur_acc_times_tangent_to_trace()
        cd.add_cur_acc_times_normal_to_trace()

        cd.draw(draw_pos_trace=draw_pos_trace.get(), draw_vel_trace=draw_vel_trace.get(),
                draw_acc_trace=draw_acc_trace.get(), draw_tangent_trace=draw_tangent_trace.get(),
                draw_normal_trace=draw_normal_trace.get(),
                draw_acc_times_tangent_trace=draw_acc_times_tangent_trace.get(),
                draw_acc_times_normal_trace=draw_acc_times_normal_trace.get(),
                draw_vel_vec=draw_vel_vec.get(),
                draw_acc_vec=draw_acc_vec.get(), draw_tangent=draw_tangent.get(), draw_normal=draw_normal.get())

        t += t_incr
    # end if

    # Several updates
    master.update()  # Handle GUI events
    sleep(t_tick)
# end while

# mainloop()
