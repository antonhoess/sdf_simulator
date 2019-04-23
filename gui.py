from tkinter import *
from vehicle import Vehicle
from canvas_drawer import CanvasDrawer
from time import sleep


canvas_width = 800
canvas_height = 400

t_incr = 1.0  # Time increase per tick
t_tick = 0.001  # Sleep [s] per tick
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


master = Tk()
master.title("Ground Truth Simulator")

root = Frame(master)
root.pack()

# The view frame on top
# ---------------------
view_frame = Frame(root)
view_frame.pack(expand=True, fill=X, side=TOP)

# Position
frm_pos = Frame(view_frame)
frm_pos.pack(fill=X, side=LEFT, padx=5)

frm_pos_x = Frame(frm_pos)
frm_pos_x.pack(fill=X, side=TOP, padx=5)
lbl_pos_x = Label(frm_pos_x, text="pos x [m]:", width=9, anchor=W)
lbl_pos_x.pack(fill=X, side=LEFT)
lbl_pos_x_val = Label(frm_pos_x, text="", width=10, bg="yellow", anchor=E)
lbl_pos_x_val.pack(fill=X, side=LEFT)

frm_pos_y = Frame(frm_pos)
frm_pos_y.pack(fill=X, side=TOP, padx=5)
lbl_pos_y = Label(frm_pos_y, text="pos y [m]:", width=9, anchor=W)
lbl_pos_y.pack(fill=X, side=LEFT)
lbl_pos_y_val = Label(frm_pos_y, text="", width=10, bg="yellow", anchor=E)
lbl_pos_y_val.pack(fill=X, side=LEFT)

# Velocity
sep_ver_ctrl_1 = Frame(view_frame, width=2, bd=1, relief=SUNKEN)
sep_ver_ctrl_1.pack(fill=Y, side=LEFT, padx=0)

frm_vel = Frame(view_frame)
frm_vel.pack(fill=X, side=LEFT, padx=5)

frm_vel_x = Frame(frm_vel)
frm_vel_x.pack(fill=X, side=TOP, padx=5)
lbl_vel_x = Label(frm_vel_x, text="vel. x [m/s]:", width=10, anchor=W)
lbl_vel_x.pack(fill=X, side=LEFT)
lbl_vel_x_val = Label(frm_vel_x, text="", width=10, bg="orange", anchor=E)
lbl_vel_x_val.pack(fill=X, side=LEFT)

frm_vel_y = Frame(frm_vel)
frm_vel_y.pack(fill=X, side=TOP, padx=5)
lbl_vel_y = Label(frm_vel_y, text="vel. y [m/s]:", width=10, anchor=W)
lbl_vel_y.pack(fill=X, side=LEFT)
lbl_vel_y_val = Label(frm_vel_y, text="", width=10, bg="orange", anchor=E)
lbl_vel_y_val.pack(fill=X, side=LEFT)

# Acceleration
sep_ver_ctrl_2 = Frame(view_frame, width=2, bd=1, relief=SUNKEN)
sep_ver_ctrl_2.pack(fill=Y, side=LEFT, padx=0)

frm_acc = Frame(view_frame)
frm_acc.pack(fill=X, side=LEFT, padx=5)

frm_acc_x = Frame(frm_acc)
frm_acc_x.pack(fill=X, side=TOP, padx=5)
lbl_acc_x = Label(frm_acc_x, text="accel. x [m/s²]:", width=13, anchor=W)
lbl_acc_x.pack(fill=X, side=LEFT)
lbl_acc_x_val = Label(frm_acc_x, text="", width=10, bg="red", anchor=E)
lbl_acc_x_val.pack(fill=X, side=LEFT)

frm_acc_y = Frame(frm_acc)
frm_acc_y.pack(fill=X, side=TOP, padx=5)
lbl_acc_y = Label(frm_acc_y, text="accel. y [m/s²]:", width=13, anchor=W)
lbl_acc_y.pack(fill=X, side=LEFT)
lbl_acc_y_val = Label(frm_acc_y, text="", width=10, bg="red", anchor=E)
lbl_acc_y_val.pack(fill=X, side=LEFT)

