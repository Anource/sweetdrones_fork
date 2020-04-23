from time import time
import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d.art3d import Line3D
import matplotlib.animation as animation
from log import print_log


class Visualization:
    def __init__(self, users, drones, groups, drones_paths, additional_lines, parameters):
        # Исходные данные
        self.area_x = parameters['area_x']
        self.area_y = parameters['area_y']
        self.area_z = 30
        self.users = users
        self.drones = drones
        self.drones_paths = drones_paths
        self.additional_lines = additional_lines
        max_simulation_time = parameters['max_simulation_time']
        delta_t = parameters['delta_t']
        self.total_time_steps = int(max_simulation_time / delta_t)
        self.groups_number = parameters['groups_number']
        self.drones_number = parameters['drones_number']
        self.max_simulation_time = parameters['max_simulation_time']
        self.delta_t = parameters['delta_t']

        gridsize = (5, 2)
        self.fig = plt.figure(dpi=100, figsize=(10, 7))
        self.ax1 = plt.subplot2grid(gridsize, (0, 0), projection='3d', colspan=2, rowspan=3)
        self.ax2 = plt.subplot2grid(gridsize, (3, 0), colspan=1, rowspan=2)
        self.ax3 = plt.subplot2grid(gridsize, (3, 1), colspan=1, rowspan=2)
        self.ax1.set_xlim(0, 100)
        self.ax1.set_ylim(0, 100)
        self.ax1.set_zlim(0, 30)

        self.ax1.xaxis.set_pane_color((0, 0, 0, 0.01))
        self.ax1.yaxis.set_pane_color((0, 0, 0, 0.01))
        self.ax1.zaxis.set_pane_color((0, 0, 0, 0.01))

        self.ax1.set_zticks([0, 10, 20, 30, 40])

        self.ax1.set_xlabel("x, m")
        self.ax1.set_ylabel("y, m")
        self.ax1.set_zlabel("H, m")

        self.ax2.set_xlabel("Modelling time, s")
        self.ax2.set_ylabel("Coverage probability, %")
        self.ax2.set_xlim(-self.max_simulation_time * 0.05, self.max_simulation_time + self.max_simulation_time * 0.05)
        self.ax2.set_ylim(-8, 108)
        self.ax2.grid(alpha=0.3)

        self.ax3.set_xlabel("Modelling time, s")
        self.ax3.set_ylabel("Coverage probability, %")
        self.ax3.grid(alpha=0.3)
        colors = [
            ['#0026FF', '#7C96FF'],  # Color 1 in picture
            ['#FF2100', '#FF7E75'],  # Color 2 in picture
            ['#009E56', '#00E57E'],  # Color 3 in picture
            ['#57007F', '#8D00CE'],  # Color 4 in picture
            ['#FF6A00', '#FFAA10'],  # Color 5 in picture
            ['#0af5f5', '#4cfcfc'],  # Color 6 in picture
            ['#71c78a', '#b5ffca']   # Color 7 in picture
        ]
        self.group = groups
        # Создаем объекты Line3D, в которые передаем координаты всего, что нужно отрисовать, в нулевой момент времени
        self.groups_leaders_line = []
        self.groups_line = []
        self.groups_circle = []
        self.drones_line = []
        self.drones_radius_circle = []
        self.drones_path_line = []
        self.drones_additional_line = []
        self.rad = np.sqrt(26.648092476442518**2 - 18**2)
        self.r_angles = np.linspace(0, 2 * np.pi, 30)
        for g in range(self.groups_number):
            self.groups_leaders_line.append(Line3D(self.users[0, self.group[g][0], 0], self.users[0, self.group[g][0], 1], self.users[0, self.group[g][0], 2], color=colors[g][0], linestyle='', marker='D'))
            self.groups_line.append(Line3D(self.users[0, self.group[g][1:], 0], self.users[0, self.group[g][:1], 1], self.users[0, self.group[g][1:], 2], color=colors[g][1], linestyle='', marker='o'))

            # self.groups_circle.append(Line3D(self.users[0, self.group[g][0], 0] + self.r_max * np.cos(self.r_angles),
            #                                  self.users[0, self.group[g][0], 1] + self.r_max * np.sin(self.r_angles),
            #                                  self.users[0, self.group[g][0], 2] + np.zeros(30),
            #                                  color=colors[g][1], linestyle='-', lw=0.5))
            self.ax1.add_line(self.groups_leaders_line[g])
            self.ax1.add_line(self.groups_line[g])
            # self.ax1.add_line(self.groups_circle[g])
        for d in range(self.drones_number):
            self.drones_line.append(Line3D(self.drones[0, d, 0], self.drones[0, d, 1], self.drones[0, d, 2], color='black', linestyle='', marker='o'))
            self.drones_radius_circle.append(Line3D(self.drones[0, d, 0] + self.rad * np.cos(self.r_angles),
                                                    self.drones[0, d, 1] + self.rad * np.sin(self.r_angles),
                                                    2, color='black', lw=0.5))

            self.drones_path_line.append(Line3D([self.drones[0, d, 0], self.drones_paths[0, d, 0]],
                                                [self.drones[0, d, 1], self.drones_paths[0, d, 1]],
                                                [self.drones[0, d, 2], self.drones_paths[0, d, 2]],
                                                color='black', linestyle='--', lw=0.7))
        #     self.drones_additional_line.append()

            self.ax1.add_line(self.drones_line[d])
            self.ax1.add_line(self.drones_radius_circle[d])
            self.ax1.add_line(self.drones_path_line[d])

    def user_update(self, number):
        self.users_line.set_data_3d(self.users[number, 0, :, 0], self.users[number, 0, :, 1], self.users[number, 0, :, 2])

    def groups_update(self, number):
        for g in range(self.groups_number):
            self.groups_leaders_line[g].set_data_3d(self.users[number, self.group[g][0], 0], self.users[number, self.group[g][0], 1], self.users[number, self.group[g][0], 2])
            self.groups_line[g].set_data_3d(self.users[number, self.group[g][1:], 0], self.users[number, self.group[g][1:], 1], self.users[number, self.group[g][1:], 2])

    def drone_update(self, number):
        for d in range(self.drones_number):
            self.drones_line[d].set_data_3d(self.drones[number, d, 0], self.drones[number, d, 1], self.drones[number, d, 2])
            self.drones_radius_circle[d].set_data_3d(self.drones[number, d, 0] + self.rad * np.cos(self.r_angles),
                                                     self.drones[number, d, 1] + self.rad * np.sin(self.r_angles), 2)
            self.drones_path_line[d].set_data_3d([self.drones[number, d, 0], self.drones_paths[number, d, 0]],
                                                [self.drones[number, d, 1], self.drones_paths[number, d, 1]],
                                                [self.drones[number, d, 2], self.drones_paths[number, d, 2]])

    def cycle_update(self, number):
        self.groups_update(number)
        self.ax1.set_title('Simulation time: {} seconds'.format(number / 10))
        self.drone_update(number)

    def start(self, save=False):
        animate = animation.FuncAnimation(self.fig, self.cycle_update, self.total_time_steps, interval=100, blit=False)
        if save:
            name = 'video.mp4'
            animate.save(name, writer='ffmpeg', dpi=100, fps=10)
        plt.show()
