from collections import namedtuple

from cad.util import calibrate_up, calibrate_down

Fig = namedtuple('Fig', ['vertices', 'faces', 'category', 'box'])
Box = namedtuple('Box', ['min_x', 'max_x', 'min_y', 'max_y', 'min_z', 'max_z'])

def calculate_bounding_box(figs, conf):
    min_x = 1000000000
    min_y = 1000000000
    min_z = 1000000000
    max_x = -1000000000
    max_y = -1000000000
    max_z = -1000000000

    for fig in figs:
        if fig.category in conf['distances']:
            allowed_distance = conf['distances'][fig.category]
        else:
            allowed_distance = conf['default_distance']
        allowed_distance += conf['wire_width']
        for x, y, z in fig.vertices:
            min_x = min(min_x, x - allowed_distance)
            min_y = min(min_y, y - allowed_distance)
            min_z = min(min_z, z - allowed_distance)
            max_x = max(max_x, x + allowed_distance)
            max_y = max(max_y, y + allowed_distance)
            max_z = max(max_z, z)
    box = Box(
        min_x=min_x,
        max_x=max_x,
        min_y=min_y,
        max_y=max_y,
        min_z=min_z,
        max_z=max_z,
    )

    return calibrate_box(box, conf)


def calculate_bounding_box_of_one_fig(vertices, category, conf):
    min_x = 1000000000
    min_y = 1000000000
    min_z = 1000000000
    max_x = -1000000000
    max_y = -1000000000
    max_z = 1000000000

    if category in conf['distances']:
        allowed_distance = conf['distances'][category]
    else:
        allowed_distance = conf['default_distance']
    allowed_distance += conf['wire_width']
    for x, y, z in vertices:
        min_x = min(min_x, x - allowed_distance)
        min_y = min(min_y, y - allowed_distance)
        min_z = min(min_z, z - allowed_distance)
        max_x = max(max_x, x + allowed_distance)
        max_y = max(max_y, y + allowed_distance)
    box = Box(
        min_x=min_x,
        max_x=max_x,
        min_y=min_y,
        max_y=max_y,
        min_z=min_z,
        max_z=max_z,
    )

    return calibrate_box(box, conf)


def point_in_box(p, box):
    return box.min_x <= p[0] <= box.max_x and box.min_y <= p[1] <= box.max_y and box.min_z <= p[2] <= box.max_z


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
