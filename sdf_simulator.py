from vehicle import Vehicle
from sensor import Radar
from gui import Gui
import numpy as np


def cb_main_loop():
    s = input("Enter command: ")
    if s == "q":
        return True
    else:
        gui.add_vehicle(Vehicle("Vehicle3", 100.0, 50.0), "blue")
        return False


if __name__ == "__main__":
    gui = Gui(canvas_width=800, canvas_height=400, base_scale_factor=.8e-4, zoom_factor=1.1, trace_length_max=100,
              meas_buf_max=10)

    # Add vehicles
    vehicle1 = Vehicle("Vehicle1", 300.0, 9.0)
    gui.add_vehicle(vehicle1, "black")
    vehicle2 = Vehicle("Vehicle2", 200.0, 20.0)
    #gui.add_vehicle(vehicle2, "red")

    # Add radars
    radar1 = Radar("R1", 3000, 8000, 5.,
                   cov_r=(np.asarray([[100000, 30000], [30000, 100000]])*1.).tolist(),
                   cov_rd=[[10000, 0], [0, 10000]],
                   cov_rdd=[[1000, 0], [0, 10000]])
    gui.add_sensor(radar1, "orange")

    radar2 = Radar("R2", -9000, -5000, 5.,
                   cov_r=[[100000, 30000], [30000, 100000]],
                   cov_rd=[[10000, 0], [0, 10000]],
                   cov_rdd=[[1000, 0], [0, 10000]])
    gui.add_sensor(radar2, "lightblue")

    gui.run(cb_main_loop=cb_main_loop)
