from abc import ABC, abstractmethod


class Filtration(ABC):
    @abstractmethod
    def node_time(self, node):
        pass

    @abstractmethod
    def edge_time(self, edge):
        pass

    @abstractmethod
    def node_iter(self):
        pass

    @abstractmethod
    def edge_iter(self):
        pass

    @abstractmethod
    def edge_dict(self):
        pass

    def ground(self, grounding_G):
        return StandardGroundedFiltration(grounding_G, self)


class StandardGroundedFiltration(Filtration):
    def __init__(self, G, filtration):
        self.G = G
        self.filtration = filtration

    def node_time(self, node):
        return 0 if self.G.has_node(node) else self.filtration.node_time(node)

    def edge_time(self, edge):
        return 0 if self.G.has_edge(*edge) else self.filtration.edge_time(edge)

    def node_iter(self):
        return [(node, 0) for node in self.G.nodes] + [
            (node, dist)
            for node, dist in self.filtration.node_iter()
            if not self.G.has_node(node)
        ]

    def edge_iter(self):
        return [(edge, 0) for edge in self.G.edges] + [
            (edge, dist)
            for edge, dist in self.filtration.edge_iter()
            if not self.G.has_edge(*edge)
        ]

    def edge_dict(self):
        filtration_dict = self.filtration.edge_dict()
        for i, j in self.G.edges:
            filtration_dict[i][j] = 0
        return filtration_dict

    def ground(self, grounding_G):
        raise Exception("Attempted to ground an already grounded filtration")


# Useful when V(F^t G) \subseteq V(G)
class ProperGroundedFiltration(StandardGroundedFiltration):
    def node_time(self, node):
        return 0

    def node_iter(self):
        return self.filtration.node_iter()
