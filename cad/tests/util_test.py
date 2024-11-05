import unittest

from cad.util import *

class UtilTest(unittest.TestCase):
    def test_cartesian_product(self):
        self.assertTrue(np.array_equal(
            cartesian_product(np.array([1, 2]), np.array([3, 4]), np.array([5, 6])),
            np.array([
                [1, 3, 5],
                [1, 3 ,6],
                [1, 4, 5],
                [1, 4, 6],
                [2, 3, 5],
                [2, 3, 6],
                [2, 4, 5],
                [2, 4, 6],
            ])
        ))


    def test_calibrate_up(self):
        self.assertEqual(calibrate_up(0, 2, -2), -2)
        self.assertEqual(calibrate_up(0, 2, -1), 0)
        self.assertEqual(calibrate_up(0, 2, 0), 0)
        self.assertEqual(calibrate_up(0, 2, 1), 2)
        self.assertEqual(calibrate_up(0, 2, 2), 2)

        self.assertEqual(calibrate_up(1, 2, -2), -1)
        self.assertEqual(calibrate_up(1, 2, -1), -1)
        self.assertEqual(calibrate_up(1, 2, 0), 1)
        self.assertEqual(calibrate_up(1, 2, 1), 1)
        self.assertEqual(calibrate_up(1, 2, 2), 3)

        self.assertEqual(calibrate_up(-1, 2, -2), -1)
        self.assertEqual(calibrate_up(-1, 2, -1), -1)
        self.assertEqual(calibrate_up(-1, 2, 0), 1)
        self.assertEqual(calibrate_up(-1, 2, 1), 1)
        self.assertEqual(calibrate_up(-1, 2, 2), 3)


    def test_calibrate_down(self):
        self.assertEqual(calibrate_down(0, 2, -2), -2)
        self.assertEqual(calibrate_down(0, 2, -1), -2)
        self.assertEqual(calibrate_down(0, 2, 0), 0)
        self.assertEqual(calibrate_down(0, 2, 1), 0)
        self.assertEqual(calibrate_down(0, 2, 2), 2)

        self.assertEqual(calibrate_down(1, 2, -2), -3)
        self.assertEqual(calibrate_down(1, 2, -1), -1)
        self.assertEqual(calibrate_down(1, 2, 0), -1)
        self.assertEqual(calibrate_down(1, 2, 1), 1)
        self.assertEqual(calibrate_down(1, 2, 2), 1)

        self.assertEqual(calibrate_down(-1, 2, -2), -3)
        self.assertEqual(calibrate_down(-1, 2, -1), -1)
        self.assertEqual(calibrate_down(-1, 2, 0), -1)
        self.assertEqual(calibrate_down(-1, 2, 1), 1)
        self.assertEqual(calibrate_down(-1, 2, 2), 1)


if __name__ == '__main__':
    unittest.main()
