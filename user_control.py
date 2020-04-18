import numpy as np
import scipy


class UserControl:
    def __init__(self, mobility):
        self.mobility = mobility

    def initialization(self):
        # Инициализация пользователей, групп, ...
        return self.mobility

    def simulation(self):
        # Симуляция пользователей на каждом шаге
        # Тут же разворот пользователей при переходе границы
        #
        return self.mobility
