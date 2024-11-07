import numpy as np

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

# Convert faces structure to PyVista format: [[0, 1, 2],[3, 4, 5]] -> [3, 0, 1, 2, 3, 3, 4, 5]
def pv_faces(faces):
    return np.concatenate(np.hstack((np.full((len(faces), 1), 3), faces)))
