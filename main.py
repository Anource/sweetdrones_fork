import numpy as np
import scipy
import matplotlib.pyplot as plt
from entity.drone import Drone
from entity.antenna import Antenna
from entity.group import Group
from user_control import UserControl
from visualization_3d import Visualization
from user_mobility.rw import RandomWalk
from user_mobility.rdm import RandomDirectionMobility
from user_mobility.rpgm import ReferencePointGroupMobility


class SweetDrones:
    def __init__(self, user_mobility, parameters):
        self.parameters = parameters
        self.simulation_time = parameters['max_simulation_time']
        self.delta_t = parameters['delta_t']
        self.drone_t_upd = parameters['drone_t_upd']
        self.total_time_steps = int(self.simulation_time / self.delta_t)
        self.users = np.array([])
        self.drones = np.array([])
        self.user_mobility = user_mobility

    def start(self):
        control = UserControl(self.user_mobility, self.parameters)
        control.initialization()
        self.users = control.simulation()
        # self.users = UserControl(self.user_mobility, self.parameters).initialization()
        print(np.shape(self.users))
        # for time_step in range(self.total_time_steps):
        #     print(1)

    def visualize(self, save=True):
        visual = Visualization(self.users, self.drones)
        visual.start(save=save)


# Initial data for simulation
basic_parameters = {
    'area_x': 100,  # meters
    'area_y': 100,  # meters
    'max_simulation_time': 60,  # s
    'delta_t': 0.1,  # s
    'snr_threshold': 20,  # dB
    'drone_t_upd': 5.0,  # seconds

    # Initial data for users
    'users_number': 100,  # number
    'groups_number': 5,  # number
    'groups_limits': [20, 20, 20, 20, 20],  # array of numbers | SUM MUST BE EQUAL TO USERS NUMBER!!! LEN OF ARRAY MUST BE EQUAL TO GROUPS NUMBER!!!
    'users_speed': 1.4,  # m/s
    'users_height': 2,  # m
    'r_max_k': 1.3,

    # Initial data for drones
    'drones_number': 3,  # number
    'drones_speed': 5,  # m/s
    'drones_height': 20,  # m

    # Initial data for antenna
    'transmit_power': 24,  # dBm
    'transmission_bandwidth': 0.56 * 10 ** 9,  # Hz
    'carrier_frequency': 60 * 10 ** 9,  # Hz
    'receive_antenna_gain': 3,  # dBi
    'transmit_antenna_gain': 3,  # dBi
}


def main():
    simulation = SweetDrones(ReferencePointGroupMobility, basic_parameters)
    simulation.start()
    simulation.visualize(save=False)
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
