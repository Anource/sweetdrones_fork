import numpy as np
import time
from tkinter import Tk, Canvas, Label
from user_control import UserControl
from user_mobility.rpgm import ReferencePointGroupMobility
from drone_control import DroneControl
from drone_navigation.pso import PSO
from drone_navigation.k_means import KMeans
from visualization_3d import Visualization


# Initial data for simulation
simulation_params = {
    'area_x': 100,  # meters
    'area_y': 100,  # meters
    'max_simulation_time': 10,  # s
    'delta_t': 0.1,  # s
    'snr_threshold': 20,  # dB

    'average_runs': 100,

    # Initial data for users
    'users_number': 150,  # number
    'groups_number': 5,  # number
    'groups_limits': [50, 50, 50, 50, 50],  # array of numbers
    'users_speed': 2.4,  # m/s
    'users_height': 2,  # m
    'r_max_k': 1.,

    # Initial data for drones
    'drones_number': 3,  # number
    'drones_speed': [5, 5, 5, 5, 5],  # m/s
    'drone_t_upd': 3.0,  # seconds    # IF ZERO - DRONES UPDATE THEIR POSITION WHEN EVERY DRONE IS ON POSITION
    'drones_height': 20,  # m

    # Initial data for antenna
    'transmit_power': 24,  # dBm
    'transmission_bandwidth': 0.56 * 10 ** 9,  # Hz
    'carrier_frequency': 60 * 10 ** 9,  # Hz
    'receive_antenna_gain': 3,  # dBi
    'transmit_antenna_gain': 3,  # dBi
}


class DronesProject:
    def __init__(self, parameters):
        self.parameters = parameters
        self.simulation_time = parameters['max_simulation_time']
        self.delta_t = parameters['delta_t']
        self.drone_t_upd = parameters['drone_t_upd']
        self.total_time_steps = int(self.simulation_time / self.delta_t)
        self.users = np.array([])
        self.drones = np.array([])
        self.groups = np.array([])
        self.drones_paths = np.array([])
        self.drones_diagrams = np.array([])
        self.coverage = np.array([])
        self.coverage_pso = np.array([])
        self.coverage_kmeans = np.array([])
        self.coverage_twice_pso = np.array([])
        self.coverage_twice_kmeans = np.array([])
        self.user_mobility = ReferencePointGroupMobility

    def start(self, pso, kmeans):
        user_control = UserControl(self.user_mobility, self.parameters)
        self.users = user_control.simulation()
        self.groups = user_control.get_groups()

        if pso:
            drone_control = DroneControl(PSO, self.users, self.parameters)
            self.drones = drone_control.simulation()
            self.drones_paths = drone_control.get_paths()
            self.drones_diagrams = np.array([])
            self.coverage_pso = drone_control.get_coverage()
            self.coverage_twice_pso = drone_control.get_twice_coverage()
            self.coverage = np.copy(self.coverage_pso)
        if kmeans:
            drone_control = DroneControl(KMeans, self.users, self.parameters)
            self.drones = drone_control.simulation()
            self.drones_paths = drone_control.get_paths()
            self.drones_diagrams = drone_control.get_diagrams()
            self.coverage_kmeans = drone_control.get_coverage()
            self.coverage_twice_kmeans = drone_control.get_twice_coverage()
            self.coverage = np.copy(self.coverage_kmeans)

    def get_coverage(self):
        return self.coverage_pso, self.coverage_kmeans

    def get_twice_coverage(self):
        return self.coverage_twice_pso, self.coverage_twice_kmeans

    def visualize(self, save=True):
        visual = Visualization(
            users=self.users,
            drones=self.drones,
            groups=self.groups,
            drones_paths=self.drones_paths,
            drones_diagrams=self.drones_diagrams,
            coverage=self.coverage,
            parameters=self.parameters
        )
        visual.start(save=save)


def main():
    pso = True
    kmeans = False
    # visual = True if pso ^ kmeans else False
    simulation = DronesProject(simulation_params)
    simulation.start(pso=pso, kmeans=kmeans)
    return simulation.users
    # if visual:
    #     simulation.visualize(save=True)


from drone_navigation.pso import PSO
from entity.antenna import Antenna

antenna = Antenna(simulation_params)

# Program start time
start_time = time.time()

