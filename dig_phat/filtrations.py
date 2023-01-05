import numpy as np
import networkx as nx
from abc import ABC, abstractmethod


def _non_trivial_dict(sp_iter):
    return {
        source: {
            target: distance
            for target, distance in distances.items()
            if target != source
        }
        for source, distances in sp_iter
    }


class AbstractFiltration(ABC):
    def __init__(self, G):
        self.G = G

    @abstractmethod
    def time(self, edge):
        pass

    @abstractmethod
    def edge_iter(self):
        pass

    @abstractmethod
    def edge_dict(self):
        pass


class ShortestPathFiltration(AbstractFiltration):
    def __init__(self, G):
        super().__init__(G)
        self.distances = _non_trivial_dict(nx.all_pairs_dijkstra_path_length(G))

    def time(self, edge):
        try:
            return self.distances[edge[0]][edge[1]]
        except KeyError:
            # No path so never enters
            return np.inf

    def edge_iter(self):
        return [
            ((source, target), dist)
            for source, distances in self.distances.items()
            for target, dist in distances.items()
        ]

    def edge_dict(self):
        return self.distances
