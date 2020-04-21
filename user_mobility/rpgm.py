import numpy as np
import scipy
from entity.group import Group

# Reference Point Group Mobility


class ReferencePointGroupMobility:
    def __init__(self, parameters):
        self.parameters = parameters
        self.area_x = parameters['area_x']
        self.area_y = parameters['area_y']
        self.users_number = parameters['users_number']
        # self.drones_radius = parameters['drones_radius']
        self.drones_radius = 20
        self.drones_number = parameters['drones_number']
        self.groups_number = parameters['groups_number']
        self.groups_limits = parameters['groups_limits']
        self.users_speed = parameters['users_speed']
        self.users_height = parameters['users_height']
        self.r_max_k = parameters['r_max_k']
        self.groups = []
        self.users = np.array([])

    def generate_users(self):
        r_max = self.r_max_k * self.drones_radius * (self.drones_number / self.groups_number)
        grid_size = int(np.ceil(np.sqrt(self.groups_number)))
        centers_x = [self.area_x / grid_size * (0.5 + i) for i in range(grid_size)]
        centers_y = [self.area_y / grid_size * (0.5 + i) for i in range(grid_size)]
        centers_z = self.users_height
        centers = []
        for ix in centers_x:
            for iy in centers_y:
                centers.append([ix, iy, centers_z])
        self.groups = []
        group_centers = []
        for group in range(self.groups_number):
            idx = np.random.randint(len(centers))
            group_centers.append(centers.pop(idx))
            self.groups.append(Group(r_max, self.groups_limits[group], self.parameters))
        self.users = np.expand_dims(self.groups[0].generate(group_centers[0]), axis=0)
        for g in range(1, self.groups_number):
            # gr_users = self.groups[g].generate(group_centers[g])
            self.users = np.concatenate((self.users, np.expand_dims(self.groups[g].generate(group_centers[g]), axis=0)))
        return self.users

    def update_simulation(self):

        for group in range(self.groups_number):
            self.groups[group].update()

        self.users = np.expand_dims(self.groups[0].get_users(), axis=0)
        for g in range(1, self.groups_number):
            self.users = np.concatenate((self.users, np.expand_dims(self.groups[g].get_users(), axis=0)))

        return self.users
