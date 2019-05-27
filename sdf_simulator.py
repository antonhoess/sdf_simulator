from vehicle import Vehicle
from sensor import *
from sensor_group import HomogeneousTriggeredSensorGroup
from gui import Gui
import numpy as np
import math


def cb_main_loop():
    s = input("Enter command: ")
    if s == "q":
        return True
    else:
        gui.add_vehicle(Vehicle("Vehicle3", True, 100.0, 50.0), color="blue")
        return False


if __name__ == "__main__":
    gui = Gui(canvas_width=800, canvas_height=400, base_scale_factor=.8e-4, zoom_factor=1.1, trace_length_max=100,
              meas_buf_max=10)

    # Add vehicles
    # ------------
    vehicle1 = Vehicle("Vehicle1", True, 300.0, 9.0)
    gui.add_vehicle(vehicle1, color="black")
    vehicle2 = Vehicle("Vehicle2", False, 200.0, 20.0)
    gui.add_vehicle(vehicle2, color="red")

    # Add sensors
    # -----------
    # > Add sensor
    sensor = Plane("P1", False, np.asarray([3000, 8000]), cov_mat=np.asarray([[100000, 80000],
                                                                            [80000, 100000]]), meas_interval=3.0)

    gui.add_sensor(sensor, fill="orange", outline="white", radius=3500, n_sides=3, font_size_scale=0.8)

    # > Add sensor
    sensor = Plane("P2", False, np.asarray([-9000, -5000]), cov_mat=np.asarray([[100000, 30000],
                                                                              [30000, 100000]]), meas_interval=5.0)

    gui.add_sensor(sensor, fill="lightblue", outline="black", radius=2500, n_sides=4, font_size_scale=1.0)
    # gui.add_sensor_group(HomogeneousTriggeredSensorGroup("Group 2", radar, 5., cov_mat=None), fill="pink")

    # > Add sensors
    sigma_c = 5.e2  # m
    radar_positions = [{"r_x": 0, "r_y": 0},
                       {"r_x": 10000, "r_y": -3000},
                       {"r_x": 5000, "r_y": 5000},
                       {"r_x": -8000, "r_y": 6000},
                       {"r_x": -7000, "r_y": -10000},
                       {"r_x": -12000, "r_y": -2000}]

    sensors = []

    for i in range(len(radar_positions)):
        sensor = Plane("P3 KF #{:03d}".format(i), False, np.asarray([radar_positions[i]["r_x"], radar_positions[i]["r_y"]]), meas_interval=None, cov_mat=None)
        gui.add_sensor(sensor, fill="violet", outline="black", radius=1000, n_sides=5, rot_offset=math.pi / 5,
                       font_size_scale=0.5)
        sensors.append(sensor)
    # end for
    gui.add_sensor_group(HomogeneousTriggeredSensorGroup("Multi Group", sensors, meas_interval=5., cov_mat=np.identity(2) * sigma_c ** 2), fill="pink")

    # > Add sensor
    sensor = Radar("R1", True, np.asarray([4000, 7000]), cov_mat=np.asarray([[.001, 0],
                                                                            [0, .01]]), meas_interval=12.0)

    gui.add_sensor(sensor, fill="green", outline="white", radius=3500, n_sides=3, rot_offset=math.pi, font_size_scale=.7)

    gui.run(cb_main_loop=cb_main_loop)
