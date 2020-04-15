import numpy as np
import scipy
import matplotlib.pyplot as plt
from visualization_3d import Visualization


def main():
    num = 600
    users_x = np.random.uniform(0, 100, size=(num, 100))
    users_y = np.random.uniform(0, 100, size=(num, 100))
    users_z = np.random.uniform(0, 3, size=(num, 100))
    users = np.dstack([users_x, users_y, users_z])
    drones_x = np.random.uniform(0, 100, size=(num, 10))
    drones_y = np.random.uniform(0, 100, size=(num, 10))
    drones_z = np.random.uniform(20, 25, size=(num, 10))
    drones = np.dstack([drones_x, drones_y, drones_z])
    visual = Visualization(users, drones)
    visual.start(save=True)


if __name__ == '__main__':
    main()
