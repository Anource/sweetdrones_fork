import numpy as np


class UserControl:
    def __init__(self, mobility, user_params):
        self.mobility = mobility(user_params)
        self.user_params = user_params
        max_simulation_time = user_params['max_simulation_time']
        delta_t = user_params['delta_t']
        self.total_time_steps = int(max_simulation_time / delta_t)
        self.users = np.array([])
        self.users_history = np.array([])

    def simulation(self):
        """
        Первоначальные и промежуточные координаты контролирует класс конкретной
        user mobility; текущий класс предназначен для единой обертки и сохранения
        всех координат в массив нужного вида
        """
        # Генерация пользователей согласно выбранной user mobility
        self.users = self.mobility.generate_users()
        self.users_history = np.expand_dims(np.copy(self.users), axis=0)

        # Симуляция пользователей на каждом шаге
        for time_step in range(1, self.total_time_steps):
            self.users = self.mobility.update_simulation_step()
            self.users_history = np.concatenate((self.users_history, np.expand_dims(self.users, axis=0)))
        return self.users_history

    def get_groups(self):
        return self.mobility.get_groups()
