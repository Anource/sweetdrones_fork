import numpy as np
from entity.antenna import Antenna
import scipy


class Drone:
    def __init__(self, x, y, z, speed):
        self.x = x
        self.y = y
        self.z = z
        self.speed_per_tact = speed
        self.antenna = Antenna()
        self.isMoving = False
        self.goal_x = x
        self.goal_y = y
        self.goal_z = z

    def move(self, x, y, z):
        self.goal_x = x
        self.goal_y = y
        self.goal_z = z
        self.isMoving = True

    def update(self):
        # Если дрон должен двигаться - обновляем координаты
        if self.isMoving:
            alpha = np.arctan2(self.goal_y - self.y, self.goal_x - self.x)
            xy = np.sqrt((self.goal_y - self.y) ** 2 + (self.goal_x - self.x) ** 2)
            beta = np.arctan2(xy, self.goal_z - self.z)
            self.x += self.speed_per_tact * np.cos(alpha) * np.sin(beta)
            self.y += self.speed_per_tact * np.sin(alpha) * np.sin(beta)
            self.z += self.speed_per_tact * np.cos(beta)

            # Если дрон долетел - останавливаем его
            if np.fabs(self.goal_x - self.x) + np.fabs(self.goal_y - self.y) + np.fabs(self.goal_z - self.z) < 3 * self.speed_per_tact:
                self.isMoving = False
