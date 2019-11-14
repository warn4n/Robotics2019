import numpy as np
import ray_tracing as ray


def get_scans_vector(grid_map, n_angles, cell_size, x, y, th):

    vector_scans = np.full(n_angles, np.nan)
    angle_resolution = 360/n_angles

    for i in range(n_angles):

        vector_scans[i] = ray.ray_tracing(x, y, th, grid_map, cell_size)
        th = th + angle_resolution

    return vector_scans
