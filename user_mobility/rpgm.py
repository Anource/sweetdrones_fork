import numpy as np
import scipy.spatial


class ReferencePointGroupMobility:
    def __init__(self, parameters):
        self.parameters = parameters
        self.area_x = parameters['area_x']
        self.area_y = parameters['area_y']
        self.users_number = parameters['users_number']
        self.drones_radius = 20
        self.drones_number = parameters['drones_number']
        self.groups_number = parameters['groups_number']
        self.groups_limits = parameters['groups_limits']
        self.users_speed = parameters['users_speed']
        self.users_height = parameters['users_height']
        self.delta_t = parameters['delta_t']
        self.user_move_time = np.array([np.random.exponential(1)])
        self.user_move_time_history = np.copy(self.user_move_time)
        self.r_max_k = parameters['r_max_k']
        self.r_max = self.r_max_k * self.drones_radius * (self.drones_number / self.groups_number)
        self.group = []
        self.users = np.array([])
        self.users_goals = np.array([])

    def users_groups_distribution(self):
        """
        Сортировка индексов пользователей и групп
        Пример:
        20 пользователей, 3 группы, распределение по группам [4, 7, 9]
        На выходе будет массив из индексов-принадлежностей пользователей к группам
        [[0, 3, 6,  9]                          - 4 пользователя  в группе 0
         [1, 4, 7, 10, 12, 14, 16]              - 7 пользователей в группе 1
         [2, 5, 8, 11, 13, 15, 17, 18, 19]]     - 9 пользователей в группе 2

        """
        group = [[] for _ in range(self.groups_number)]
        # group = [[]] * self.groups_number
        group_index = 0
        group_limit_index = 0
        for i in range(self.users_number):
            group[group_index].append(i)
            if len(group[group_index]) == self.groups_limits[group_index]:
                group_limit_index += 1
            group_index += 1
            group_index = group_limit_index if group_index == self.groups_number else group_index
        self.group = group

    def generate_users(self):
        self.users_groups_distribution()
        grid_size = int(np.ceil(np.sqrt(self.groups_number)))
        centers_x = [self.area_x / grid_size * (0.5 + i) for i in range(grid_size)]
        centers_y = [self.area_y / grid_size * (0.5 + i) for i in range(grid_size)]
        centers_z = self.users_height
        centers = []
        for ix in centers_x:
            for iy in centers_y:
                centers.append([ix, iy, centers_z])

        users_x = np.zeros(self.users_number)
        users_y = np.zeros(self.users_number)
        users_z = np.ones(self.users_number) * self.users_height

        for g in range(self.groups_number):
            idx = np.random.randint(len(centers))
            group_center = centers.pop(idx)

            groups_x = group_center[0] + np.random.uniform(-self.r_max / 2, self.r_max / 2)
            groups_y = group_center[1] + np.random.uniform(-self.r_max / 2, self.r_max / 2)
            groups_z = group_center[2]

            radius = np.random.uniform(0, self.r_max ** 2, size=self.groups_limits[g])
            radius[0] = 0  # to generate first user in leader coordinates (leader itself)
            angle = np.random.uniform(0, 2 * np.pi, size=self.groups_limits[g])

            # Generate users in range of 'r_max' radius
            users_x[self.group[g]] = groups_x + np.sqrt(radius) * np.cos(angle)
            users_y[self.group[g]] = groups_y + np.sqrt(radius) * np.sin(angle)
            users_z[self.group[g]] = groups_z

        self.users = np.dstack([users_x, users_y, users_z])[0]  # Array of users [x, y, z]
        self.update_goals()
        return self.users

    def move(self):
        # users shape: (num, 3), users_goals shape: (num, 3)
        alpha = np.arctan2(self.users_goals[:, 1] - self.users[:, 1], self.users_goals[:, 0] - self.users[:, 0])
        xy = np.sqrt((self.users_goals[:, 1] - self.users[:, 1]) ** 2 + (self.users_goals[:, 0] - self.users[:, 0]) ** 2)
        beta = np.arctan2(xy, self.users_goals[:, 2] - self.users[:, 2])

        # если скорость всех пользователей едина
        speed = self.users_speed * self.delta_t

        # если скорость зависит от расстояния, которое нужно пройти
        # dists_to_move = [scipy.spatial.distance.cdist(self.users, self.users_goals)[i, i] for i in range(self.users_number)]
        # speed = np.array(dists_to_move) / self.user_move_time * self.delta_t

        users_dx = speed * np.cos(alpha) * np.sin(beta)
        users_dy = speed * np.sin(alpha) * np.sin(beta)
        users_dz = speed * np.cos(beta)
        self.users += np.dstack([users_dx, users_dy, users_dz])[0]
        self.user_move_time -= self.delta_t

    def update_goals(self):
        users_goal_x = np.zeros(self.users_number)
        users_goal_y = np.zeros(self.users_number)
        users_goal_z = np.zeros(self.users_number)
        for g in range(self.groups_number):
            # Дистанция, на которую может пройти лидер за новое время
            leader_radius = self.user_move_time * self.users_speed
            # leader_radius = self.r_max
            leader_angle = np.random.uniform(0, 2 * np.pi)

            # Определяем путь, который пройдет лидер
            leader_goal_delta_x = leader_radius * np.cos(leader_angle)
            leader_goal_delta_y = leader_radius * np.sin(leader_angle)
            leader_goal_delta_z = 0  # на будущее: изменение высоты (если потребуется)

            # Генерируем дополнительные векторы пользователей той же группы
            users_radius = np.random.uniform(0, leader_radius, size=self.groups_limits[g])
            users_angle = np.random.uniform(0, 2 * np.pi, size=self.groups_limits[g])

            # У лидера нет дополнительного пути
            users_radius[0] = 0

            # Цель юзеров: точка, в которую они будут сходиться
            # Текущие координаты + вектор движения лидера + их вектор движения
            goals_x = self.users[self.group[g], 0] + leader_goal_delta_x + users_radius * np.cos(users_angle)
            goals_y = self.users[self.group[g], 1] + leader_goal_delta_y + users_radius * np.sin(users_angle)
            goals_z = self.users[self.group[g], 2] + leader_goal_delta_z + np.zeros(len(users_radius))

            # Определяем координаты цели лидера и целей юзеров
            leader = np.dstack([goals_x[0], goals_y[0], goals_z[0]])[0]
            others = np.dstack([goals_x, goals_y, goals_z])[0]

            # Ищем расстояние между лидером и каждым юзером группы и отмечаем тех,
            # чья цель за пределами радиуса r_max (относительно лидера)
            dist_from_leader = scipy.spatial.distance.cdist(leader, others)[0]
            dist_idx = np.where(dist_from_leader > self.r_max)[0]

            # Определяем трехмерные полярные углы между целями юзеров и лидера
            c1_theta = np.arctan2(goals_y[0] - goals_y, goals_x[0] - goals_x)[dist_idx]
            xy = np.sqrt((goals_y[0] - goals_y) ** 2 + (goals_x[0] - goals_x) ** 2)
            c2_theta = np.arctan2(xy, goals_z[0] - goals_z)[dist_idx]

            # Перезаписываем цели тех, кто собирается уйти от лидера:
            # Если цель юзера вне радиуса r_max с центром на цели лидера,
            # то устанавливаем целью точку на границе r_max (подробнее в документации)
            goals_x[dist_idx] += (dist_from_leader[dist_idx] - self.r_max) * np.cos(c1_theta) * np.sin(c2_theta)
            goals_y[dist_idx] += (dist_from_leader[dist_idx] - self.r_max) * np.sin(c1_theta) * np.sin(c2_theta)
            goals_z[dist_idx] += (dist_from_leader[dist_idx] - self.r_max) * np.cos(c2_theta)

            users_goal_x[self.group[g]] = goals_x
            users_goal_y[self.group[g]] = goals_y
            users_goal_z[self.group[g]] = goals_z

        self.users_goals = np.dstack([users_goal_x, users_goal_y, users_goal_z])[0]

    def update_simulation_step(self):
        # Обновление шага всех пользователей
        self.move()

        if self.user_move_time <= 0:
            self.user_move_time = np.array([np.random.exponential(1 / np.mean(self.user_move_time_history))])
            self.user_move_time_history = np.concatenate((self.user_move_time_history, self.user_move_time))
            self.update_goals()

        # Masks for boundaries. It will return those users who are trying to escape the area
        mask_x_l = self.users[:, 0] <= 0
        mask_x_h = self.users[:, 0] >= self.area_x
        mask_y_l = self.users[:, 1] <= 0
        mask_y_h = self.users[:, 1] >= self.area_y

        # Turn leaving users back into area
        self.users[:, 0][mask_x_l] = - self.users[:, 0][mask_x_l]
        self.users[:, 0][mask_x_h] = 2 * self.area_x - self.users[:, 0][mask_x_h]
        self.users[:, 1][mask_y_l] = - self.users[:, 1][mask_y_l]
        self.users[:, 1][mask_y_h] = 2 * self.area_y - self.users[:, 1][mask_y_h]

        mask_x_l = self.users_goals[:, 0] <= 0
        mask_x_h = self.users_goals[:, 0] >= self.area_x
        mask_y_l = self.users_goals[:, 1] <= 0
        mask_y_h = self.users_goals[:, 1] >= self.area_y

        # Turn leaving users back into area
        self.users_goals[:, 0][mask_x_l] = - self.users_goals[:, 0][mask_x_l]
        self.users_goals[:, 0][mask_x_h] = 2 * self.area_x - self.users_goals[:, 0][mask_x_h]
        self.users_goals[:, 1][mask_y_l] = - self.users_goals[:, 1][mask_y_l]
        self.users_goals[:, 1][mask_y_h] = 2 * self.area_y - self.users_goals[:, 1][mask_y_h]
        return self.users

    def get_groups(self):
        return self.group
