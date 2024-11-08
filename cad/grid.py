import sys
from queue import PriorityQueue

import meshlib.mrmeshnumpy as mrmeshnumpy
import meshlib.mrmeshpy as mr
import numpy as np
from progressbar import ProgressBar
from sklearn.neighbors import NearestNeighbors

from cad.util import cartesian_product
from cad.box import point_in_box

class Grid:
    def __init__(self, x, y, z, start, end, model, conf):
        self.model = model

        # Flatten points numeration: (x[i], y[j], z[k]) -> i * len(y) * len(z) + j * len(z) + k
        self.points = cartesian_product(x, y, z)

        self.is_valid = np.array(list(map(lambda i: self.is_valid_point(i), np.arange(0, len(self.points)))))
        self.valid_points = self.points[self.is_valid]

        self.length = len(x)
        self.width = len(y)
        self.height = len(z)
        self.size = len(self.points)
        self.start = start
        self.end = end
        self.conf = conf

        # Calculate start and end neighbors (8 closest points on grid)
        neigh = NearestNeighbors(n_neighbors=8, metric='euclidean', algorithm='brute').fit(self.valid_points)
        self.start_neighbors, self.end_neighbors = neigh.kneighbors([start, end], return_distance=False)
        self.start_neighbors = np.arange(0, len(self.points))[self.is_valid][self.start_neighbors]
        self.end_neighbors = np.arange(0, len(self.points))[self.is_valid][self.end_neighbors]

        # Add start and end to array of points
        self.points = np.concatenate((self.points, np.array([start, end])), axis=0)
        self.is_valid = np.concatenate((self.is_valid, np.array([True, True])), axis=0)
        self.start_idx = self.size
        self.end_idx = self.size + 1

        # Group objects by category and build meshes
        categories = {}
        for m in model:
            if m.category not in categories:
                v, f = np.array([[0,0,0]]), np.array([[0,0,0]])
            else:
                v, f = categories[m.category]
            categories[m.category] = (np.append(v, m.vertices, axis=0)
                                      , np.append(f, m.faces + len(v), axis=0))

        self.categories = {}
        for c, (v, f) in categories.items():
            self.categories[c] = mrmeshnumpy.meshFromFacesVerts(f, v)

    # A* end distance estimation (Manhattan metric is used for more straight paths)
    def estimate(self, v):
        return np.linalg.norm(self.points[v] - self.end, ord=1)


    # Distance between two points (Euclidean metric)
    def dist(self, v, u):
        return np.linalg.norm(self.points[v] - self.points[u])


    def is_straight_pair_of_edges(self, a, b, c):
        if a == -1 or b == -1 or c == -1:
            return False
        return np.array_equal(self.points[b] - self.points[a], self.points[c] - self.points[b])


    # Indices in self.points array
    def neighbor_indices(self, v):
        if v == self.start_idx:
            return self.start_neighbors
        if v == self.end_idx:
            return self.end_neighbors
        i, j, k = v // self.height // self.width, v // self.height % self.width, v % self.height

        neigh = np.array([
            [1, 0, 0],
            [0, 1, 0],
            [0, 0, 1],
            [-1, 0, 0],
            [0, -1, 0],
            [0, 0, -1]
        ]) + np.array([i, j, k])

        neigh = np.array(list(
            map (
                lambda p: p[0] * self.width * self.height + p[1] * self.height + p[2],
                filter(
                    lambda p: 0 <= p[0] < self.length and 0 <= p[1] < self.width and 0 <= p[2] < self.height,
                    neigh,
                ),
            )
        ))
        if v in self.start_neighbors:
            neigh = np.append(neigh, [self.start_idx])
        if v in self.end_neighbors:
            neigh = np.append(neigh, [self.end_idx])

        return neigh


    def is_valid_point(self, v):
        return any(map(lambda f: point_in_box(self.points[v], f.box), self.model))


    # Check distance between edge and model
    def is_valid_edge(self, v, u):
        a = self.points[v]
        b = self.points[u]
        # Thin triangle mesh (it works)
        edge_mesh = mrmeshnumpy.meshFromFacesVerts(np.array([[0, 1, 2]]), np.array([a, b, b]))
        for category, mesh in self.categories.items():
            # Signed distance is negative, when meshes collide
            distance = mr.findSignedDistance(edge_mesh, mesh).signedDist
            if category in self.conf['distances']:
                allowed_distance = self.conf['distances'][category]
            else:
                allowed_distance = self.conf['default_distance']
            if distance < self.conf['wire_width'] + allowed_distance:
                return False
        return True


    # A* algorithm
    def get_path(self):
        q = PriorityQueue()
        dist = np.full(len(self.points), np.inf)
        turns = np.full(len(self.points), np.inf)
        prev = np.full(len(self.points), -1)
        dist[self.start_idx] = 0
        turns[self.start_idx] = 0
        q.put((
            (self.estimate(self.start_idx), 0),
            (self.start_idx, 0)
        ))

        # Progress bar by estimated distance to end
        est = self.estimate(self.start_idx)
        bar = ProgressBar(start=0, maxval=est, fd=sys.stdout)
        cur_est = est

        while not q.empty():
            (_, t), (v, d) = q.get()
            if dist[v] != d or turns[v] != t:
                continue

            # Update progress bar
            new_est = self.estimate(v)
            if new_est < cur_est:
                bar.update(est - new_est)
                cur_est = new_est

            if v == self.end_idx:
                break

            for to in self.neighbor_indices(v):
                if self.is_straight_pair_of_edges(prev[v], v, to):
                    t = turns[v]
                else:
                    t = turns[v] + 1
                if self.is_valid[to] and self.is_valid_edge(v, to) and (dist[v] + self.dist(v, to), t) < (dist[to], turns[to]):
                    dist[to] = dist[v] + self.dist(v, to)
                    turns[to] = t
                    prev[to] = v
                    q.put((
                        (dist[to] + self.estimate(to), t),
                        (to, dist[to])
                    ))

        bar.finish()

        v = self.end_idx
        path = []
        while v != -1:
            path.append(v)
            v = prev[v]

        path = np.array(list(reversed(path)))

        return self.points[path]
