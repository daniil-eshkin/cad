import numpy as np
import sys

from cad.parser import parse_model, parse_config, parse_input
from cad.plotter import show_model
from cad.grid import Grid

def main(conf_path, model_path, input_path):
    conf = parse_config(conf_path)

    # Get start and end of path
    start, end = parse_input(input_path)

    # Get objects and raw bounding box
    floors, objs, box = parse_model(model_path, conf)

    # Generate grid points
    x = np.arange(box.min_x, box.max_x + 1, conf['grid']['length'])
    y = np.arange(box.min_y, box.max_y + 1, conf['grid']['length'])
    z = np.arange(box.min_z, box.max_z + 1, conf['grid']['length'])

    # Build graph
    grid = Grid(x, y, z, start, end, floors + objs, conf)

    # Calculate wire path
    path = grid.get_path()

    # Visualize
    show_model(floors, objs, grid.valid_points, start, end, path, conf)

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], sys.argv[3])
