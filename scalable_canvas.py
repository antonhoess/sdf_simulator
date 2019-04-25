import tkinter as tk


class ScalableCanvas(tk.Canvas):

    # scale_ratio = width / height
    def __init__(self, widget, scale_factor=1.0, scale_ratio=None, invert_y=False,
                 center_origin=False, offset_x=0, offset_y=0, **kwargs):
        super().__init__(widget, **kwargs)

        self._scale_factor = scale_factor
        self._scale_ratio = scale_ratio
        self._invert_y = invert_y
        self._center_origin = center_origin
        self._offset_x = offset_x
        self._offset_y = offset_y

        self._zoom = 1.

    def get_offset(self):
        return self._offset_x, self._offset_y

    def set_offset(self, offset_x, offset_y):
        self._offset_x = offset_x
        self._offset_y = offset_y

    def zoom(self, zoom=1.):
        self._zoom = zoom

    def _create(self, *args, **kwargs):
        x = super()._create(*args, **kwargs)

        width = self.winfo_width()
        height = self.winfo_height()

        if self._scale_ratio is not None:
            ratio = width / height

            if ratio < self._scale_ratio:
                ratio_scale_factor = (width / 2.0 * self._scale_ratio)
            else:
                ratio_scale_factor = (height / 2.0 * self._scale_ratio)

            self.scale(x, 0., 0., ratio_scale_factor, ratio_scale_factor)
        # end if

        if self._invert_y:
            self.scale(x, 0., 0., 1., -1.)

        self.scale(x, 0., 0., self._scale_factor, self._scale_factor)

        self.scale(x, 0., 0., self._zoom, self._zoom)

        if self._center_origin:
            self.move(x, width / 2, height / 2)

        self.move(x, self._offset_x, self._offset_y)

        return x