max_x = simulation_params['area_x']
max_y = simulation_params['area_y']
users_num = simulation_params['users_number']
users_height = simulation_params['users_height']
snr_threshold = simulation_params['snr_threshold']
drones_height = simulation_params['drones_height']
drones_number = simulation_params['drones_number']


users_x = np.random.uniform(0, max_x, size=users_num)  # Array of users x's
users_y = np.random.uniform(0, max_y, size=users_num)  # Array of users y's
users_z = np.ones(users_num) * users_height  # Array of users y's
users_positions = np.dstack([users_x, users_y, users_z])[0]
# users_positions = main()[0]
# Duration of first movement
users_move_time = np.array([np.random.exponential(1)])

# Time parameters
simulation_time = 0.
max_simulation_time = 60.

# Time (in seconds) per one life cycle step
delta_t = 0.1

# User positions history (to visualize)
users_positions_history = np.expand_dims(users_positions, axis=0)

drones = np.array([
    [30., 28.],
    [30., 72.],
    [70., 50.]
])
drones_positions_history = np.expand_dims(drones, axis=0)
# drones_radius = 20




# Program parameters
window_width = 600
window_height = 600
window_name = "PSO demonstration"

# Program initialization
root = Tk()
root.title(window_name)
root.geometry('{}x{}'.format(window_width, window_height + 30))
label = Label(text="Simulation time: {}s".format(0), fg="black", font=("Helvetica", 18))
label.pack()
c = Canvas(root, width=window_width, height=window_height, background="#ffffff")
c.pack()
# End of initialization


# Simple functions to convert coordinates (visualization tool has different way to do it)
def scale_x(x):
    return x * window_width / max_x


def scale_y(y):
    return window_height - y * window_height / max_y


def place_user(x, y, color='black', d_size=5, *args, **kwargs):
    # d_size = 5
    return c.create_oval(x - d_size, y - d_size, x + d_size, y + d_size, fill=color, *args, **kwargs)


def place_drone(x, y, color='red', *args, **kwargs):
    d_size = 7
    return c.create_oval(x - d_size, y - d_size, x + d_size, y + d_size, fill=color, *args, **kwargs)


def place_drone_radius(x, y, r, color='#DDDDDD', *args, **kwargs):
    return c.create_oval(x - r, y - r, x + r, y + r, fill=color, *args, **kwargs)


started = False


# Для запуска симуляции по кнопке (для записи видео с экрана может быть полезно)
def starter(event):
    global started
    if not started:
        users_loop()
        started = True


def covered_users_by_single_drone(users, drone, radius):
    """
    Считаем количество покрытых пользователей ОДНИМ КОНКРЕТНЫМ дроном (используется в PSO,
    но если вам тоже нужно, юзайте)
    """
    # Count how many users are covered by one chosen drone (used mostly for PSO)
    users_lx = users[:, 0]
    users_ly = users[:, 1]
    drone_x, drone_y = drone
    return len(users[np.sqrt((users_lx - drone_x) ** 2 + (users_ly - drone_y) ** 2) <= radius])

label.configure(text="To start simulation press <Space>")

delta_t = 0.1
counter = 0
simulation_time = 0.

users_pso = np.copy(users_positions)
dists = [antenna.get_distance_on_snr(snr_threshold) for d in range(drones_number)]
drones_radius = np.sqrt(dists[0] ** 2 - (drones_height - users_height) ** 2)

particles_num = 100
w = 0.5
c1 = 0.5
c2 = 0.5
#
particles_x = np.random.uniform(0, max_x, size=particles_num)
particles_y = np.random.uniform(0, max_y, size=particles_num)
group_best = np.array([0, 0])
particle_best = np.dstack([particles_x, particles_y])[0]
u_curr = [covered_users_by_single_drone(users_positions, particle_best[l], drones_radius) for l in range(100)]
g_curr = covered_users_by_single_drone(users_positions, group_best, drones_radius)
if np.max(u_curr) > g_curr:
    group_best = particle_best[np.argmax(u_curr)]
particles_velocity_x = np.random.uniform(-max_x, max_x, size=particles_num)
particles_velocity_y = np.random.uniform(-max_y, max_y, size=particles_num)

cdrone = 0
drones_best = []


