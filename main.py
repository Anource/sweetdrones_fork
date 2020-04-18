import numpy as np
import scipy
import matplotlib.pyplot as plt
from entity.drone import Drone
from entity.antenna import Antenna
from entity.group import Group
from user_control import UserControl
from visualization_3d import Visualization


class SweetDrones:
    def __init__(self, delta_t, simulation_time, user_mobility):
        self.a = 1
        self.simulation_time = simulation_time
        self.delta_t = delta_t
        self.total_time_steps = int(simulation_time / delta_t)
        self.users = np.array([])
        self.drones = np.array([])
        self.user_mobility = user_mobility

    def generate_users(self):
        return UserControl(self.user_mobility).simulation()

    def start(self):
        for time_step in range(self.total_time_steps):
            print(1)

    def visualize(self, save=True):
        visual = Visualization(self.users, self.drones)
        visual.start(save=save)

def main():
    simulation = SweetDrones(0.1, 100)
    simulation.start()
    # num = 600
    # users_x = np.random.uniform(0, 100, size=(num, 100))
    # users_y = np.random.uniform(0, 100, size=(num, 100))
    # users_z = np.random.uniform(0, 3, size=(num, 100))
    # users = np.dstack([users_x, users_y, users_z])
    # drones_x = np.random.uniform(0, 100, size=(num, 10))
    # drones_y = np.random.uniform(0, 100, size=(num, 10))
    # drones_z = np.random.uniform(20, 25, size=(num, 10))
    # drones = np.dstack([drones_x, drones_y, drones_z])
    # visual = Visualization(users, drones)
    # visual.start(save=True)


if __name__ == '__main__':
    main()
