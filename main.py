import numpy as np
from user_control import UserControl
from drone_control import DroneControl
from drone_navigation.pso import PSO
from drone_navigation.k_means import KMeans
import matplotlib.pyplot as plt

# Initial data for simulation
simulation_params = {
    'area_x': 100,  # meters
    'area_y': 100,  # meters
    'max_simulation_time': 100,  # s
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


class DroneSimulator:
    def __init__(self, parameters):
        self.parameters = parameters
        self.simulation_time = parameters['max_simulation_time']
        self.delta_t = parameters['delta_t']
        self.drone_t_upd = parameters['drone_t_upd']
        self.total_time_steps = int(self.simulation_time / self.delta_t)
        self.users = np.array([])
        self.drones = np.array([])
        self.coverage_pso = np.array([])
        self.coverage_kmeans = np.array([])

    def start(self, pso, kmeans):
        user_control = UserControl(self.parameters)
        self.users = user_control.simulation()

        if pso:
            drone_control = DroneControl(PSO, self.users, self.parameters)
            self.drones = drone_control.simulation()
            self.coverage_pso = drone_control.get_coverage()
        if kmeans:
            drone_control = DroneControl(KMeans, self.users, self.parameters)
            self.drones = drone_control.simulation()
            self.coverage_kmeans = drone_control.get_coverage()

    def get_coverage(self):
        return self.coverage_pso, self.coverage_kmeans


def main():
    number_of_iterations = 100
    all_coverage_pso = []
    all_coverage_kmeans = []
    for iteration in range(number_of_iterations):
        simulation = DroneSimulator(simulation_params)
        simulation.start(pso=True, kmeans=True)
        coverage_pso, coverage_kmeans = simulation.get_coverage()
        all_coverage_pso.append(coverage_pso)
        all_coverage_kmeans.append(coverage_kmeans)

    all_coverage_pso = np.average(all_coverage_pso, axis=0)
    all_coverage_kmeans = np.average(all_coverage_kmeans, axis=0)

    sim_time = simulation_params['max_simulation_time']
    delta_t = simulation_params['delta_t']
    label_x = np.arange(int(sim_time / delta_t))
    plt.figure(dpi=150, figsize=(10, 5))
    plt.title(f'Coverage probability: average value in {number_of_iterations} simulations')
    plt.plot(label_x, all_coverage_pso, label='PSO')
    plt.plot(label_x, all_coverage_kmeans, label='K-Means')
    locs = plt.xticks()[0][1:-1]
    new_locs = [int(i * delta_t) for i in locs]
    plt.xticks(locs, new_locs)
    plt.ylim(18, 102)
    plt.xlabel('Modelling time, s')
    plt.ylabel('Coverage probability, %')
    plt.grid(alpha=0.6)
    plt.legend()
    plt.show()


if __name__ == '__main__':
    main()
