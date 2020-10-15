import tkinter as tk


__author__ = "Anton Höß"
__copyright__ = "Copyright 2020"


class PopupMenu(tk.Menu):
    """A popup menu appearing on the mouse cursor's position.

    Parameters
    ----------
    parent
        The parent widget.
    **kwargs : dict, optional
        Keyword arguments passed to tkinter.Menu.
    """

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
    # end def

    def popup(self, event):
        """Pops up the menu on the event's (= mouse cursor's) position.

        Parameters
        ----------
        event
            Event information.
        """

        try:
            self.tk_popup(event.x_root, event.y_root, 0)
        finally:
            self.grab_release()
        # end try
    # end def
# end class
