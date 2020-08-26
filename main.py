import numpy as np
from user_control import UserControl
from user_mobility.rpgm import ReferencePointGroupMobility
from drone_control import DroneControl
from drone_navigation.pso import PSO
from drone_navigation.k_means import KMeans
from visualization_3d import Visualization
import time


# Initial data for simulation
simulation_params = {
    'area_x': 200,  # meters
    'area_y': 200,  # meters
    'max_simulation_time': 10,  # s
    'delta_t': 0.001,  # s
    'snr_threshold': 20,  # dB

    'average_runs': 100,

    # Initial data for users
    'users_number': 250,  # number
    'groups_number': 5,  # number
    'groups_limits': [50, 50, 50, 50, 50],  # array of numbers
    'users_speed': 1.4,  # m/s
    'users_height': 2,  # m
    'r_max_k': 1.,

    # Initial data for drones
    'drones_number': 5,  # number
    'drones_speed': [5, 5, 5, 5, 5],  # m/s
    'drone_t_upd': 0.01,  # seconds    # IF ZERO - DRONES UPDATE THEIR POSITION WHEN EVERY DRONE IS ON POSITION
    'drones_height': 40,  # m

    # Initial data for antenna
    'transmit_power': 24,  # dBm
    'transmission_bandwidth': 1. * 10 ** 9,  # Hz
    'carrier_frequency': 28 * 10 ** 9,  # Hz
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
        self.coverage_pso = np.array([])
        self.coverage_kmeans = np.array([])
        self.coverage_twice_pso = np.array([])
        self.coverage_twice_kmeans = np.array([])
        self.user_mobility = ReferencePointGroupMobility

    def start(self, pso, kmeans):
        gitime = time.time()
        user_control = UserControl(self.user_mobility, self.parameters)
        self.users = user_control.simulation()
        self.groups = user_control.get_groups()
        print("Time of users:", time.time() - gitime)
        if pso:
            gptime = time.time()
            drone_control = DroneControl(PSO, self.users, self.parameters)
            self.drones = drone_control.simulation()
            self.drones_paths = drone_control.get_paths()
            self.drones_diagrams = np.array([])
            self.coverage_pso = drone_control.get_coverage()
            self.coverage_twice_pso = drone_control.get_twice_coverage()
            self.coverage = np.copy(self.coverage_pso)
            print("Time of pso:", time.time() - gptime)
        if kmeans:
            gktime = time.time()
            drone_control = DroneControl(KMeans, self.users, self.parameters)
            self.drones = drone_control.simulation()
            self.drones_paths = drone_control.get_paths()
            self.drones_diagrams = drone_control.get_diagrams()
            self.coverage_kmeans = drone_control.get_coverage()
            self.coverage_twice_kmeans = drone_control.get_twice_coverage()
            self.coverage = np.copy(self.coverage_kmeans)
            print("Time of km:", time.time() - gktime)

    def get_coverage(self):
        return self.coverage_pso, self.coverage_kmeans

    def get_twice_coverage(self):
        return self.coverage_twice_pso, self.coverage_twice_kmeans

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
        simulation.visualize(save=True)


if __name__ == '__main__':
    main()