def users_loop():
    global users_positions, users_pso, particles_x, particles_y, particles_velocity_x, particles_velocity_y, group_best, particle_best, \
        counter, simulation_time, drones_radius, cdrone
    start_frame_time = time.time()
    # Удаляем все объекты
    c.delete('all')
    if counter == 0:
        particles_x = np.random.uniform(0, max_x, size=particles_num)
        particles_y = np.random.uniform(0, max_y, size=particles_num)
        group_best = np.array([0, 0])
        particle_best = np.dstack([particles_x, particles_y])[0]
        u_curr = [covered_users_by_single_drone(users_pso, particle_best[l], drones_radius) for l in range(100)]
        g_curr = covered_users_by_single_drone(users_pso, group_best, drones_radius)
        if np.max(u_curr) > g_curr:
            group_best = particle_best[np.argmax(u_curr)]
        particles_velocity_x = np.random.uniform(-max_x, max_x, size=particles_num)
        particles_velocity_y = np.random.uniform(-max_y, max_y, size=particles_num)
    for cd in range(len(drones_best)):
        place_drone_radius(scale_x(drones_best[cd][0]), scale_y(drones_best[cd][1]), scale_x(drones_radius))
    [place_user(scale_x(x), scale_y(y)) for x, y, _ in users_positions]

    r_p = np.random.uniform(0, 1, size=particles_num)
    r_g = np.random.uniform(0, 1, size=particles_num)

    particles_velocity_x = w * particles_velocity_x + c1 * r_p * (particle_best[:, 0] - particles_x) + c2 * r_g * (
            group_best[0] - particles_x)
    particles_velocity_y = w * particles_velocity_y + c1 * r_p * (particle_best[:, 1] - particles_y) + c2 * r_g * (
            group_best[1] - particles_y)
    particles_x += particles_velocity_x
    particles_y += particles_velocity_y

    u_curr = [covered_users_by_single_drone(users_pso, np.dstack([particles_x, particles_y])[0][l], drones_radius) for l in
              range(100)]
    p_u_curr = [covered_users_by_single_drone(users_pso, particle_best[l], drones_radius) for l in range(100)]
    particle_best[u_curr > p_u_curr] = np.dstack([particles_x, particles_y])[0]
    g_curr = covered_users_by_single_drone(users_pso, group_best, drones_radius)
    if np.max(p_u_curr) > g_curr:
        group_best = particle_best[np.argmax(p_u_curr)]

    for i in range(len(particles_x)):
        place_user(scale_x(particles_x[i]), scale_y(particles_y[i]), d_size=3, color='green')

    for cd in range(len(drones_best)):
        place_drone(scale_x(drones_best[cd][0]), scale_y(drones_best[cd][1]))
    frame_time = time.time() - start_frame_time
    label.configure(text="PSO iterations for {} drone: {}".format(cdrone + 1, counter))
    simulation_time += 0.1
    if counter < 30:
        counter += 1
        root.after(100 - int(np.round(frame_time * 1000)), lambda: users_loop())
    else:
        cdrone += 1
        counter = 0
        users_pso = users_pso[np.where(np.sqrt((users_pso[:, 0] - group_best[0]) ** 2 + (users_pso[:, 1] - group_best[1]) ** 2) >= drones_radius)[0]]
        if cdrone < drones_number:
            place_drone_radius(scale_x(group_best[0]), scale_y(group_best[1]), scale_x(drones_radius))
            [place_user(scale_x(x), scale_y(y)) for x, y, _ in users_positions]
            place_drone(scale_x(group_best[0]), scale_y(group_best[1]))
            root.after(100 - int(np.round(frame_time * 1000)), lambda: users_loop())

        label.configure(text="PSO iteration stopped after placing {} drones".format(cdrone))
        c.delete('all')
        drones_best.append([group_best[0], group_best[1]])
        for cd in range(len(drones_best)):
            place_drone_radius(scale_x(drones_best[cd][0]), scale_y(drones_best[cd][1]), scale_x(drones_radius))
        [place_user(scale_x(x), scale_y(y)) for x, y, _ in users_positions]
        for cd in range(len(drones_best)):
            place_drone(scale_x(drones_best[cd][0]), scale_y(drones_best[cd][1]))


root.bind("<space>", starter)
root.mainloop()
