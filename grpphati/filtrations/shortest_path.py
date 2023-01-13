import numpy as np
import networkx as nx
from .abstract import Filtration, ProperGroundedFiltration


class ShortestPathFiltration(Filtration):
    def __init__(self, G):
        self.nodes = G.nodes
        self.distances = _non_trivial_dict(nx.all_pairs_dijkstra_path_length(G))

    def node_time(self, node):
        return 0

    def edge_time(self, edge):
        try:
            return self.distances[edge[0]][edge[1]]
        except KeyError:
            # No path so never enters
            return np.inf

    def node_iter(self):
        return [(node, 0) for node in self.nodes]

    def edge_iter(self):
        return [
            ((source, target), dist)
            for source, distances in self.distances.items()
            for target, dist in distances.items()
        ]

    def edge_dict(self):
        return self.distances

    def ground(self, grounding_G):
        return ProperGroundedFiltration(grounding_G, self)


def _non_trivial_dict(sp_iter):
    return {
        source: {
            target: distance
            for target, distance in distances.items()
            if target != source and np.isfinite(distance)
        }
        for source, distances in sp_iter
    }
