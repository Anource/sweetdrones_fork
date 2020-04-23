import numpy as np
import random
from scipy.spatial import Voronoi
from scipy.optimize import minimize


class KMeans:
    def __init__(self, params):
        self.params = params
        self.area_x = params['area_x']
        self.area_y = params['area_y']
        self.drones_number = params['drones_number']
        self.drones_height = params['drones_height']
        self.users_height = params['users_height']
        self.snr_threshold = params['snr_threshold']

    def generate_new_positions(self, drones, users):
        dists = [drones[d].get_antenna_distance(self.snr_threshold) for d in range(self.drones_number)]
        drones_radius = np.sqrt(dists[0]**2 - (self.drones_height - self.users_height)**2)
        new_drones, new_regions, new_radii = self.sd_km(users, drones_radius)
        return np.array(new_drones), np.array(new_regions)

    # def get_diagrams(self):

    def sd_km(self, users, radius):
        xx = []
        yy = []

        for res in users:
            xx.append(res[0])
            yy.append(res[1])

        def cluster_points(X, mu):
            clusters = {}
            for x in X:
                bestmukey = min([(i[0], np.linalg.norm(x - mu[i[0]])) \
                                 for i in enumerate(mu)], key=lambda t: t[1])[0]
                try:
                    clusters[bestmukey].append(x)
                except KeyError:
                    clusters[bestmukey] = [x]
            return clusters

        def reevaluate_centers(clusters):
            newmu = []
            keys = sorted(clusters.keys())
            for k in keys:
                newmu.append(np.mean(clusters[k], axis=0))
            return newmu

        def has_converged(mu, oldmu):
            return set([tuple(a) for a in mu]) == set([tuple(a) for a in oldmu])

        def find_centers(X, K):
            X = list(X)
            # Initialize to K random centers
            oldmu = random.sample(X, K)
            mu = random.sample(X, K)
            while not has_converged(mu, oldmu):
                oldmu = mu
                # Assign all points in X to clusters
                clusters = cluster_points(X, mu)
                # Reevaluate centers
                mu = reevaluate_centers(clusters)
            return mu

        def min_distance_from_point_to_segment_of_line(px, py, line):
            x1 = line[0][0]
            y1 = line[0][1]
            x2 = line[1][0]
            y2 = line[1][1]
            return np.abs(px * (y1 - y2) + py * (x2 - x1) + (x1 * y2 - y1 * x2)) / get_distance(x1, y1, x2, y2)

        def resolve_minlp():

            def get_max_radius(par):
                xv = par[0]
                yv = par[1]
                max_radius = radius
                for reg_line in reg:
                    radius_temp = min_distance_from_point_to_segment_of_line(xv, yv, reg_line)
                    if max_radius > radius_temp:
                        max_radius = radius_temp
                return max_radius

            def get_number_of_covered_users(par):
                xv = par[0]
                yv = par[1]
                counter = 0

                max_radius = get_max_radius(par)

                if all(check_restriction(xv, yv, reg[i], new_reg_orient[i])
                       and np.round(min_distance_from_point_to_segment_of_line(xv, yv, reg[i])) >= max_radius
                       for i in range(len(reg))):
                    dist = np.sqrt((xv - xx) ** 2 + (yv - yy) ** 2)
                    for d in dist:
                        if d <= max_radius:
                            counter -= 1
                return counter

            x0 = np.array(center0)
            result1 = minimize(get_number_of_covered_users, x0, method='powell',
                               options={'xtol': 1e-8, 'disp': False})

            # if max_radius < max_radius_1:
            #     max_radius = max_radius_1
            # if max_radius > radius:
            # max_radius = radius
            return result1.x, get_max_radius(x0)

        def check_restriction(x, y, line, orient):
            c_y = check_y(x, y, line[0][0], line[0][1], line[1][0], line[1][1])
            c_x = check_x(np.abs(get_angle(line, [[0, 0], [1, 0]])), c_y)
            return c_x == orient[0] and c_y == orient[1]

        def check_x(angle, c_y):
            return (c_y and np.abs(angle) > 90) or (not c_y and np.abs(angle) < 90)

        def check_y(px, py, x1, y1, x2, y2):
            return px * (y1 - y2) + py * (x2 - x1) + (x1 * y2 - y1 * x2) < 0

        def get_a_b(line, above):
            a = (line[1][1] - line[0][1]) / (line[1][0] - line[0][0])
            b = line[0][1] - line[0][0] * a
            return [a, b, above]

        def get_distance(point1_x, point1_y, point2_x, point2_y):
            return np.sqrt((point1_x - point2_x) ** 2 + (point1_y - point2_y) ** 2)

        def get_angle(line1, line2):
            a_b = get_a_b(line1, True)
            a1, b1 = a_b[0], a_b[1]
            a_b = get_a_b(line2, True)
            a2, b2 = a_b[0], a_b[1]

            x = (b2 - b1) / (a1 - a2)
            y = a2 * x + b2

            p0 = [line1[0][0], line1[0][1]]
            p1 = [x, y]
            p2 = [line2[0][0], line2[0][1]]

            v0 = np.array(p0) - np.array(p1)
            v1 = np.array(p2) - np.array(p1)

            angle = np.math.atan2(np.linalg.det([v0, v1]), np.dot(v0, v1))
            return np.degrees(angle)

        K = self.drones_number
        points = []
        while len(points) < K:
            points = find_centers(users[:, :2], K)
        points = np.array(points)
        vor = Voronoi(points)
        # voronoi_plot_2d(vor)
        # plt.show()
        center = vor.points.mean(axis=0)
        ptp_bound = vor.points.ptp(axis=0)

        finite_segments = []
        infinite_segments = []
        for pointidx, simplex in zip(vor.ridge_points, vor.ridge_vertices):
            simplex = np.asarray(simplex)
            if np.all(simplex >= 0):
                finite_segments.append(vor.vertices[simplex])
            else:
                i = simplex[simplex >= 0][0]  # finite end Voronoi vertex

                t = vor.points[pointidx[1]] - vor.points[pointidx[0]]  # tangent
                t /= np.linalg.norm(t)
                n = np.array([-t[1], t[0]])  # normal

                midpoint = vor.points[pointidx].mean(axis=0)
                direction = np.sign(np.dot(midpoint - center, n)) * n
                far_point = vor.vertices[i] + direction * ptp_bound.max()

                infinite_segments.append([vor.vertices[i], far_point])

        v_points = vor.points
        point_reg = []
        regs = []
        radii = []
        # print(vor.ridge_vertices)
        # print(len(v_points))
        for i in range(len(v_points)):
            reg = []
            for rp in vor.ridge_points:
                if i == rp[0] or i == rp[1]:
                    for seg in infinite_segments + finite_segments:
                        if np.round(np.abs(get_angle([v_points[rp[0]], v_points[rp[1]]], seg))) == 90:
                            reg.append(seg)
                            break
            # for j in range(len(v_points)):
            #     if i != j:
            #         for inf_seg in infinite_segments:
            #             if np.round(np.abs(get_angle([v_points[i], v_points[j]], inf_seg))) == 90:
            #                 if all(not np.array_equal(r, inf_seg) for r in reg):
            #                     reg.append(inf_seg)
            # reg_s = []
            # for r in reg:
            #     for r1 in reg:
            #         stop = False
            #         for seg in finite_segments:
            #             if (np.array_equal(seg[0], r[0]) and np.array_equal(seg[1], r1[0])) \
            #                     or (np.array_equal(seg[0], r[0]) and np.array_equal(seg[1], r1[1])) \
            #                     or (np.array_equal(seg[0], r[1]) and np.array_equal(seg[1], r1[0])) \
            #                     or (np.array_equal(seg[0], r[1]) and np.array_equal(seg[1], r1[1])):
            #                 if all(not np.array_equal(r2, seg) for r2 in reg_s):
            #                     reg_s.append(seg)
            #                 stop = True
            #                 break
            #         if stop:
            #             break
            # reg = reg + reg_s

            new_reg_orient = []
            for line in reg:
                y2 = line[1][1]
                x2 = line[1][0]
                y1 = line[0][1]
                x1 = line[0][0]
                py = v_points[i][1]
                px = v_points[i][0]
                angle = get_angle([[x1, y1], [x2, y2]], [[0, 0], [1, 0]])

                orient_y = check_y(px, py, x1, y1, x2, y2)
                orient_x = check_x(angle, orient_y)
                new_reg_orient.append([orient_x, orient_y])

            center0 = v_points[i]
            resolve, new_radius = resolve_minlp()
            resolve = list(resolve)
            resolve.append(self.drones_height)
            point_reg.append(resolve)
            regs.append(reg)
            radii.append(new_radius)

        return np.array(point_reg), regs, radii
