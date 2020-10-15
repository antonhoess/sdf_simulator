import tkinter as tk


__author__ = "Anton Höß"
__copyright__ = "Copyright 2020"


class AutoScrollbar(tk.Scrollbar):
    """A scrollbar that hides itself if it's not needed. Only works if you use the grid geometry manager!

    Parameters
    ----------
    master
        The master widget to place this scrollbar in.
    """

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self._active = False
    # end def

    def set(self, lo, hi):
        """Set the fractional values of the slider position (upper and lower ends as value between 0 and 1).

        Parameters
        ----------
        lo : float
            Lower end with a value between 0 and 1.
        hi : float
            Upper end with a value between 0 and 1.
        """
        if float(lo) <= 0.0 and float(hi) >= 1.0:
            self.grid_remove()
            self._active = False
        else:
            self.grid()
            self._active = True

        super().set(lo, hi)
    # end def

    def pack(self, **kw):
        raise tk.TclError("cannot use pack with this widget")
    # end def

    def place(self, **kw):
        raise tk.TclError("cannot use place with this widget")
    # end def

    @property
    def active(self):
        return self._active
    # end def
# end class


class ScrollFrame:
    """A self-made scrollable frame with scrollbars that hide itself if they're not needed.

    Parameters
    ----------
    master
        The master widget to place this scrollbar in.
    max_width : int, optional
        The max. width of the scrollable frame.
    max_height : int, optional
        The max. height of the scrollable frame.
    **kwargs : dict, optional
        Keyword arguments passed to tkinter.Canvas.
    """

    tag_name = "scroll_frame"

    def __init__(self, master, max_width=0, max_height=0, **kwargs):
        self.master = master

        self.max_width = max_width
        self.max_height = max_height

        self.vscrollbar = AutoScrollbar(master)
        self.vscrollbar.grid(row=0, column=1, sticky=tk.N + tk.S)

        self.hscrollbar = AutoScrollbar(master, orient=tk.HORIZONTAL)
        self.hscrollbar.grid(row=1, column=0, sticky=tk.E + tk.W)

        self.canvas = tk.Canvas(master, yscrollcommand=self.vscrollbar.set, xscrollcommand=self.hscrollbar.set, **kwargs)
        self.canvas.grid(row=0, column=0, sticky=tk.N + tk.S + tk.E + tk.W)

        self.vscrollbar.config(command=self.canvas.yview)
        self.hscrollbar.config(command=self.canvas.xview)

        # Make the canvas expandable
        self.master.grid_rowconfigure(0, weight=1)
        self.master.grid_columnconfigure(0, weight=1)

        # Create frame inside canvas
        self.frame = tk.Frame(self.canvas)
        self.frame.rowconfigure(1, weight=1)
        self.frame.columnconfigure(1, weight=1)

        self.frame.bind('<Configure>', self.reset_scrollregion)

        self.bind_mouse_wheel_event(self.master)
    # end def

    def bind_mouse_wheel_event(self, master):
        """Binds mouse scroll events (for different OSs) to the master widget.

        Parameters
        ----------
        master
            The master widget to place this scrollbar in.
        """

        self.bind_tree(master, '<MouseWheel>', self.cb_mouse_wheel_vertical)  # With Windows OS
        self.bind_tree(master, '<Button-4>', self.cb_mouse_wheel_vertical)  # With Linux OS
        self.bind_tree(master, '<Button-5>', self.cb_mouse_wheel_vertical)  # "

        self.bind_tree(master, '<Shift-MouseWheel>', self.cb_mouse_wheel_horizontal)  # With Windows OS
        self.bind_tree(master, '<Shift-Button-4>', self.cb_mouse_wheel_horizontal)  # With Linux OS
        self.bind_tree(master, '<Shift-Button-5>', self.cb_mouse_wheel_horizontal)  # "
    # end def

    #
    def bind_tree(self, widget, event, callback, add=''):
        """Binds an event to a widget and all its descendants recursively.

        Parameters
        ----------
        widget
            The widget to bind the callback to.
        event
            The event to bind to the widget.
        callback
            The callback to call on event.
        add : str, optional
            Specifies whether callback will be called additionally ('+') to the other bound function or whether it will replace the previous function ('').
        """

        widget.bind(event, callback, add)

        for child in widget.children.values():
            self.bind_tree(child, event, callback, add)
        # end for
    # end def

    def update(self):
        """Updates the widgets width and height (when its parent's size changes)."""

        self.bind_mouse_wheel_event(self.master)

        self.canvas.create_window(0, 0, anchor=tk.NW, window=self.frame)
        self.frame.update_idletasks()
        self.canvas.config(scrollregion=self.canvas.bbox(tk.ALL))

        if self.frame.winfo_reqwidth() != self.canvas.winfo_width():
            # Update the canvas's width to fit the inner frame
            if self.max_width > 0:
                self.canvas.config(width=min(self.max_width, self.frame.winfo_reqwidth()))
            else:
                self.canvas.config(width=self.frame.winfo_reqwidth())
            # end if
        # end if

        if self.frame.winfo_reqheight() != self.canvas.winfo_height():
            # Update the canvas's height to fit the inner frame
            if self.max_height > 0:
                self.canvas.config(height=min(self.max_height, self.frame.winfo_reqheight()))
            else:
                self.canvas.config(height=self.frame.winfo_reqheight())
            # end if
        # end if
    # end def

    def reset_scrollregion(self, _event):
        """Resets the size of the scroll-region to the size of the bounding box around all elements when the size of the widget has changed.

        Parameters
        ----------
        _event
            The event information. Not used.
        """

        self.canvas.configure(scrollregion=self.canvas.bbox(tk.ALL))
    # end def

    def cb_mouse_wheel(self, event, ver):
        """The mouse scroll callback that scrolls the window.

        Parameters
        ----------
        event
            The event information.
        ver : bool
            If True, scroll in vertical direction, else scroll in horizontal direction.
        """

        # Respond to Linux or Windows wheel event
        if event.num == 4:
            event.delta = 120

        elif event.num == 5:
            event.delta = -120

        if ver:
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), tk.UNITS)
        else:
            self.canvas.xview_scroll(int(-1 * (event.delta / 120)), tk.UNITS)
        # end if
    # end def

    def cb_mouse_wheel_horizontal(self, event):
        """The horizontal mouse scroll callback.

        Parameters
        ----------
        event
            The event information.
        """

        if self.hscrollbar.active:
            self.cb_mouse_wheel(event, ver=False)
    # end def

    def cb_mouse_wheel_vertical(self, event):
        """The vertical mouse scroll callback.

        Parameters
        ----------
        event
            The event information.
        """

        if self.vscrollbar.active:
            self.cb_mouse_wheel(event, ver=True)
    # end def
# end class
