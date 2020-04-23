import numpy as np
import scipy.spatial
from entity.drone import Drone


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
        self.users = users
        self.drones = np.array([])
        self.drones_coordinates = np.array([])
        self.drones_history = np.array([])
        self.goals_history = np.array([])

    def simulation(self):
        # Генерация координат дронов согласно выбранной mobility для момента t0 (initial)
        self.drones = [Drone(0, 0, 0, d, self.params) for d in range(self.drones_number)]
        drones_coordinates = self.mobility.generate_new_positions(self.drones, self.users[0])
        [self.drones[d].set_position(x, y, z) for d, [x, y, z] in zip(range(self.drones_number), drones_coordinates)]
        self.drones_history = np.expand_dims(np.copy(drones_coordinates), axis=0)
        self.goals_history = np.expand_dims(np.copy(self.get_goals()), axis=0)
        # Симуляция дронов на каждом шаге и сохранение в историю
        for time_step in range(1, self.total_time_steps):

            # Case 1: Если текущий тайм слот совпадает с t_upd
            self.update_goals_in_t_upd_interval(time_step)

            # Case 2: Если все дроны прилетели туда, куда нужно было
            # self.update_goals_when_all_arrived(time_step)

            # Обновляем дронов + сохраняем их координаты в "историю"
            current_coordinates = self.update_drones()
            self.goals_history = np.concatenate((self.goals_history, np.expand_dims(self.get_goals(), axis=0)))
            self.drones_history = np.concatenate((self.drones_history, np.expand_dims(current_coordinates, axis=0)))
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
            new_coordinates = self.mobility.generate_new_positions(self.drones, self.users[time_step])
            self.update_drones_goals(new_coordinates)

    def update_goals_when_all_arrived(self, time_step):
        if sum([self.drones[d].get_state() for d in self.drones_number]) == self.drones_number:
            # определяем новые позиции дронов и обновляем цели дронов
            new_coordinates = self.mobility.generate_new_positions(self.drones, self.users[time_step])
            self.update_drones_goals(new_coordinates)

    def get_paths(self):
        return self.goals_history

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