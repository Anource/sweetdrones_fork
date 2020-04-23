import numpy as np
import scipy.spatial


class Group:
    def __init__(self, r_max, users_in_group, other_parameters):
        self.r_max = r_max
        self.users_in_group = users_in_group
        self.users = np.array([])
        self.users_goals = np.array([])
        self.isMoving = False
        self.speed = other_parameters['users_speed']
        self.delta_t = other_parameters['delta_t']
        self.group_move_time = np.array([np.random.exponential(1)])
        self.group_move_time_history = np.copy(self.group_move_time)

    def generate(self, leader_coordinates):
        # Load leader coordinates
        leader_x, leader_y, leader_z = leader_coordinates

        # Generate radius and angle for each user (here, power of 2 in 'self.r_max ** 2' means normalization)
        radius = np.random.uniform(0, self.r_max ** 2, size=self.users_in_group)
        radius[0] = 0  # to generate first user in leader coordinates (leader itself)
        angle = np.random.uniform(0, 2 * np.pi, size=self.users_in_group)

        # Generate users in range of 'r_max' radius
        users_x = leader_x + np.sqrt(radius) * np.cos(angle)
        users_y = leader_y + np.sqrt(radius) * np.sin(angle)
        users_z = leader_z + np.zeros(len(radius))
        self.users = np.dstack([users_x, users_y, users_z])[0]  # Array of users [x, y, z]
        self.update_goals()
        return self.users

    def update_goals(self):
        leader_radius = self.group_move_time * self.speed
        leader_angle = np.random.uniform(0, 2 * np.pi)
        leader_goal_x = self.users[0, 0] + leader_radius * np.cos(leader_angle)
        leader_goal_y = self.users[0, 1] + leader_radius * np.sin(leader_angle)
        leader_goal_z = self.users[0, 2]

        users_radius = np.random.uniform(0, self.r_max, size=self.users_in_group)
        users_radius[0] = 0
        users_angle = np.random.uniform(0, 2 * np.pi, size=self.users_in_group)
        users_goal_x = leader_goal_x + users_radius * np.cos(users_angle)
        users_goal_y = leader_goal_y + users_radius * np.sin(users_angle)
        users_goal_z = leader_goal_z + np.zeros(len(users_radius))
        self.users_goals = np.dstack([users_goal_x, users_goal_y, users_goal_z])[0]

    # def move(self):
    #     c_theta = np.arctan2(self.users[0, 1] - self.users[:, 1], self.users[0, 0] - self.users[:, 0])
    #     gangles = np.random.uniform(0, 2 * np.pi, size=self.users_in_group)
    #     dist_from_leader = scipy.spatial.distance.cdist(np.expand_dims(users[groups[g][0]], axis=0), users[groups[g]])[0]
    #     distances_indexes = np.where(dist_from_leader > self.r_max)[0]  # ищем тех, кто ушел от лидера дальше чем надо
    #     gangles[distances_indexes] = c_theta[distances_indexes]
    #     delta_gx = frame_speed * np.cos(gangles)
    #     delta_gy = frame_speed * np.sin(gangles)
    #     delta_gz = np.zeros(len(delta_gy))  # Заглушка: вдруг потребуется менять высоту юзеров?
    #     users[groups[g][1:]] += np.dstack([delta_gx[1:], delta_gy[1:], delta_gz[1:]])[0]

    def update(self):
        # users shape: (num, 3), users_goals shape: (num, 3)
        alpha = np.arctan2(self.users_goals[:, 1] - self.users[:, 1], self.users_goals[:, 0] - self.users[:, 0])
        xy = np.sqrt((self.users_goals[:, 1] - self.users[:, 1]) ** 2 + (self.users_goals[:, 0] - self.users[:, 0]) ** 2)
        beta = np.arctan2(xy, self.users_goals[:, 2] - self.users[:, 2])
        users_dx = self.speed * self.delta_t * np.cos(alpha) * np.sin(beta)
        users_dy = self.speed * self.delta_t * np.sin(alpha) * np.sin(beta)
        users_dz = self.speed * self.delta_t * np.cos(beta)
        self.users += np.dstack([users_dx, users_dy, users_dz])[0]
        self.group_move_time -= self.delta_t


        if self.group_move_time <= 0:
            self.group_move_time = np.array([np.random.exponential(1 / np.mean(self.group_move_time_history))])
            self.group_move_time_history = np.concatenate((self.group_move_time_history, self.group_move_time))
            self.update_goals()


    def get_users(self):
        return self.users
