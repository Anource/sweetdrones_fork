import numpy as np
from user_control import UserControl
from user_mobility.rpgm import ReferencePointGroupMobility
from drone_control import DroneControl
from drone_navigation.pso import PSO
from drone_navigation.k_means import KMeans
from visualization_3d import Visualization

# Initial data for simulation
simulation_params = {
    'area_x': 100,  # meters
    'area_y': 100,  # meters
    'max_simulation_time': 60,  # s
    'delta_t': 0.1,  # s
    'snr_threshold': 20,  # dB
    'drone_t_upd': 5.0,  # seconds

    # Initial data for users
    'users_number': 100,  # number
    'groups_number': 4,  # number
    'groups_limits': [8, 15, 25, 52],  # array of numbers
    'users_speed': 1.4,  # m/s
    'users_height': 2,  # m
    'r_max_k': 1.3,

    # Initial data for drones
    'drones_number': 3,  # number
    'drones_speed': [5, 5, 5],  # m/s
    'drones_height': 20,  # m

    # Initial data for antenna
    'transmit_power': 24,  # dBm
    'transmission_bandwidth': 0.56 * 10 ** 9,  # Hz
    'carrier_frequency': 60 * 10 ** 9,  # Hz
    'receive_antenna_gain': 3,  # dBi
    'transmit_antenna_gain': 3,  # dBi
}


class DronesProject:
    def __init__(self, parameters):
        self.parameters = parameters
        self.simulation_time = parameters['max_simulation_time']
        self.delta_t = parameters['delta_t']
        self.drone_t_upd = parameters['drone_t_upd']
        self.total_time_steps = int(self.simulation_time / self.delta_t)
        self.users = np.array([])
        self.drones = np.array([])
        self.groups = np.array([])
        self.drones_paths = np.array([])
        self.drones_diagrams = np.array([])
        self.coverage = np.array([])
        self.user_mobility = ReferencePointGroupMobility

    def start(self, pso, kmeans):
        user_control = UserControl(self.user_mobility, self.parameters)
        self.users = user_control.simulation()
        self.groups = user_control.get_groups()

        if pso:
            drone_control = DroneControl(PSO, self.users, self.parameters)
            self.drones = drone_control.simulation()
            self.drones_paths = drone_control.get_paths()
        if kmeans:
            drone_control = DroneControl(KMeans, self.users, self.parameters)
            self.drones = drone_control.simulation()
            self.drones_paths = drone_control.get_paths()
            self.drones_diagrams = drone_control.get_diagrams()
            self.coverage = drone_control.get_coverage()

    def visualize(self, save=True):
        visual = Visualization(
            users=self.users,
            drones=self.drones,
            groups=self.groups,
            drones_paths=self.drones_paths,
            drones_diagrams=self.drones_diagrams,
            coverage=self.coverage,
            parameters=self.parameters
        )
        visual.start(save=save)


def main():
    pso = False
    kmeans = True
    visual = True if pso ^ kmeans else False
    simulation = DronesProject(simulation_params)
    simulation.start(pso=pso, kmeans=kmeans)
    if visual:
        simulation.visualize(save=False)


if __name__ == '__main__':
    main()
