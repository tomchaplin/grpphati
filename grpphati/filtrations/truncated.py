import numpy as np
from .abstract import Filtration


class TruncatedFiltration(Filtration):
    def __init__(self, filtration: Filtration, truncation_time):
        self.filtration = filtration
        self.truncation_time = truncation_time

    def node_time(self, node):
        underlying_time = self.filtration.node_time(node)
        if underlying_time > self.truncation_time:
            return np.inf
        else:
            return underlying_time

    def edge_time(self, edge):
        underlying_time = self.filtration.edge_time(edge)
        if underlying_time > self.truncation_time:
            return np.inf
        else:
            return underlying_time

    def node_iter(self):
        return [
            (node, t)
            for node, t in self.filtration.node_iter()
            if t <= self.truncation_time
        ]

    def edge_iter(self):
        return [
            (edge, t)
            for edge, t in self.filtration.edge_iter()
            if t <= self.truncation_time
        ]

    def edge_dict(self):
        return {
            source: {
                target: distance
                for target, distance in distances.items()
                if distance <= self.truncation_time
            }
            for source, distances in self.filtration.edge_dict().items()
        }

    def ground(self, grounding_G):
        return TruncatedFiltration(
            self.filtration.ground(grounding_G), self.truncation_time
        )
