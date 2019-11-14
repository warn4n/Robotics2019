import math
import numpy as np


def ray_tracing(x_pos, y_pos, direction, gridmap, cell_size):

    # Set Max Row/Col to Extremities
    max_row = len(gridmap)
    max_col = len(gridmap[0])

    # Set Start Row/Col based on Current Location
    start_row = math.floor(y_pos / cell_size)
    start_col = math.floor(x_pos / cell_size)

    # Wrap Direction to 360 Degrees
    direction = direction % 360

    # Band-aid for Values Where Slopes are 0 or Inf
    if direction == 90 or direction == 180 or direction == 0 or direction == 360 or direction == 270:
        direction = (direction + np.spacing(1000)) % 360

    # Check if Position is Outside of Map *
    if start_row < 1 or start_row > max_row or start_col < 1 or start_col > max_col:
        RuntimeError('Location outside of map!')

    # Check if We Start Inside an Obstacle *
    if gridmap[start_row][start_col] != 0:
        RuntimeError('Location outside of map!')

    # Determine the Quadrant of The Direction
    inc_col = np.sign(math.cos(direction * np.pi / 180))
    inc_row = np.sign(math.sin(direction * np.pi / 180))

    ########################################
    # Get Horizontal Scan and Intersection #
    ########################################
    if inc_row > 0:
        delta_y1 = cell_size * start_row - y_pos
    else:
        delta_y1 = cell_size * (start_row - 1) - y_pos

    delta_x1 = delta_y1 / math.tan(direction * np.pi / 180)

    y_step = inc_row * cell_size
    x_step = y_step / math.tan(direction * np.pi / 180)

    current_x = x_pos + delta_x1
    current_y = y_pos + delta_y1

    current_row = start_row + inc_row
    current_col = math.floor(current_x / cell_size)

    while True:
        if current_col < 1 or current_col > max_col:
            x_intersection_h = np.nan
            y_intersection_h = np.nan
            break
        elif current_row < 1 or current_row > max_row:
            x_intersection_h = current_x
            y_intersection_h = current_y
            break
        elif gridmap(current_row, current_col) != 0:
            x_intersection_h = current_x
            y_intersection_h = current_y
            break

        current_x = current_x + x_step
        current_y = current_y + y_step
        current_col = math.floor(current_x / cell_size)
        current_row = current_row + inc_row

    ########################################
    # Get Vertical Scan and Intersection #
    ########################################
    if inc_col > 0:
        delta_x1 = cell_size * start_col - x_pos
    else:
        delta_x1 = cell_size * (start_col - 1) - x_pos

    delta_y1 = delta_x1 * math.tan(direction * np.pi / 180)

    x_step = inc_col * cell_size
    y_step = x_step * math.tan(direction * np.pi / 180)

    current_x = x_pos + delta_x1
    current_y = y_pos + delta_y1

    current_col = start_col + inc_col
    current_row = math.floor(current_y / cell_size)

    while True:
        if current_row < 1 or current_row > max_row:
            x_intersection_v = np.nan
            y_intersection_v = np.nan
            break
        elif current_col < 1 or current_col > max_col:
            x_intersection_v = current_x
            y_intersection_v = current_y
            break
        elif gridmap(current_row, current_col) != 0:
            x_intersection_v = current_x
            y_intersection_v = current_y
            break

        current_x = current_x + x_step
        current_y = current_y + y_step
        current_row = math.floor(current_y / cell_size)
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
    else:
        distance = dist_v

    return distance
