from time import time
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Line3D
import matplotlib.animation as animation


class Visualization:
    def __init__(self, users, drones):
        # Исходные данные
        self.area_x = 100
        self.area_y = 100
        self.area_z = 30
        self.log = True
        self.users = users
        self.drones = drones
        self.groups = 5
        self.max_simulation_time = 60
        self.delta_t = 0.1

        # self.fig = plt.figure()
        # self.ax = self.fig.add_subplot(1, 1, 1, projection='3d')

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

        self.ax1.xaxis._axinfo['grid']['color'] = (0, 0, 0, 0.1)
        self.ax1.yaxis._axinfo['grid']['color'] = (0, 0, 0, 0.1)
        self.ax1.zaxis._axinfo['grid']['color'] = (0, 0, 0, 0.1)
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

        # Создаем объекты Line3D, в которые передаем координаты всего, что нужно отрисовать, в нулевой момент времени
        self.groups_leaders_line = []
        self.groups_line = []
        for g in range(self.groups):
            self.groups_leaders_line.append(Line3D(self.users[0, g, 0, 0], self.users[0, g, 0, 1], self.users[0, g, 0, 2], color=colors[g][0], linestyle='', marker='D'))
            self.groups_line.append(Line3D(self.users[0, g, 1:, 0], self.users[0, g, 1:, 1], self.users[0, g, 1:, 2], color=colors[g][1], linestyle='', marker='o'))
            self.ax1.add_line(self.groups_leaders_line[g])
            self.ax1.add_line(self.groups_line[g])

        # self.drones_line = Line3D(self.drones[0, :, 0], self.drones[0, :, 1], self.drones[0, :, 2], color='black', linestyle='', marker='o')
        # self.ax.add_line(self.users_line)
        # self.ax.add_line(self.drones_line)

        # Настраиваем параметры
        # self.ax.set_xlim([0, self.area_x])
        # self.ax.set_xlabel('X')
        # self.ax.set_ylim([0, self.area_y])
        # self.ax.set_ylabel('Y')
        # self.ax.set_zlim([0, self.area_z])
        # self.ax.set_zlabel('Z')
        # self.ax.set_title('3D Test')
        if self.log:
            print('[VISUAL] Visualization is ready')

    def user_update(self, number):
        self.users_line.set_data_3d(self.users[number, 0, :, 0], self.users[number, 0, :, 1], self.users[number, 0, :, 2])

    def groups_update(self, number):
        for g in range(self.groups):
            self.groups_leaders_line[g].set_data_3d(self.users[number, g, 0, 0], self.users[number, g, 0, 1], self.users[number, g, 0, 2])
            self.groups_line[g].set_data_3d(self.users[number, g, 1:, 0], self.users[number, g, 1:, 1], self.users[number, g, 1:, 2])

    def drone_update(self, number):
        self.drones_line.set_data_3d(self.drones[number, :, 0], self.drones[number, :, 1], self.drones[number, :, 2])

    def cycle_update(self, number):
        self.groups_update(number)
        self.ax1.set_title('Simulation time: {} seconds'.format(number / 10))
        # self.drone_update(number)

    def start(self, save=False):
        animate = animation.FuncAnimation(self.fig, self.cycle_update, 600, interval=100, blit=False)
        if save:
            print('[VISUAL] Saving animation..')
            start_time = time()
            name = 'video.mp4'
            animate.save(name, writer='ffmpeg', dpi=100, fps=10)
            print(f'[VISUAL] Animation saved as \'{name}\'. It took {round(time() - start_time, 1)} seconds.')
        if self.log:
            print('[VISUAL] Visualization started')
        plt.show()
