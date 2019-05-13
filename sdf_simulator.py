from vehicle import Vehicle
from sensor import Radar
from gui import Gui
import numpy as np
import math


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
    vehicle1 = Vehicle("Vehicle1", True, 300.0, 9.0)
    gui.add_vehicle(vehicle1, color="black")
    vehicle2 = Vehicle("Vehicle2", False, 200.0, 20.0)
    gui.add_vehicle(vehicle2, color="red")

    # Add radars
    radar1 = Radar("R1", True, 3000, 8000, 5.,
                   cov_r=(np.asarray([[100000, 80000], [80000, 100000]])*1.).tolist(),
                   cov_rd=[[10000, 0], [0, 10000]],
                   cov_rdd=[[1000, 0], [0, 10000]])
    gui.add_sensor(radar1, fill="orange", outline="white", radius=3500, n_sides=3, rot_offset=math.pi, font_size_scale=1.2)

    radar2 = Radar("R2", True, -9000, -5000, 5.,
                   cov_r=[[100000, 30000], [30000, 100000]],
                   cov_rd=[[10000, 0], [0, 10000]],
                   cov_rdd=[[1000, 0], [0, 10000]])
    gui.add_sensor(radar2, fill="lightblue", outline="black", radius=2500, n_sides=4, rot_offset=math.pi/4, font_size_scale=1.0)

    gui.run(cb_main_loop=cb_main_loop)
