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

        # Создаем объекты Line3D, в которые передаем координаты всего, что нужно отрисовать, в нулевой момент времени
        self.users_line = Line3D(self.users[0, :, 0], self.users[0, :, 1], self.users[0, :, 2], color='red', linestyle='', marker='o')
        self.drones_line = Line3D(self.drones[0, :, 0], self.drones[0, :, 1], self.drones[0, :, 2], color='black', linestyle='', marker='o')
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(1, 1, 1, projection='3d')
        self.ax.add_line(self.users_line)
        self.ax.add_line(self.drones_line)

        # Настраиваем параметры
        self.ax.set_xlim([0, self.area_x])
        self.ax.set_xlabel('X')
        self.ax.set_ylim([0, self.area_y])
        self.ax.set_ylabel('Y')
        self.ax.set_zlim([0, self.area_z])
        self.ax.set_zlabel('Z')
        self.ax.set_title('3D Test')
        if self.log:
            print('[VISUAL] Visualization is ready')

    def user_update(self, number):
        self.users_line.set_data_3d(self.users[number, :, 0], self.users[number, :, 1], self.users[number, :, 2])

    def drone_update(self, number):
        self.drones_line.set_data_3d(self.drones[number, :, 0], self.drones[number, :, 1], self.drones[number, :, 2])

    def cycle_update(self, number):
        self.user_update(number)
        self.drone_update(number)

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
