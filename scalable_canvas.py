import tkinter as tk
import numpy as np


class ScalableCanvas(tk.Canvas):

    # XXX scale_ratio width / height
    def __init__(self, widget, width=100, height=100, scale_factor=1.0, scale_ratio=None, invert_y=False,
                 center_origin=False, offset_x=0, offset_y=0, **kwargs):
        self._canvas_width = width
        self._canvas_height = height

        if scale_ratio is not None:
            ratio = width / height

            if ratio < scale_ratio:
                scale_factor *= (width / 2.0)
            else:
                scale_factor *= (height / 2.0)
        # end if

        self._scale_factor = scale_factor
        self._invert_y = invert_y
        self._center_origin = center_origin
        self._offset_x = offset_x
        self._offset_y = offset_y

        super().__init__(widget, width=width, height=height, **kwargs)

    # def create_line(self, *coords, **options):
    #     super().create_line(*coords, **options)

    def create_line(self, x0, y0, x1, y1, **options):
        p0 = np.asarray([x0, y0])
        p1 = np.asarray([x1, y1])

        if self._invert_y:
            p0 *= np.asarray([1.0, -1.0])
            p1 *= np.asarray([1.0, -1.0])
        # end if

        p0 *= self._scale_factor
        p1 *= self._scale_factor

        if self._center_origin:
            p0 += np.asarray([self._canvas_width / 2, self._canvas_height / 2])
            p1 += np.asarray([self._canvas_width / 2, self._canvas_height / 2])
        # end if

        p0 += np.asarray([self._offset_x, self._offset_y])
        p1 += np.asarray([self._offset_x, self._offset_y])

        super().create_line(p0[0], p0[1], p1[0], p1[1], **options)
