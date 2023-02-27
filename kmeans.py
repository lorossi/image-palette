from __future__ import annotations

import logging
import random


class KMeans:
    _centroids: list[list[float]] = None

    def __init__(
        self, n_clusters: int, initial_state: int = 0, min_dist: float = 1
    ) -> KMeans:
        self._n_clusters = n_clusters
        self._initial_state = initial_state
        self._min_dist = min_dist

        random.seed(self._initial_state)

    def fit(self, pixels: list[list[float]]) -> KMeans:
        centroids = random.sample(pixels, self._n_clusters)

        logging.info(
            "Starting fit of KMeans model. "
            f"n_clusters={self._n_clusters}, min_dist={self._min_dist}"
        )

        iteration = 0
        while True:
            logging.info(f"Iteration {iteration}...")
            clusters = [[] for _ in range(self._n_clusters)]

            for pixel in pixels:
                dist = [self._distance(pixel, centroid) for centroid in centroids]
                clusters[dist.index(min(dist))].append(pixel)

            new_centroids = [self._centroid(cluster) for cluster in clusters]

            if all(
                self._distance(c1, c2) < self._min_dist
                for c1, c2 in zip(centroids, new_centroids)
            ):
                self._centroids = centroids
                self._clusters = clusters
                logging.info("Fitting completed.")
                break

            centroids = new_centroids
            iteration += 1
            logging.info(f"Iteration {iteration} completed.")

        return self

    def _distance(self, pixel: list[float], centroid: list[float]) -> float:
        return sum((p - c) ** 2 for p, c in zip(pixel, centroid)) ** 0.5

    def _centroid(self, cluster: list[list[float]]) -> list[float]:
        return [sum(pixel) / len(pixel) for pixel in zip(*cluster)]

    @property
    def centroids(self) -> list[list[float]]:
        return self._centroids.copy()

    @property
    def clusters(self) -> list[list[list[float]]]:
        return self._clusters.copy()
