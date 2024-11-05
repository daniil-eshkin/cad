import unittest

from cad.grid import *
from cad.util import *

class GridTest(unittest.TestCase):

    def test_is_valid_edge(self):
        # Given
        conf = {
            'grid': {
                'starting_point': {
                    'x': 0,
                    'y': 0,
                    'z': 0,
                },
                'length': 1,
            },
            'wire_width': 1,
            'default_distance': 10,
            'distances': {
                'Floors': 0,
                'Objs': 1,
            },
        }

        model = [
            Fig(
                vertices=np.array([[0, 0, 0],
                                   [0, 2, 0],
                                   [0, 0, 2]], dtype=np.float32),
                faces=np.array([[0, 1, 2]]),
                category="Floors"
            ),
            Fig(
                vertices=np.array([[3, 0, 0],
                                   [3, 2, 0],
                                   [3, 0, 2]], dtype=np.float32),
                faces=np.array([[0, 1, 2]]),
                category="Objs"
            ),
        ]

        box = Box(
            min_x=0,
            max_x=3,
            min_y=0,
            max_y=2,
            min_z=0,
            max_z=2,
        )
        x = np.arange(box.min_x, box.max_x + 1, 1, dtype=np.float32)
        y = np.arange(box.min_y, box.max_y + 1, 1, dtype=np.float32)
        z = np.arange(box.min_z, box.max_z + 1, 1, dtype=np.float32)

        grid = Grid(x, y, z, np.array([0, 0, 0]), np.array([0, 0, 0]), model, conf)

        # Edge closer to Floor is valid
        self.assertTrue(grid.is_valid_edge(1 * len(z) * len(y) + 1, 1 * len(z) * len(y) + 1 * len(z) + 1))
        self.assertFalse(grid.is_valid_edge(2 * len(z) * len(y) + 1, 2 * len(z) * len(y) + 1 * len(z) + 1))


if __name__ == '__main__':
    unittest.main()
