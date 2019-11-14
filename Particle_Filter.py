import math
import numpy as np
from numpy import genfromtxt
import statistics
import random
from sklearn.cluster import k_means
import scipy.stats
import matplotlib.pyplot as plt


class ParticleFilter:
    rows = 0
    cols = 0
    x_pos = 0
    y_pos = 0
    th_pos = 0
    particles = 0

    def __init__(self, file_name, cell_size, n_angles, n_samples, resample_rate, sigma_measure, sigma_resample_pos,
                 sigma_resample_angle):
        self.grid_map = genfromtxt(file_name, delimiter=',')  # read in file_name and store as numpy array
        self.pad_border()
        self.buffer_map(1)

        self.cell_size = cell_size
        self.n_angles = n_angles
        self.angle_resolution = 360/n_angles
        self.n_samples = n_samples
        self.resample_rate = resample_rate
        self.sigma_measure = sigma_measure
        self.sigma_resample_pos = sigma_resample_pos
        self.sigma_resample_angle = sigma_resample_angle
        self.rows = np.size(self.grid_map, 0)
        self.cols = np.size(self.grid_map, 1)

        # plt.ion()
        # fig = plt.figure()
        # plt.imshow(self.grid_map, 'Greys')
        # fig.canvas.draw()
        # fig.canvas.flush_events()

        self.init_particles()
        self.update_estimation()

    def pad_border(self):
        self.grid_map = np.pad(self.grid_map, pad_width=1, mode='constant', constant_values=1)

    def buffer_map(self, size):

        # Switcharoo
        self.grid_map = 1 - self.grid_map

        num_rows = self.grid_map.shape[0]  # number of rows (size of Y direction)
        num_cols = self.grid_map.shape[1]  # number of columns (size of X)

        ones_row = np.ones((1, num_cols), dtype=np.int)  # add to top and bottom
        ones_col = np.ones(num_rows, dtype=np.int)  # add to left and right

        for k in range(size):
            # arr1 - shift up (remove first row, add bottom row)
            arr1 = np.delete(self.grid_map, 0, axis=0)  # removes first row
            arr1 = np.insert(arr1, (num_rows - 1), ones_row, axis=0)  # zero adds to the row axis

            # arr2 - shift down (remove last row, add first row)
            arr2 = np.delete(self.grid_map, (num_rows - 1), axis=0)  # removes last row
            arr2 = np.insert(arr2, 0, ones_row, axis=0)

            # arr3 - shift right (remove last column, add first column)
            arr3 = np.delete(self.grid_map, (num_cols - 1), axis=1)
            arr3 = np.insert(arr3, 0, ones_col, axis=1)

            # arr4 - shift left (remove first column, add last column)
            arr4 = np.delete(self.grid_map, 0, axis=1)
            arr4 = np.insert(arr4, (num_cols - 1), ones_col, axis=1)

            # arr5 shift up one AND left one, arr1 is already shifted up, now shift left
            arr5 = np.delete(arr1, 0, axis=1)
            arr5 = np.insert(arr5, (num_cols - 1), ones_col, axis=1)

            # arr6 shift up one AND right one -- shift arr1 right
            arr6 = np.delete(arr1, (num_cols - 1), axis=1)
            arr6 = np.insert(arr6, 0, ones_col, axis=1)

            # arr7 shift down one AND left one -- shift arr2 left
            arr7 = np.delete(arr2, 0, axis=1)
            arr7 = np.insert(arr7, (num_cols - 1), ones_col, axis=1)

            # arr8 shift down one AND right one -- shift arr2 right
            arr8 = np.delete(arr2, (num_cols - 1), axis=1)
            arr8 = np.insert(arr8, 0, ones_col, axis=1)

            self.grid_map = self.grid_map * arr1 * arr2 * arr3 * arr4 * arr5 * arr6 * arr7 * arr8

        # Switcharoo
        self.grid_map = 1 - self.grid_map

    def ray_tracing(self, x_pos, y_pos, direction):

        # Set Max Row/Col to Extremities
        max_row = self.rows
        max_col = self.cols

        # Set Start Row/Col based on Current Location
        start_row = math.floor(y_pos / self.cell_size)
        start_col = math.floor(x_pos / self.cell_size)

        # Wrap Direction to 360 Degrees
        direction = direction % 360

        # Band-aid for Values Where Slopes are 0 or Inf
        if direction == 90 or direction == 180 or direction == 0 or direction == 360 or direction == 270:
            direction = (direction + np.spacing(1000)) % 360

        # Determine the Quadrant of The Direction
        inc_col = int(np.sign(math.cos(direction * np.pi / 180)))
        inc_row = int(np.sign(math.sin(direction * np.pi / 180)))

        ########################################
        # Get Horizontal Scan and Intersection #
        ########################################
        if inc_row > 0:
            delta_y1 = self.cell_size * start_row - y_pos
        else:
            delta_y1 = self.cell_size * (start_row - 1) - y_pos

        delta_x1 = delta_y1 / math.tan(direction * np.pi / 180)

        y_step = inc_row * self.cell_size
        x_step = y_step / math.tan(direction * np.pi / 180)

        current_x = x_pos + delta_x1
        current_y = y_pos + delta_y1

        current_row = start_row + inc_row
        current_col = math.floor(current_x / self.cell_size)

        while True:
            if current_col < 0 or current_col >= max_col:
                x_intersection_h = np.nan
                y_intersection_h = np.nan
                break
            elif current_row < 0 or current_row >= max_row:
                x_intersection_h = current_x
                y_intersection_h = current_y
                break
            elif self.grid_map[current_row, current_col] != 0:
                x_intersection_h = current_x
                y_intersection_h = current_y
                break

            current_x = current_x + x_step
            current_y = current_y + y_step
            current_col = math.floor(current_x / self.cell_size)
            current_row = current_row + inc_row

        ########################################
        # Get Vertical Scan and Intersection #
        ########################################
        if inc_col > 0:
            delta_x1 = self.cell_size * start_col - x_pos
        else:
            delta_x1 = self.cell_size * (start_col - 1) - x_pos

        delta_y1 = delta_x1 * math.tan(direction * np.pi / 180)

        x_step = inc_col * self.cell_size
        y_step = x_step * math.tan(direction * np.pi / 180)

        current_x = x_pos + delta_x1
        current_y = y_pos + delta_y1

        current_col = start_col + inc_col
        current_row = math.floor(current_y / self.cell_size)

        while True:
            if current_row < 0 or current_row >= max_row:
                x_intersection_v = np.nan
                y_intersection_v = np.nan
                break
            elif current_col < 0 or current_col >= max_col:
                x_intersection_v = current_x
                y_intersection_v = current_y
                break
            elif self.grid_map[current_row, current_col] != 0:
                x_intersection_v = current_x
                y_intersection_v = current_y
                break

            current_x = current_x + x_step
            current_y = current_y + y_step
            current_row = math.floor(current_y / self.cell_size)
            current_col = current_col + inc_col

        #####################
        # COMPUTE DISTANCES #
        #####################
        dist_h = math.sqrt(math.pow((x_pos - x_intersection_h), 2) + math.pow((y_pos - y_intersection_h), 2))
        dist_v = math.sqrt(math.pow((x_pos - x_intersection_v), 2) + math.pow((y_pos - y_intersection_v), 2))

        my_list = [dist_h, dist_v]
        min_index = my_list.index(min(my_list))

        if np.isnan(dist_h):
            assert not np.isnan(dist_v)
            return dist_v

        if np.isnan(dist_v):
            assert not np.isnan(dist_h)
            return dist_h

        if min_index == 0:
            distance = dist_h
        else:
            distance = dist_v

        return distance

    # PLOT MAP
    # SHOW LOCATION

    def init_particles(self):

        self.particles = np.full([self.n_samples, 4 + self.n_angles], np.nan)

        weight = 1 / self.n_samples
        max_x = 0.99998 * (self.cols * self.cell_size)
        max_y = 0.99998 * (self.rows * self.cell_size)

        for i in range(self.n_samples):

            self.particles[i][0] = max_x * random.uniform(0, 1.0) + 0.00001
            self.particles[i][1] = max_y * random.uniform(0, 1.0) + 0.00001
            self.particles[i][2] = 359 * random.uniform(0, 1.0)
            self.particles[i][3] = weight

            ind_row = math.floor(self.particles[i][1] / self.cell_size)
            ind_col = math.floor(self.particles[i][0] / self.cell_size)

            while self.grid_map[ind_row, ind_col] != 0:
                self.particles[i][0] = max_x * random.uniform(0, 1) + 0.00001
                self.particles[i][1] = max_y * random.uniform(0, 1) + 0.00001

                ind_row = math.floor(self.particles[i][1] / self.cell_size)
                ind_col = math.floor(self.particles[i][0] / self.cell_size)

            vector_scans = self.get_scans(self.particles[i][0], self.particles[i][1], self.particles[i][2])
            self.particles[i][4:] = vector_scans

    def get_scans(self, x, y, th):

        vector_scans = np.full(self.n_angles, np.nan)

        for i in range(self.n_angles):
            vector_scans[i] = self.ray_tracing(x, y, th)
            th = th + self.angle_resolution

        return vector_scans

    # SHOW PARTICLES

    def move_particles(self, delta_x, delta_y, delta_theta):

        max_x = self.cols * self.cell_size
        max_y = self.rows * self.cell_size
        nan_vec = np.full([1, 4 + self.n_angles], np.nan)

        for i in range(self.n_samples):
            self.particles[i][0] = self.particles[i][0] + delta_x
            self.particles[i][1] = self.particles[i][1] + delta_y
            self.particles[i][2] = (self.particles[i][2] + delta_theta) % 360

            ind_row = math.floor(self.particles[i][1] / self.cell_size)
            ind_col = math.floor(self.particles[i][0] / self.cell_size)

            if (self.particles[i][0] < 0 or self.particles[i][0] >= max_x or
                    self.particles[i][1] < 0 or self.particles[i][1] >= max_y):

                self.particles[i][:] = nan_vec  # outside map

            elif not self.grid_map[ind_row, ind_col] == 0:
                self.particles[i][:] = nan_vec  # inside obstacle

    def weight_computation(self, particle_vector, measurements_vector):

        if not len(particle_vector) == len(measurements_vector):
            RuntimeError('Lidar measurements must have same resolution of particle filter!')

        weight = 1

        for i in range(len(particle_vector)):
            if np.isnan(particle_vector[i]) or np.isnan(measurements_vector[i]):
                continue

            difference = abs(particle_vector[i] - measurements_vector[i])  # assume mm
            prob = scipy.stats.norm(0, self.sigma_measure).pdf(difference)
            weight = weight * prob

        return weight

    def re_sample(self, measurements_vec):

        max_x_gen = 0.99998 * self.cols * self.cell_size
        max_y_gen = 0.99998 * self.rows * self.cell_size

        n_old_samples = round(self.n_samples * (1 - self.resample_rate))

        new_particles = np.full(np.size(self.particles), np.nan)

        np.where(np.isnan(self.particles[:][3]), None, self.particles[:][3])

        for i in range(np.size(self.particles[:][0])):
            self.particles[i][3] = self.weight_computation(self.particles[i][4:], measurements_vec)

        total_weight = math.fsum(self.particles[:][3])
        self.particles[:][3] = round((self.particles[:][3] / total_weight) * n_old_samples)

        index = 0
        weight = 1 / self.n_samples

        for i in range(np.size(self.particles[:][3])):
            for j in range(np.size(self.particles[i][3])):
                thth = np.random.normal(self.particles[i][2], self.sigma_resample_angle) % 360
                xx = abs(np.random.normal(self.particles[i][0], self.sigma_resample_pos))
                yy = abs(np.random.normal(self.particles[i][1], self.sigma_resample_pos))

                if xx > max_x_gen:
                    xx = max_x_gen
                elif xx <= 0:
                    xx = 0.00001

                if yy > max_y_gen:
                    yy = max_y_gen
                elif yy <= 0:
                    yy = 0.00001

                ind_row = math.floor(yy / self.cell_size)
                ind_col = math.floor(xx / self.cell_size)

                while self.grid_map[ind_row][ind_col] != 0:

                    xx = abs(np.random.normal(self.particles[i][0], self.sigma_resample_pos))
                    yy = abs(np.random.normal(self.particles[i][1], self.sigma_resample_pos))

                    if xx > max_x_gen:
                        xx = max_x_gen
                    elif xx <= 0:
                        xx = 0.00001

                    if yy > max_y_gen:
                        yy = max_y_gen
                    elif yy <= 0:
                        yy = 0.00001

                    ind_row = math.floor(yy / self.cell_size)
                    ind_col = math.floor(xx / self.cell_size)

                new_particles[index][0] = xx
                new_particles[index][1] = yy
                new_particles[index][2] = thth

                vector_scans = self.get_scans(xx, yy, thth)

                new_particles[index][4:] = vector_scans
                new_particles[index][3] = weight
                index += 1

                if index > n_old_samples:
                    break

        for i in range(index, self.n_samples):

            new_particles[i][2] = 359 * random.uniform(0, 1)
            new_particles[i][3] = weight

            new_particles[i][0] = max_x_gen * random.uniform(0, 1) + 0.00001
            new_particles[i][1] = max_y_gen * random.uniform(0, 1) + 0.00001

            ind_row = math.floor(new_particles[i][1] / self.cell_size)
            ind_col = math.floor(new_particles[i][0] / self.cell_size)

            while self.grid_map[ind_row][ind_col] != 0:
                new_particles[i][0] = max_x_gen * random.uniform(0, 1) + 0.00001
                new_particles[i][1] = max_y_gen * random.uniform(0, 1) + 0.00001
                ind_row = math.floor(new_particles[i][1] / self.cell_size)
                ind_col = math.floor(new_particles[i][0] / self.cell_size)

            vector_scans = self.get_scans(new_particles[i][0], new_particles[i][1], new_particles[i][2])

            new_particles[i][4:] = vector_scans

        self.particles = new_particles

    def update_estimation(self):

        # COULD USE MODE, MUCH FASTER, SEE WHAT THE PROBLEM REQUIRES

        [vec_pos, c_pos] = k_means(X=self.particles[:,0:2], n_clusters=2)
        #test = k_means(X=self.particles[:,0:2], n_clusters=2)
        [vec_th, c_th] = k_means(X=self.particles[2,:], n_clusters=2)
        #test1 = k_means(X=self.particles[2,:], n_clusters=2)

        ind_pos = statistics.mode(vec_pos)
        ind_th = statistics.mode(vec_th)

        self.y_pos = c_pos[ind_pos][1]
        self.x_pos = c_pos[ind_pos][0]
        self.th_pos = c_th[ind_th]

    def update_state(self, delta_x, delta_y, delta_theta, distance_vec):

        # Move Particles
        self.move_particles(delta_x, delta_y, delta_theta)

        # Resample
        self.re_sample(distance_vec)

        # Update Estimation
        self.update_estimation()

