import numpy as np
from entity.antenna import Antenna
import scipy


class Drone:
    def __init__(self, x, y, z, id, params):
        self.x = x
        self.y = y
        self.z = z
        self.id = id
        self.speed_per_tact = params['drones_speed'][id] * params['delta_t']
        self.antenna = Antenna(params)
        self.isMoving = False
        self.goal_x = x
        self.goal_y = y
        self.goal_z = z

    def update_goal(self, x, y, z):
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

    def get_goal(self):
        return np.array([self.goal_x, self.goal_y, self.goal_z])

    def get_state(self):
        return self.isMoving

    def get_position(self):
        return np.array([self.x, self.y, self.z])

    def set_position(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
        self.goal_x = x
        self.goal_y = y
        self.goal_z = z

    def get_antenna_distance(self, snr_threshold):
        return self.antenna.get_distance_on_snr(snr_threshold)
