import tkinter as tk
import numpy as np


__author__ = "Anton Höß"
__copyright__ = "Copyright 2020"


class ScaleCanvas(tk.Canvas):
    """A canvas that can be scaled.

    Parameters
    ----------
    widget
        The parent widget.
    scale_factor : float, optional
        The scale factor for all objects based to the origin. A value of 1. means the original size.
    scale_ratio : float, optional
        Defines the scale ratio (= width / height) that forces the view to keep this ratio when adjusting the content to its area.
    invert_y : bool, optional
        Inverts the direction of y axis.
    center_origin : bool, optional
        Indicates, if the origin is centered in the viewing area instead of being on (0, 0).
    offset_x : float, optional
        Offset in x-direction.
    offset_y : float, optional
        Offset in y-direction.
    zoom_factor : float, optional
        Defines the zoom factor for one time zooming in or out.
    **kwargs : dict, optional
        Keyword arguments passed to tkinter.Canvas.
    """

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
    # end def

    def _cb_motion(self, event):
        """Callback that handles the mouse move event, transforms the coordinates and call the used defined callback with these scales values.

        Parameters
        ----------
        event
            The event information.
        """

        x, y = self._scale_point(event.x, event.y)

        e = {
            'x': x,
            'y': y
        }

        # We only need to update x and y, since all other values of event are automatically generated.
        # It's not possible to add new key-names
        self.event_generate("<<MotionScaled>>", **e)
    # end def

    def zoom_in(self):
        """Zooms in to make objects appear larger. The zoom center is the current mouse cursor position."""

        zoom_factor_update = 1. * self.zoom_factor
        zoom_factor_diff = abs(zoom_factor_update - 1)
        self.zoom *= self.zoom_factor
        self.set_offset(self.offset_x - (self.winfo_pointerx() - self.winfo_rootx() - (
                self.offset_x + (self.winfo_width() / 2. if self.get_center_origin() else 0.))) * zoom_factor_diff,
                        self.offset_y - (self.winfo_pointery() - self.winfo_rooty() - (self.offset_y + (
                            self.winfo_height() / 2. if self.get_center_origin() else 0.))) * zoom_factor_diff)
    # end def

    def zoom_out(self):
        """Zooms out to make objects appear smaller. The zoom center is the current mouse cursor position."""

        zoom_factor_update = 1. / self.zoom_factor
        zoom_factor_diff = abs(zoom_factor_update - 1)
        self.zoom /= self.zoom_factor
        self.set_offset(self.offset_x + (self.winfo_pointerx() - self.winfo_rootx() - (
                self.offset_x + (self.winfo_width() / 2. if self.get_center_origin() else 0.))) * zoom_factor_diff,
                        self.offset_y + (self.winfo_pointery() - self.winfo_rooty() - (self.offset_y + (
                            self.winfo_height() / 2. if self.get_center_origin() else 0.))) * zoom_factor_diff)
    # end def

    def get_offset(self):
        return self.offset_x, self.offset_y
    # end def

    def set_offset(self, offset_x, offset_y):
        self.offset_x = offset_x
        self.offset_y = offset_y
    # end def

    def get_center_origin(self):
        return self.center_origin
    # end def

    def _scale_point(self, x, y):
        """Scales a given point by applying the basic scaling factor, the zoom factor and the y-inversion.

        Parameters
        ----------
        x : float
            Point's x-coordinate.
        y : float
            Point's y-coordinate.

        Returns
        -------
        (float, float)
            The x and y-coordinate of the scaled point.
        """

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
    # end def

    def _create(self, *args, **kwargs):
        """Applies some transformations after using the tkinter create() function to transform the object's points.

        Parameters
        ----------
        *args : tuple, optional
            Arguments passed to tkinter.Canvas._create().
        **kwargs : dict, optional
            Keyword arguments passed to tkinter.Canvas._create().

        Returns
        -------
        int
            The handle of the created object.
        """

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
    # end def
# end class
