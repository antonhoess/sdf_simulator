from tkinter import *
import numpy as np


class CanvasDrawer:
	
	def __init__(self, vehicle, canvas, canvas_width, canvas_height, scale_factor, trace_length_max=10):
		self.vehicle = vehicle
		self.canvas = canvas
		self.canvas_width = canvas_width
		self.canvas_height = canvas_height
		self.scale_factor = scale_factor
		self.trace_length_max = trace_length_max
		
		self.trace = []

	def scale_for_canvas(self, v):
		return v * self.scale_factor * np.asarray([1.0, -1.0]) + np.asarray([self.canvas_width / 2, self.canvas_height / 2])


	# Update trace array
	def add_cur_pos_to_trace(self):
		self.trace.append(self.scale_for_canvas(self.vehicle.r))
		if len(self.trace) > self.trace_length_max: # Limit trace array length
			self.trace.pop(0)

	def draw(self):
		# Clear canvas
		self.canvas.delete("all")

		# Draw trace array
		for step in range(1, len(self.trace)):
			x = step / float(self.trace_length_max - 1)
			self.canvas.create_line(self.trace[step-1][0], self.trace[step-1][1], self.trace[step][0], self.trace[step][1], width=5.0, capstyle=ROUND, fill="#{:02x}{:02x}{:02x}".format(int(x * 255), 0, int((1 - x) * 255)))
		# end for
		
		# Draw velocity vector
		v = self.vehicle
		r = self.scale_for_canvas(v.r)
		
		# Draw acceleration vector
		rd = v.rd * np.asarray([1.0, -1.0]) * 0.5
		rdd = v.rdd * np.asarray([1.0, -1.0]) * 5.0
		
		self.canvas.create_line(r[0], r[1], r[0] + rd[0], r[1] + rd[1], width=2.0, capstyle=ROUND, fill="#000000")
		self.canvas.create_line(r[0], r[1], r[0] + rdd[0], r[1] + rdd[1], width=2.0, capstyle=ROUND, fill="#00FF00")

			