sep_hor_1 = Frame(root, height=2, bd=1, relief=SUNKEN)
sep_hor_1.pack(fill=X, padx=5, pady=5)

# The control frame on the left
# -----------------------------
control_frame = Frame(root)
control_frame.pack(expand=True, fill=Y, side=LEFT)

btn_play_pause = Button(control_frame, text="Pause", width=10, bg="lightblue", command=cb_play_pause)
btn_play_pause.pack(fill=X, side=TOP)

draw_pos_trace = IntVar()
draw_pos_trace.set(1)
chk_draw_pos_trace = Checkbutton(control_frame, text="Draw Pos. Trace", variable=draw_pos_trace)
chk_draw_pos_trace.pack(side=TOP, anchor=W)

draw_vel_trace = IntVar()
chk_draw_vel_trace = Checkbutton(control_frame, text="Draw Vel. Trace", variable=draw_vel_trace)
chk_draw_vel_trace.pack(side=TOP, anchor=W)

draw_acc_trace = IntVar()
chk_draw_acc_trace = Checkbutton(control_frame, text="Draw Accel. Trace", variable=draw_acc_trace)
chk_draw_acc_trace.pack(side=TOP, anchor=W)

draw_tangent_trace = IntVar()
chk_draw_tangent_trace = Checkbutton(control_frame, text="Draw Tangent Trace", variable=draw_tangent_trace)
chk_draw_tangent_trace.pack(side=TOP, anchor=W)

draw_normal_trace = IntVar()
chk_draw_normal_trace = Checkbutton(control_frame, text="Draw Normal Trace", variable=draw_normal_trace)
chk_draw_normal_trace.pack(side=TOP, anchor=W)

draw_acc_times_tangent_trace = IntVar()
chk_draw_acc_times_tangent_trace = Checkbutton(control_frame, text="Draw Acc. x Tangent Trace",
                                               variable=draw_acc_times_tangent_trace)
chk_draw_acc_times_tangent_trace.pack(side=TOP, anchor=W)

draw_acc_times_normal_trace = IntVar()
chk_draw_acc_times_normal_trace = Checkbutton(control_frame, text="Draw Acc. x Normal Trace",
                                              variable=draw_acc_times_normal_trace)
chk_draw_acc_times_normal_trace.pack(side=TOP, anchor=W)

sep_hor_2 = Frame(control_frame, height=2, bd=1, relief=SUNKEN)
sep_hor_2.pack(fill=X, padx=5, pady=5)

draw_vel_vec = IntVar()
chk_draw_vel_vec = Checkbutton(control_frame, text="Draw Vel. Vec.", variable=draw_vel_vec)
chk_draw_vel_vec.pack(side=TOP, anchor=W)

draw_acc_vec = IntVar()
chk_draw_acc_vec = Checkbutton(control_frame, text="Draw Accel. Vec.", variable=draw_acc_vec)
chk_draw_acc_vec.pack(side=TOP, anchor=W)

sep_hor_3 = Frame(control_frame, height=2, bd=1, relief=SUNKEN)
sep_hor_3.pack(fill=X, padx=5, pady=5)

draw_tangent = IntVar()
chk_draw_tangent = Checkbutton(control_frame, text="Draw Tangent", variable=draw_tangent)
chk_draw_tangent.pack(side=TOP, anchor=W)

draw_normal = IntVar()
chk_draw_normal = Checkbutton(control_frame, text="Draw Normal", variable=draw_normal)
chk_draw_normal.pack(side=TOP, anchor=W)


# The canvas frame on the bottom right
# ------------------------------------
canvas_frame = Frame(root)
canvas_frame.pack(side=TOP)

canvas = Canvas(canvas_frame, width=canvas_width, height=canvas_height)
canvas.pack()

# Non-GUI initialization
# ----------------------
v = Vehicle("Vehicle", 300.0, 9.0)
cd = CanvasDrawer(v, canvas, canvas_width, canvas_height, 0.01, trace_length_max=100)
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
