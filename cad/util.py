import numpy as np
from collections import namedtuple

Fig = namedtuple('Fig', ['vertices', 'faces', 'category'])
Box = namedtuple('Box', ['min_x', 'max_x', 'min_y', 'max_y', 'min_z', 'max_z'])

def cartesian_product(x, y, z):
    mx, my, mz = np.meshgrid(y, x, z)
    return np.array([my.ravel(), mx.ravel(), mz.ravel()]).transpose()

# Move point (x) to the closest point on start + step * t upwards
def calibrate_up(start, step, x):
    return x + (start - x) % step

# Move point (x) to the closest point on start + step * t downwards
def calibrate_down(start, step, x):
    y = calibrate_up(start, step, x)
    if y == x:
        return y
    else:
        return y - step

# Match bounding box and grid
def calibrate_box(box, conf):
    return Box(
        min_x=calibrate_down(conf['grid']['starting_point']['x'], conf['grid']['length'], box.min_x),
        min_y=calibrate_down(conf['grid']['starting_point']['y'], conf['grid']['length'], box.min_y),
        min_z=calibrate_down(conf['grid']['starting_point']['z'], conf['grid']['length'], box.min_z),
        max_x=calibrate_up(conf['grid']['starting_point']['x'], conf['grid']['length'], box.max_x),
        max_y=calibrate_up(conf['grid']['starting_point']['y'], conf['grid']['length'], box.max_y),
        max_z=calibrate_up(conf['grid']['starting_point']['z'], conf['grid']['length'], box.max_z),
    )

# Convert faces structure to PyVista format: [[0, 1, 2],[3, 4, 5]] -> [3, 0, 1, 2, 3, 3, 4, 5]
def pv_faces(faces):
    return np.concatenate(np.hstack((np.full((len(faces), 1), 3), faces)))
