import numpy as np
import scipy.spatial


class PSO:
    def __init__(self, params):
        self.params = params
        self.area_x = params['area_x']
        self.area_y = params['area_y']
        self.drones_number = params['drones_number']
        self.drones_height = params['drones_height']
        self.users_height = params['users_height']
        self.snr_threshold = params['snr_threshold']

    def generate_new_positions(self, drones, users):
        users_pso = np.copy(users)
        dists = [drones[d].get_antenna_distance(self.snr_threshold) for d in range(self.drones_number)]
        drones_radius = np.sqrt(dists[0]**2 - (self.drones_height - self.users_height)**2)
        drones_best = []
        for i in range(self.drones_number):
            particles_num = 100
            w = 0.5
            c1 = 0.5
            c2 = 0.5
            particles_x = np.random.uniform(0, self.area_x, size=particles_num)
            particles_y = np.random.uniform(0, self.area_y, size=particles_num)
            group_best = np.array([0, 0])
            particle_best = np.dstack([particles_x, particles_y])[0]
            u_curr = [self.covered_users_by_single_drone(users_pso, particle_best[l], drones_radius) for l in
                      range(100)]
            g_curr = self.covered_users_by_single_drone(users_pso, group_best, drones_radius)
            if np.max(u_curr) > g_curr:
                group_best = particle_best[np.argmax(u_curr)]
            particles_velocity_x = np.random.uniform(-self.area_x, self.area_x, size=particles_num)
            particles_velocity_y = np.random.uniform(-self.area_y, self.area_y, size=particles_num)
            for t in range(30):
                r_p = np.random.uniform(0, 1, size=particles_num)
                r_g = np.random.uniform(0, 1, size=particles_num)

                particles_velocity_x = w * particles_velocity_x + c1 * r_p * (
                        particle_best[:, 0] - particles_x) + c2 * r_g * (
                                               group_best[0] - particles_x)
                particles_velocity_y = w * particles_velocity_y + c1 * r_p * (
                        particle_best[:, 1] - particles_y) + c2 * r_g * (
                                               group_best[1] - particles_y)
                particles_x += particles_velocity_x
                particles_y += particles_velocity_y

                u_curr = [self.covered_users_by_single_drone(users_pso, np.dstack([particles_x, particles_y])[0][l],
                                                             drones_radius) for l in
                          range(100)]
                p_u_curr = [self.covered_users_by_single_drone(users_pso, particle_best[l], drones_radius) for l in
                            range(100)]
                particle_best[u_curr > p_u_curr] = np.dstack([particles_x, particles_y])[0]
                g_curr = self.covered_users_by_single_drone(users_pso, group_best, drones_radius)
                if np.max(p_u_curr) > g_curr:
                    group_best = particle_best[np.argmax(p_u_curr)]
            group_best = list(group_best)
            group_best.append(self.drones_height)
            group_best = np.array(group_best)
            drones_best.append(group_best)
            users_pso = users_pso[
                np.where(np.sqrt((users_pso[:, 0] - group_best[0]) ** 2 + (
                        users_pso[:, 1] - group_best[1]) ** 2) >= drones_radius)[0]]
        return np.array(drones_best), np.array([])

    def covered_users_by_single_drone(self, users, drone, radius):
        """
        Считаем количество покрытых пользователей ОДНИМ КОНКРЕТНЫМ дроном (используется в PSO,
        но если вам тоже нужно, юзайте)
        """
        # Count how many users are covered by one chosen drone (used mostly for PSO)
        users_lx = users[:, 0]
        users_ly = users[:, 1]
        drone_x, drone_y = drone
        return len(users[np.sqrt((users_lx - drone_x) ** 2 + (users_ly - drone_y) ** 2) <= radius])
