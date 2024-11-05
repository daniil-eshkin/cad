import numpy as np
import json
import yaml

from cad.util import Box, Fig

def parse_fig(data):
    vertices = np.array(np.array_split(data['Coords'], len(data['Coords']) // 3)) * 1.0
    faces = np.array(np.array_split(data['Indices'], len(data['Indices']) // 3))

    return Fig(
        vertices=vertices,
        faces=faces,
        category=data['Category'],
    )


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
        for x, y, z in fig.vertices:
            min_x = min(min_x, x)
            min_y = min(min_y, y)
            min_z = min(min_z, z - allowed_distance)
            max_x = max(max_x, x)
            max_y = max(max_y, y)
            max_z = max(max_z, z)
    return Box(
        min_x=min_x,
        max_x=max_x,
        min_y=min_y,
        max_y=max_y,
        min_z=min_z,
        max_z=max_z,
    )


def parse_model(path, conf):
    with open(path, 'r') as file:
        data = json.load(file)
    figs = list(map(parse_fig, data))

    return (list(filter(lambda f: f.category == 'Floors', figs))
            , list(filter(lambda f: f.category != 'Floors', figs))
            , calculate_bounding_box(figs, conf))


def parse_config(path):
    # Default config
    conf = {
        'grid': {
            'starting_point': {
                'x': 0,
                'y': 0,
                'z': 0,
            },
            'length': 10,
        },
        'wire_width': 10,
        'default_distance': 100,
        'distances': {
            'Floors': 0,
        },
    }

    with open(path, 'r') as file:
        data = yaml.load(file, yaml.SafeLoader)

    if 'grid' in data and data['grid'] is not None:
        if 'starting_point' in data['grid'] and data['grid']['starting_point'] is not None:
            if 'x' in data['grid']['starting_point'] and data['grid']['starting_point']['x'] is not None:
                conf['grid']['starting_point']['x'] = data['grid']['starting_point']['x']
            if 'y' in data['grid']['starting_point'] and data['grid']['starting_point']['y'] is not None:
                conf['grid']['starting_point']['y'] = data['grid']['starting_point']['y']
            if 'z' in data['grid']['starting_point'] and data['grid']['starting_point']['z'] is not None:
                conf['grid']['starting_point']['z'] = data['grid']['starting_point']['z']
        if 'length' in data['grid'] and data['grid']['length'] is not None:
            conf['grid']['length'] = data['grid']['length']
    if 'wire_width' in data and data['wire_width'] is not None:
        conf['wire_width'] = data['wire_width']
    if 'default_distance' in data and data['default_distance'] is not None:
        conf['default_distance'] = data['default_distance']
    if 'distances' in data and data['distances'] is not None:
        for category, distance in data['distances'].items():
            if distance is not None:
                conf["distances"][category] = distance

    return conf


def parse_input(path):
    with open(path, 'r') as file:
        data = json.load(file)
    return ([data['start']['x'], data['start']['y'], data['start']['z']]
            , [data['end']['x'], data['end']['y'], data['end']['z']])
