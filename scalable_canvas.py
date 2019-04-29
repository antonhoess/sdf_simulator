import tkinter as tk
import numpy as np
import math


class ScalableCanvas(tk.Canvas):
    # scale_ratio = width / height
    def __init__(self, widget, scale_factor=1.0, scale_ratio=None, invert_y=False,
                 center_origin=False, offset_x=0, offset_y=0, zoom_factor=1., **kwargs):
        super().__init__(widget, **kwargs)

        self.scale_factor = scale_factor
        self.scale_ratio = scale_ratio
        self.invert_y = invert_y
        self.center_origin = center_origin
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.zoom_factor = zoom_factor

        self.zoom = 1.

        self.bind("<Motion>", self._cb_motion)

    def _cb_motion(self, event):
        x, y = self._scale_point(event.x, event.y)

        e = {
            'x': x,
            'y': y
        }

        # We only need to update x and y, since all other values of event are automatically generated.
        # It's not possible to add new key-names
        self.event_generate("<<MotionScaled>>", **e)

    def zoom_in(self):
        zoom_factor_update = 1. * self.zoom_factor
        zoom_factor_diff = abs(zoom_factor_update - 1)
        self.zoom *= self.zoom_factor

        # Zoom center around the canvas origin if cursor is outside of the canvas
        pointerx = self.winfo_pointerx() - self.winfo_rootx()
        pointery = self.winfo_pointery() - self.winfo_rooty()
        if pointerx < 0 or pointerx > self.winfo_width() or\
            pointery < 0 or pointery > self.winfo_height():
            pointerx = self.winfo_width() / 2.
            pointery = self.winfo_height() / 2.
        # end if

        self.set_offset(self.offset_x - (
        pointerx - (self.offset_x + (self.winfo_width() / 2. if self.get_center_origin() else 0.))) * zoom_factor_diff,
                        self.offset_y - (pointery - (self.offset_y + (
                        self.winfo_height() / 2. if self.get_center_origin() else 0.))) * zoom_factor_diff)

    def zoom_out(self):
        zoom_factor_update = 1. / self.zoom_factor
        zoom_factor_diff = abs(zoom_factor_update - 1)
        self.zoom /= self.zoom_factor

        # Zoom center around the canvas origin if cursor is outside of the canvas
        pointerx = self.winfo_pointerx() - self.winfo_rootx()
        pointery = self.winfo_pointery() - self.winfo_rooty()
        if pointerx < 0 or pointerx > self.winfo_width() or \
                        pointery < 0 or pointery > self.winfo_height():
            pointerx = self.winfo_width() / 2.
            pointery = self.winfo_height() / 2.
        # end if

        self.set_offset(self.offset_x + (pointerx - (
            self.offset_x + (self.winfo_width() / 2. if self.get_center_origin() else 0.))) * zoom_factor_diff,
                        self.offset_y + (pointery - (self.offset_y + (
                            self.winfo_height() / 2. if self.get_center_origin() else 0.))) * zoom_factor_diff)

    def get_offset(self):
        return self.offset_x, self.offset_y

    def set_offset(self, offset_x, offset_y):
        self.offset_x = offset_x
        self.offset_y = offset_y

    def get_center_origin(self):
        return self.center_origin

    def create_oval_rotated(self, x, y, r1, r2, theta, n_segments=10, *args, **kwargs):
        coords = []

        # Adapted from https://stackoverflow.com/questions/22694850/approximating-an-ellipse-with-a-polygon
        # I've removed Nth point calculation, that involves indefinite Tan(Pi/2)
        # It would better to assign known value 0 to Fi in this point
        for i in range(-n_segments, n_segments):
            _theta = math.pi / 2. * i / n_segments
            phi = math.pi / 2. - math.atan(math.tan(_theta) * r1 / r2)
            _x = r1 * math.cos(phi)
            _y = r2 * math.sin(phi)
            coords.append(np.asarray([_x, _y]))
        # end for

        # Duplicate the upper half of the ellipse to the bottom (mirrored)
        for c in range(len(coords) - 1, 0, -1):
            coords.append(np.copy(coords[c]) * np.asarray([1, -1]))

        # Rotate and translate the ellipse
        c, s = np.cos(theta), np.sin(theta)
        R = np.array(((c, -s), (s, c)))  # Rotation matrix
        O = np.asarray([x, y])  # Offset vector

        for c in range(len(coords)):
            coords[c] = np.dot(coords[c], R.T) + O

        # Create list with x0, y0, x1, y1, x2, ...
        _coords = []
        for c in coords:
            _coords.append(c[0])
            _coords.append(c[1])
        # end for

        return self.create_polygon(_coords, *args, **kwargs)

    def _scale_point(self, x, y):
        p = np.asarray([x, y], dtype=np.float)

        width = self.winfo_width()
        height = self.winfo_height()

        if self.center_origin:
            p -= np.asarray([width / 2, height / 2])

        p -= np.asarray([self.offset_x, self.offset_y])

        if self.scale_ratio is not None:
            ratio = width / height

            if ratio < self.scale_ratio:
                ratio_scale_factor = (width / 2.0 * self.scale_ratio)
            else:
                ratio_scale_factor = (height / 2.0 * self.scale_ratio)

            p /= ratio_scale_factor
        # end if

        if self.invert_y:
            p *= np.asarray([1., -1.])

        p /= self.scale_factor

        p /= self.zoom

        return p[0], p[1]

    def _create(self, *args, **kwargs):
        x = super()._create(*args, **kwargs)

        width = self.winfo_width()
        height = self.winfo_height()

        if self.scale_ratio is not None:
            ratio = width / height

            if ratio < self.scale_ratio:
                ratio_scale_factor = (width / 2.0 * self.scale_ratio)
            else:
                ratio_scale_factor = (height / 2.0 * self.scale_ratio)

            self.scale(x, 0., 0., ratio_scale_factor, ratio_scale_factor)
        # end if

        if self.invert_y:
            self.scale(x, 0., 0., 1., -1.)

        self.scale(x, 0., 0., self.scale_factor, self.scale_factor)

        self.scale(x, 0., 0., self.zoom, self.zoom)

        if self.center_origin:
            self.move(x, width / 2, height / 2)

        self.move(x, self.offset_x, self.offset_y)

        return x
