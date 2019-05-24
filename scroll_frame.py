import tkinter as tk


# A scrollbar that hides itself if it's not needed.
# Only works if you use the grid geometry manager!
class AutoScrollbar(tk.Scrollbar):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self._active = False

    def set(self, lo, hi):
        if float(lo) <= 0.0 and float(hi) >= 1.0:
            self.grid_remove()
            self._active = False
        else:
            self.grid()
            self._active = True

        super().set(lo, hi)

    def pack(self, **kw):
        raise tk.TclError("cannot use pack with this widget")

    def place(self, **kw):
        raise tk.TclError("cannot use place with this widget")

    @property
    def active(self):
        return self._active


class ScrollFrame:
    tag_name = "scroll_frame"

    def __init__(self, master, max_width=0, max_height=0, **kwargs):
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
        master.grid_rowconfigure(0, weight=1)
        master.grid_columnconfigure(0, weight=1)

        # Create frame inside canvas
        self.frame = tk.Frame(self.canvas)
        self.frame.rowconfigure(1, weight=1)
        self.frame.columnconfigure(1, weight=1)

        self.frame.bind('<Configure>', self.reset_scrollregion)

        self.bind_mouse_wheel_event(master)

    def bind_mouse_wheel_event(self, master):
        self.bind_tree(master, '<MouseWheel>', self.cb_mouse_wheel_vertical)  # With Windows OS
        self.bind_tree(master, '<Button-4>', self.cb_mouse_wheel_vertical)  # With Linux OS
        self.bind_tree(master, '<Button-5>', self.cb_mouse_wheel_vertical)  # "

        self.bind_tree(master, '<Shift-MouseWheel>', self.cb_mouse_wheel_horizontal)  # With Windows OS
        self.bind_tree(master, '<Shift-Button-4>', self.cb_mouse_wheel_horizontal)  # With Linux OS
        self.bind_tree(master, '<Shift-Button-5>', self.cb_mouse_wheel_horizontal)  # "

    # Binds an event to a widget and all its descendants
    def bind_tree(self, widget, event, callback, add=''):
        widget.bind(event, callback, add)

        for child in widget.children.values():
            self.bind_tree(child, event, callback, add)

    def update(self):
        self.canvas.create_window(0, 0, anchor=tk.NW, window=self.frame)
        self.frame.update_idletasks()
        self.canvas.config(scrollregion=self.canvas.bbox(tk.ALL))

        if self.frame.winfo_reqwidth() != self.canvas.winfo_width():
            # Update the canvas's width to fit the inner frame
            if self.max_width > 0:
                self.canvas.config(width=min(self.max_width, self.frame.winfo_reqwidth()))
            else:
                self.canvas.config(width=self.frame.winfo_reqwidth())

        if self.frame.winfo_reqheight() != self.canvas.winfo_height():
            # Update the canvas's width to fit the inner frame
            if self.max_height > 0:
                self.canvas.config(height=min(self.max_height, self.frame.winfo_reqheight()))
            else:
                self.canvas.config(height=self.frame.winfo_reqheight())

    def reset_scrollregion(self, _event):
        self.canvas.configure(scrollregion=self.canvas.bbox(tk.ALL))

    def cb_mouse_wheel(self, event, ver):
        # Respond to Linux or Windows wheel event
        if event.num == 4:
            event.delta = 120

        elif event.num == 5:
            event.delta = -120

        if ver:
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), tk.UNITS)
        else:
            self.canvas.xview_scroll(int(-1 * (event.delta / 120)), tk.UNITS)

    def cb_mouse_wheel_horizontal(self, event):
        if self.hscrollbar.active:
            self.cb_mouse_wheel(event, ver=False)

    def cb_mouse_wheel_vertical(self, event):
        if self.vscrollbar.active:
            self.cb_mouse_wheel(event, ver=True)

