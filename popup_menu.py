import tkinter as tk


class PopupMenu(tk.Menu):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)

    def popup(self, event):
        try:
            self.tk_popup(event.x_root, event.y_root, 0)
        finally:
            self.grab_release()
