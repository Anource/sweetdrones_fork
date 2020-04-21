import numpy as np
import scipy
from entity.group import Group


class UserControl:
    def __init__(self, mobility, user_params):
        self.mobility = mobility(user_params)
        self.user_params = user_params
        self.users_number = user_params['users_number']
        self.groups_number = user_params['groups_number']
        self.users_speed = user_params['users_speed']
        self.users_height = user_params['users_height']
        self.r_max_k = user_params['r_max_k']
        self.total_time_steps = int(user_params['max_simulation_time'] / user_params['delta_t'])
        self.users = np.array([])
        self.users_history = np.array([])

    def initialization(self):
        self.users = self.mobility.generate_users()
        self.users_history = np.copy(self.users)

    def simulation(self):
        self.users_history = np.expand_dims(self.users_history, axis=0)
        # Симуляция пользователей на каждом шаге
        # Тут же разворот пользователей при переходе границы
        # Управляем каждой группой

        for time_step in range(1, self.total_time_steps):
            self.users = self.mobility.update_simulation()

            # mask_x_l = users[:, 0] <= 0
            # mask_x_h = users[:, 0] >= self.area_x
            # mask_y_l = users[:, 1] <= 0
            # mask_y_h = users[:, 1] >= self.area_y
            #
            # # Turn leaving users back into area
            # users[:, 0][mask_x_l] = - users[:, 0][mask_x_l]
            # users[:, 0][mask_x_h] = 2 * self.area_x - users[:, 0][mask_x_h]
            # users[:, 1][mask_y_l] = - users[:, 1][mask_y_l]
            # users[:, 1][mask_y_h] = 2 * self.area_y - users[:, 1][mask_y_h]
            #
            # users_angles[mask_x_l + mask_x_h] = np.pi - users_angles[mask_x_l + mask_x_h]
            # users_angles[mask_y_l + mask_y_h] = - users_angles[mask_y_l + mask_y_h]

            self.users_history = np.concatenate((self.users_history, np.expand_dims(self.users, axis=0)))

        # Masks for boundaries. It will return those users who are trying to escape the area

        return self.users_history
