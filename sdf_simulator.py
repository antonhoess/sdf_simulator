from vehicle import Vehicle
from gui import Gui


def cb_main_loop():
    s = input("Enter command: ")
    if s == "q":
        return True
    else:
        gui.add_vehicle(Vehicle("Vehicle3", 100.0, 50.0), "blue")
        return False


if __name__ == "__main__":
    gui = Gui(canvas_width=800, canvas_height=400, base_scale_factor=.8e-4, zoom_factor=1.1, trace_length_max=100)
    gui.add_vehicle(Vehicle("Vehicle1", 300.0, 9.0), "black")
    gui.add_vehicle(Vehicle("Vehicle2", 200.0, 20.0), "red")
    gui.run(cb_main_loop=cb_main_loop)
