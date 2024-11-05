import sys
from queue import PriorityQueue

import meshlib.mrmeshnumpy as mrmeshnumpy
import meshlib.mrmeshpy as mr
import numpy as np
from progressbar import ProgressBar
from sklearn.neighbors import NearestNeighbors

from cad.util import cartesian_product


class Grid:
    def __init__(self, x, y, z, start, end, model, conf):
        # Flatten points numeration: (x[i], y[j], z[k]) -> i * len(y) * len(z) + j * len(z) + k
        self.points = cartesian_product(x, y, z)

        self.length = len(x)
        self.width = len(y)
        self.height = len(z)
        self.size = len(self.points)
        self.start = start
        self.end = end
        self.conf = conf

        # Calculate start and end neighbors (8 closest points on grid)
        neigh = NearestNeighbors(n_neighbors=8, metric='euclidean', algorithm='brute').fit(self.points)
        self.start_neighbors, self.end_neighbors = neigh.kneighbors([start, end], return_distance=False)

        # Add start and end to array of points
        self.points = np.concatenate((self.points, np.array([start, end])), axis=0)
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
        prev = np.full(len(self.points), -1)
        dist[self.start_idx] = 0
        q.put((self.estimate(self.start_idx), (self.start_idx, 0)))

        # Progress bar by estimated distance to end
        est = self.estimate(self.start_idx)
        bar = ProgressBar(start=0, maxval=est, fd=sys.stdout)
        cur_est = est

        while not q.empty():
            _, (v, d) = q.get()
            if dist[v] != d:
                continue

            # Update progress bar
            new_est = self.estimate(v)
            if new_est < cur_est:
                bar.update(est - new_est)
                cur_est = new_est

            if v == self.end_idx:
                break

            for to in self.neighbor_indices(v):
                if self.is_valid_edge(v, to) and dist[v] + self.dist(v, to) < dist[to]:
                    dist[to] = dist[v] + self.dist(v, to)
                    prev[to] = v
                    q.put((dist[to] + self.estimate(to), (to, dist[to])))

        bar.finish()

        v = self.end_idx
        path = []
        while v != -1:
            path.append(v)
            v = prev[v]

        path = np.array(list(reversed(path)))

        return self.points[path]
