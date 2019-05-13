import tkinter as tk


class BaseVisu:
    def __init__(self, canvas):
        self.canvas = canvas

    def draw(self, omit_clear=False, draw_origin_cross=True):
        # Clear canvas
        if not omit_clear:
            self.clear()

        # Draw cross
        if draw_origin_cross:
            x0, y0 = self.canvas.scale_point(0, 0)
            x1, y1 = self.canvas.scale_point(self.canvas.winfo_width(), self.canvas.winfo_height())

            self.canvas.create_line(0, y0, 0, y1, dash=(3, 5))
            self.canvas.create_line(x0, 0, x1, 0, dash=(3, 5))

    def clear(self):
        self.canvas.delete(tk.ALL)
