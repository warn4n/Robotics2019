import math
import numpy as np
import pandas as pd
import statistics
import random
import sklearn as sk


class ParticleFilter:
	rows = 0
	cols = 0
	N_samples = 0
	x_pos = 0
	y_pos = 0
	th_pos = 0
	particles = 0

	def __init__(self, csv, cell_size, num_angles, angle_resolution, resample_rate, sigma_measure, sigma_resample_pos,
	             sigma_resample_angle):
		self.grid_map = pd.read_csv(csv).values  # read in csv and store as numpy array
		self.cell_size = cell_size
		self.n_angles = num_angles
		self.angle_resolution = angle_resolution
		self.resample_rate = resample_rate
		self.sigma_measure = sigma_measure
		self.sigma_resample_pos = sigma_resample_pos
		self.sigma_resample_angle = sigma_resample_angle
		self.loc_rows = np.size(self.grid_map, 0)
		self.loc_cols = np.size(self.grid_map, 1)

		init_particles()
		self.update_estimation()

	def ray_tracing(self, x_pos, y_pos, direction):

		# Set Max Row/Col to Extremities
		max_row = self.loc_rows
		max_col = self.loc_cols

		# Set Start Row/Col based on Current Location
		start_row = math.floor(y_pos / self.cell_size) + 1
		start_col = math.floor(x_pos / self.cell_size) + 1

		# Wrap Direction to 360 Degrees
		direction = direction % 360

		# Band-aid for Values Where Slopes are 0 or Inf
		if direction == 90 or direction == 180 or direction == 0 or direction == 360 or direction == 270:
			direction = (direction + np.spacing(1000)) % 360

		# Check if Position is Outside of Map *
		if start_row < 1 or start_row > max_row or start_col < 1 or start_col > max_col:
			distance = float('nan')
			end_point_x = float('nan')
			end_point_y = float('nan')
			print('Location outside of Map!')

		# Check if We Start Inside an Obstacle *
		if self.grid_map[start_row][start_col] != 0:
			distance = float('nan')
			end_point_x = float('nan')
			end_point_y = float('nan')
			print('Location Inside of Obstacle!')

		# Determine the Quadrant of The Direction
		inc_col = np.sign(math.cos(direction * np.pi / 180))
		inc_row = np.sign(math.sin(direction * np.pi / 180))

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
		current_col = math.floor(current_x / self.cell_size) + 1

		while True:
			if current_col < 1 or current_col > max_col:
				x_intersection_h = np.nan
				y_intersection_h = np.nan
				break
			elif current_row < 1 or current_row > max_row:
				x_intersection_h = current_x
				y_intersection_h = current_y
				break
			elif self.grid_map(current_row, current_col) != 0:
				x_intersection_h = current_x
				y_intersection_h = current_y
				break

			current_x = current_x + x_step
			current_y = current_y + y_step
			current_col = math.floor(current_x / self.cell_size) + 1
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
		current_row = math.floor(current_y / self.cell_size) + 1

		while True:
			if current_row < 1 or current_row > max_row:
				x_intersection_v = np.nan
				y_intersection_v = np.nan
				break
			elif current_col < 1 or current_col > max_col:
				x_intersection_v = current_x
				y_intersection_v = current_y
				break
			elif self.grid_map(current_row, current_col) != 0:
				x_intersection_v = current_x
				y_intersection_v = current_y
				break

			current_x = current_x + x_step
			current_y = current_y + y_step
			current_row = math.floor(current_y / self.cell_size) + 1
			current_row = current_row + inc_col

		#####################
		# COMPUTE DISTANCES #
		#####################
		dist_h = math.sqrt(math.pow((x_pos - x_intersection_h), 2) + math.pow((y_pos - y_intersection_h), 2))
		dist_v = math.sqrt(math.pow((x_pos - x_intersection_v), 2) + math.pow((y_pos - y_intersection_v), 2))

		my_list = [dist_h, dist_v]
		min_index = my_list.index(min(my_list))

		if min_index == 0:
			distance = dist_h
			end_point_x = x_intersection_h
			end_point_y = y_intersection_h
		else:
			distance = dist_v
			end_point_x = x_intersection_v
			end_point_y = y_intersection_v

		return distance, end_point_x, end_point_y

	def update_estimation(self):

		# COULD USE MODE, MUCH FASTER, SEE WHAT THE PROBLEM REQUIRES
		[vec_pos, c_pos] = sk.cluster.k_means(X=self.particles[:][0:2], n_clusters=2)
		[vec_th, c_th] = sk.cluster.k_means(X=self.particles[:][2], n_clusters=2)

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

	def re_sample(self, measurements_vec):

		max_x_gen = 0.99998 * self.cols * self.cell_size
		max_y_gen = 0.99998 * self.rows * self.cell_size

		n_old_samples = round(self.N_samples * (1 - self.resample_rate))

		new_particles = np.full(np.size(self.particles), np.nan)

		np.where(np.isnan(self.particles[:][3]), None, self.particles[:][3])

		for i in range(np.size(self.particles[:][0])):
			self.particles[i][3] = self.weight_computation(self.particles[i][5:], measurements_vec)

		total_weight = math.fsum(self.particles[:][3])
		self.particles[:][3] = round((self.particles[:][3] / total_weight) * n_old_samples)

		index = 1
		weight = 1 / self.N_samples

		for i in range(np.size(self.particles[:][3])):
			for j in range(np.size(self.particles[i][3])):
				thth = () % 360

	def init_particles(self):
		self.particles = np.empty((self.N_samples, 4 + self.n_angles,))
		weight = 1 / self.N_samples
		max_x = 0.99998 * (self.cols*self.cell_size)
		max_y = 0.99998 * (self.rows * self.cell_size)

		for i in range(self.N_samples):
			self.particles[i][2] = 359*random.uniform(0, 1)
			self.particles[i][3] = weight
			
			self.particles[i][0] = max_x * random.uniform(0, 1) + 0.00001
			self.particles[i][1] = max_y * random.uniform(0 ,1) + 0.00001
			ind_row = math.floor(self.particles[i][2]/self.cell_size) + 1
			ind_col = math.floor(self.particles[i][1]/self.cell_size) + 1

			while not self.grid_map[ind_row,ind_col]  == 0:
				self.particles[i][0] = max_x*random.uniform(0, 1) + 0.00001
				self.particles[i][1] = max_y*random.uniform(0, 1) + 0.00001

				ind_row = math.floor(self.particles[i][1] / self.cell_size) + 1
				ind_col = math.floor(self.particles[i][0] / self.cell_size) + 1

			vector_scans = self.get_scans(self.particles[i][0],self.particles[i][1],self.particles[i][2])
			self.particles[i][4:] = vector_scans

			
