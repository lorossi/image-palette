"""Naive implementation of KMeans clustering algorithm."""
from __future__ import annotations

import logging
import random
from datetime import datetime

from .color import Color


class KMeans:
    """Naive implementation of KMeans clustering algorithm."""

    _centroids: list[Color] = None
    _clusters: list[list[Color]] = None
    _avg_dist: float = None

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
        self._centroids = random.sample(pixels, self._n_clusters)
        self._pixels = pixels
        # cound the number of iterations for logging purposes
        iteration = 0
        while True:
            logging.info(f"Iteration {iteration}...")
            self._invalidateAvgDist()
            self._clusters = [[] for _ in range(self._n_clusters)]

            logging.info("Assigning pixels to clusters...")
            for pixel in self._pixels:
                dist = [
                    self._sq_distance(pixel, centroid) for centroid in self._centroids
                ]
                self._clusters[dist.index(min(dist))].append(pixel)

            logging.info("Calculating new centroids...")
            new_centroids = [self._centroid(cluster) for cluster in self._clusters]
            self._centroids = new_centroids

            logging.info(f"Average distance: {self.avg_dist:.2f}")

            if self.avg_dist < self._min_dist:
                logging.info("Fitting completed.")
                break

            logging.info(f"Iteration {iteration} completed.")
            iteration += 1

        return self

    def _sq_distance(self, pixel: Color, centroid: list[float]) -> float:
        return sum((p - c) ** 2 for p, c in zip(pixel.rgb, centroid.rgb))

    def _centroid(self, cluster: list[list[float]]) -> list[float]:
        return Color(
            *[int(sum(p) / len(p)) for p in zip(*[pixel.rgb for pixel in cluster])]
        )

    def _calculateAvgDist(self) -> float:
        return (
            sum(
                [
                    self._sq_distance(pixel, centroid)
                    for centroid, cluster in zip(self._centroids, self._clusters)
                    for pixel in cluster
                ]
            )
            / len(self._pixels)
        ) ** 0.5

    def _invalidateAvgDist(self) -> None:
        self._avg_dist = None

    @property
    def avg_dist(self) -> float:
        """Get the average distance between pixels and their centroids.

        Returns:
            float
        """

        if self._avg_dist is None:
            self._avg_dist = self._calculateAvgDist()

        return self._avg_dist

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
