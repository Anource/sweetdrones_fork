import numpy as np
import scipy.spatial
from entity.drone import Drone
from entity.antenna import Antenna


class DroneControl:

    def __init__(self, drone_mobility, users, params):
        self.mobility = drone_mobility(params)
        self.params = params
        max_simulation_time = params['max_simulation_time']
        self.delta_t = params['delta_t']
        self.total_time_steps = int(max_simulation_time / self.delta_t)
        self.drone_t_upd = params['drone_t_upd']
        self.t_upd_in_time_steps = int(self.drone_t_upd / self.delta_t)
        self.drones_number = params['drones_number']
        self.default_antenna = Antenna(params)
        self.users = users
        self.drones = np.array([])
        self.drones_coordinates = np.array([])
        self.drones_history = np.array([])
        self.goals_history = np.array([])
        self.diagrams = np.array([])
        self.diagrams_history = np.array([])
        self.coverage = []
        self.coverage_twice = []

    def simulation(self):
        # Генерация координат дронов согласно выбранной mobility для момента t0 (initial)
        self.drones = [Drone(0, 0, 0, d, self.params) for d in range(self.drones_number)]
        drones_coordinates, self.diagrams = self.mobility.generate_new_positions(self.drones, self.users[0])
        [self.drones[d].set_position(x, y, z) for d, [x, y, z] in zip(range(self.drones_number), drones_coordinates)]
        self.drones_history = np.expand_dims(np.copy(drones_coordinates), axis=0)
        self.diagrams_history = np.expand_dims(np.copy(self.diagrams), axis=0)
        self.goals_history = np.expand_dims(np.copy(self.get_goals()), axis=0)
        self.coverage.append(self.coverage_probability(self.users[0], drones_coordinates))
        self.coverage_twice.append(self.count_for_twice_covering(self.users[0], drones_coordinates))
        # Симуляция дронов на каждом шаге и сохранение в историю
        for time_step in range(1, self.total_time_steps):

            if self.drone_t_upd != 0.:
                # Case 1: Если текущий тайм слот совпадает с t_upd
                self.update_goals_in_t_upd_interval(time_step)
            else:
                # Case 2: Если все дроны прилетели туда, куда нужно было
                self.update_goals_when_all_arrived(time_step)

            # Обновляем дронов + сохраняем их координаты в "историю"
            current_coordinates = self.update_drones()
            self.coverage.append(self.coverage_probability(self.users[time_step], current_coordinates))
            self.coverage_twice.append(self.count_for_twice_covering(self.users[time_step], current_coordinates))
            self.goals_history = np.concatenate((self.goals_history, np.expand_dims(self.get_goals(), axis=0)))
            self.drones_history = np.concatenate((self.drones_history, np.expand_dims(current_coordinates, axis=0)))
            self.diagrams_history = np.concatenate((self.diagrams_history, np.expand_dims(self.diagrams, axis=0)))

        return self.drones_history

    def update_drones(self):
        # Обновляем координаты дронов: у них есть цели, они летят к ним (либо стоят)
        [self.drones[d].update() for d in range(self.drones_number)]
        # Возвращаем массив координат дронов
        return np.array([self.drones[d].get_position() for d in range(self.drones_number)])

    def update_drones_goals(self, new_coordinates):
        old_coordinates = np.array([self.drones[d].get_position() for d in range(self.drones_number)])
        coordinates = self.resort(old_coordinates, new_coordinates)
        [self.drones[d].update_goal(x, y, z) for d, [x, y, z] in zip(range(self.drones_number), coordinates)]

    def get_goals(self):
        return np.array([self.drones[d].get_goal() for d in range(self.drones_number)])

    def update_goals_in_t_upd_interval(self, time_step):
        if not time_step % self.t_upd_in_time_steps:
            # определяем новые позиции дронов и обновляем цели дронов
            new_coordinates, self.diagrams = self.mobility.generate_new_positions(self.drones, self.users[time_step])
            self.update_drones_goals(new_coordinates)

    def update_goals_when_all_arrived(self, time_step):
        if sum([self.drones[d].get_state() for d in range(self.drones_number)]) == self.drones_number:
            # определяем новые позиции дронов и обновляем цели дронов
            new_coordinates = self.mobility.generate_new_positions(self.drones, self.users[time_step])
            self.update_drones_goals(new_coordinates)

    def get_paths(self):
        return self.goals_history

    def get_diagrams(self):
        return self.diagrams_history

    def get_coverage(self):
        return np.array(self.coverage)

    def get_twice_coverage(self):
        return np.array(self.coverage_twice)

    def coverage_probability(self, users, drones):
        """
        Считаем Coverage Probability для конкретного момента времени: подаем список пользователей
        и список дронов в момент времени t, t>0, на выходе имеем число подключенных юзеров
        """
        # Calculate distances between each user and nearest drone
        distance = scipy.spatial.distance.cdist(users, drones)
        min_distances = np.min(distance, axis=1)
        min_distances_indexes = np.argmin(distance, axis=1)
        common_snr = self.default_antenna.calculate_snr(min_distances)
        return len(users[common_snr > self.params['snr_threshold']]) / len(users) * 100

    def count_for_twice_covering(self, users, drones):
        # Calculate distances between each user and nearest drone
        distance = scipy.spatial.distance.cdist(users, drones)
        min_distances_1 = np.min(distance, axis=1)
        min_distances_indexes = np.argmin(distance, axis=1)

        distance_wo_min = np.array([np.delete(distance[i], min_distances_indexes[i]) for i in range(len(distance))])
        min_distances_2 = np.min(distance_wo_min, axis=1)

        # Calculate SNR based on distance and SNR threshold
        snr_closest_drone = self.default_antenna.calculate_snr(min_distances_1)
        snr_second_closest_drone = self.default_antenna.calculate_snr(min_distances_2)
        covered_users = len(users[snr_closest_drone > self.params['snr_threshold']])
        condition1 = snr_closest_drone > self.params['snr_threshold']
        condition2 = snr_second_closest_drone > self.params['snr_threshold']
        covered_twice_users = len(users[np.logical_and(condition1, condition2)])
        all_users = len(users)
        return covered_twice_users / all_users * 100
        # return (covered_users - covered_twice_users) / all_users * 100

    def minor_matrix(self, arr, i, j):
        return arr[np.array(list(range(i)) + list(range(i + 1, arr.shape[0])))[:, np.newaxis],
                   np.array(list(range(j)) + list(range(j + 1, arr.shape[1])))]

    def combinations(self, dists):
        if len(dists) == 3:
            comb = []
            for i in range(len(dists)):
                first = dists[0][i]
                minor = self.minor_matrix(dists, 0, i)
                comb.append([first, minor[0][0], minor[1][1]])
                comb.append([first, minor[0][1], minor[1][0]])
            return comb
        else:
            array = []
            for i in range(len(dists)):
                first = dists[0][i]
                minor = self.minor_matrix(dists, 0, i)
                rec_combinations = self.combinations(minor)
                new_arr = []
                for i in range(len(rec_combinations)):
                    temp = [first]
                    for j in range(len(rec_combinations[i])):
                        temp.append(rec_combinations[i][j])
                    new_arr.append(temp)

                for i in range(len(new_arr)):
                    array.append(new_arr[i])
            return array

    def resort(self, old_drones, new_drones):
        distances = scipy.spatial.distance.cdist(old_drones, new_drones)
        distance_combinations = self.combinations(distances)
        dists_norm = np.linalg.norm(distance_combinations, axis=1)
        idx = np.argmin(dists_norm)
        min_distances = distance_combinations[idx]
        order = []
        for i in range(len(distances)):
            order.append(np.where(distances[i] == min_distances[i])[0][0])
        return new_drones[order]