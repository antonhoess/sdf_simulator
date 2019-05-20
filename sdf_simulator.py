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
    print(np.version.version)
    gui = Gui(canvas_width=800, canvas_height=400, base_scale_factor=.8e-4, zoom_factor=1.1, trace_length_max=100,
              meas_buf_max=10)

    # Add vehicles
    vehicle1 = Vehicle("Vehicle1", True, 300.0, 9.0)
    gui.add_vehicle(vehicle1, color="black")
    vehicle2 = Vehicle("Vehicle2", False, 200.0, 20.0)
    gui.add_vehicle(vehicle2, color="red")

    # Add radars
    radar = Radar("R1", False, 3000, 8000, 5.,
                   cov_r=np.asarray([[100000, 80000],
                                     [80000, 100000]]),
                   cov_rd=np.asarray([[10000, 0],
                                      [0, 10000]]),
                   cov_rdd=np.asarray([[1000, 0],
                                       [0, 10000]]))
    gui.add_sensor(radar, fill="orange", outline="white", radius=3500, n_sides=3, rot_offset=math.pi, font_size_scale=1.2)

    radar = Radar("R2", False, -9000, -5000, 5.,
                   cov_r=np.asarray([[100000, 30000],
                                     [30000, 100000]]),
                   cov_rd=np.asarray([[10000, 0],
                                      [0, 10000]]),
                   cov_rdd=np.asarray([[1000, 0],
                                       [0, 10000]]))
    gui.add_sensor(radar, fill="lightblue", outline="black", radius=2500, n_sides=4, rot_offset=math.pi/4, font_size_scale=1.0)

    sigma_r = 5.e1
    sigma_rd = 1.e0
    sigma_rdd = 1.e-2
    radar_positions = [{"r_x": 0, "r_y": 0},
                       {"r_x": 10000, "r_y": -3000},
                       {"r_x": 5000, "r_y": 5000},
                       {"r_x": -8000, "r_y": 6000},
                       {"r_x": -7000, "r_y": -10000},
                       {"r_x": -12000, "r_y": -2000}]

    for i in range(len(radar_positions)):
        radar = Radar("R3 KF Test #{:03d}".format(i), True, radar_positions[i]["r_x"], radar_positions[i]["r_y"], 5.,
                      cov_r=np.identity(2) * sigma_r**2,
                      cov_rd=np.identity(2) * sigma_rd**2,
                      cov_rdd=np.identity(2) * sigma_rdd**2)
        gui.add_sensor(radar, fill="violet", outline="black", radius=1000, n_sides=5, rot_offset=math.pi/5, font_size_scale=0.1)
    # end for

    gui.run(cb_main_loop=cb_main_loop)
