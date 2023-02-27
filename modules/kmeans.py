"""Naive implementation of KMeans clustering algorithm."""
from __future__ import annotations

import logging
import random
from datetime import datetime

from .color import Color


class KMeans:
    """Naive implementation of KMeans clustering algorithm."""

    _centroids: list[Color] = None

    def __init__(
        self, n_clusters: int, random_seed: int = None, min_dist: float = 1
    ) -> KMeans:
        """Initialize a KMeans object.

        Args:
            n_clusters (int): number of clusters
            random_seed (int, optional): random seed. \
               If none is passed, the current timestamp is used. Defaults to None.
            min_dist (float, optional): minimum square distance between centroids. \
                Defaults to 1.

        Returns:
            KMeans
        """
        self._n_clusters = n_clusters
        self._random_seed = random_seed
        self._min_dist = min_dist

        if random_seed is None:
            self._random_seed = int(datetime.now().timestamp())

    def fit(self, pixels: list[Color]) -> KMeans:
        """Fit the KMeans model.

        Args:
            pixels (list[Color]): list of Color objects

        Returns:
            KMeans
        """
        logging.info(
            "Starting fit of KMeans model. "
            f"n_clusters={self._n_clusters}, min_dist={self._min_dist}, "
            f"random_seed={self._random_seed}."
        )

        # initialize centroids by randomly picking pixels
        random.seed(self._random_seed)
        centroids = random.sample(pixels, self._n_clusters)
        # cound the number of iterations for logging purposes
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

    def _distance(self, pixel: Color, centroid: list[float]) -> float:
        return sum((p - c) ** 2 for p, c in zip(pixel.rgb, centroid.rgb))

    def _centroid(self, cluster: list[list[float]]) -> list[float]:
        return Color(
            *[int(sum(p) / len(p)) for p in zip(*[pixel.rgb for pixel in cluster])]
        )

    @property
    def centroids(self) -> list[Color]:
        """Get the centroids of the clusters.

        Returns:
            list[Color]
        """
        return self._centroids.copy()

    @property
    def clusters(self) -> list[list[Color]]:
        """Get the clusters.

        Returns:
            list[list[Color]]
        """
        return self._clusters.copy()
