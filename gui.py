from tkinter import *
from vehicle import Vehicle
from canvas_drawer import CanvasDrawer
from time import sleep
import numpy as np


canvas_width = 800
canvas_height = 400

t_incr = 1.0 # Time increase per tick
t_tick = 0.001 # Sleep [s] per tick
trace_length_max = int(100.0 / t_incr) # Max. length of the trace


master = Tk()
master.title("Ground Truth Simulator")

root = Frame(master)
root.pack()

control_frame = Frame(root)
control_frame.pack(expand=True, fill=X, side=TOP)

# Position
frm_pos = Frame(control_frame)
frm_pos.pack(fill=X, side=LEFT, padx=5)

frm_pos_x = Frame(frm_pos)
frm_pos_x.pack(fill=X, side=TOP, padx=5)
lbl_pos_x = Label(frm_pos_x, text="pos x [m]:")
lbl_pos_x.pack(fill=X, side=LEFT)
lbl_pos_x_val = Label(frm_pos_x, text="", width=10, bg="yellow", anchor=E)
lbl_pos_x_val.pack(fill=X, side=LEFT)

frm_pos_y = Frame(frm_pos)
frm_pos_y.pack(fill=X, side=TOP, padx=5)
lbl_pos_y = Label(frm_pos_y, text="pos y [m]:")
lbl_pos_y.pack(fill=X, side=LEFT)
lbl_pos_y_val = Label(frm_pos_y, text="", width=10, bg="yellow", anchor=E)
lbl_pos_y_val.pack(fill=X, side=LEFT)

# Velocity
frm_vel = Frame(control_frame)
frm_vel.pack(fill=X, side=LEFT, padx=5)

frm_vel_x = Frame(frm_vel)
frm_vel_x.pack(fill=X, side=TOP, padx=5)
lbl_vel_x = Label(frm_vel_x, text="vel. x [m/s]:")
lbl_vel_x.pack(fill=X, side=LEFT)
lbl_vel_x_val = Label(frm_vel_x, text="", width=10, bg="orange", anchor=E)
lbl_vel_x_val.pack(fill=X, side=LEFT)

frm_vel_y = Frame(frm_vel)
frm_vel_y.pack(fill=X, side=TOP, padx=5)
lbl_vel_y = Label(frm_vel_y, text="vel. y [m/s]:")
lbl_vel_y.pack(fill=X, side=LEFT)
lbl_vel_y_val = Label(frm_vel_y, text="", width=10, bg="orange", anchor=E)
lbl_vel_y_val.pack(fill=X, side=LEFT)

# XXX doch besser grid


sep_ver_ctrl_1 = Frame(control_frame, width=2, bd=1, relief=SUNKEN)
sep_ver_ctrl_1.pack(fill=X, side=LEFT, padx=5)

lbl_accel = Label(control_frame, text="accel. [m/s²]:")
lbl_accel.pack(fill=X, side=LEFT)

lbl_accel_val = Label(control_frame, text="", width=10, bg="red", anchor=E)
lbl_accel_val.pack(fill=X, side=LEFT)

sep_hor = Frame(root, height=2, bd=1, relief=SUNKEN)
sep_hor.pack(fill=X, padx=5, pady=5)

canvas_frame = Frame(root)
canvas_frame.pack(side=TOP)

canvas = Canvas(canvas_frame, width=canvas_width, height=canvas_height)
canvas.pack()

v = Vehicle("Vehicle", 300.0, 9.0)
cd = CanvasDrawer(v, canvas, canvas_width, canvas_height, 0.01, trace_length_max=100)
t = 0.0

while True:
	# Update vehicle position
	v.update(t)

	# Update gui elements with current values
	lbl_pos_x_val.config(text="{:.4f}".format(v.r[0]))
	lbl_pos_y_val.config(text="{:.4f}".format(v.r[1]))
	
	lbl_vel_x_val.config(text="{:.4f}".format(v.rd[0]))
	lbl_vel_y_val.config(text="{:.4f}".format(v.rd[1]))
	
	
	#lbl_accel_val.config(text="{:.4f}".format(v.r[1]))

	## Visualization in canvas
	## -----------------------
	cd.add_cur_pos_to_trace()
	cd.draw()
	
	# Several updates
	master.update() # Handle GUI events
	sleep(t_tick)
	t += t_incr
# end while

# mainloop()
