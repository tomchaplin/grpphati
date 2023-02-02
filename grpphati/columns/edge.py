from .abstract import Column
from .node import NodeCol


class EdgeCol(Column):
    def __init__(self, edge, entrance_time=None):
        self.edge = edge
        self.entrance_time = entrance_time

    def __repr__(self):
        return f"Edge {self.edge} :: {self.entrance_time}"

    def __eq__(self, other):
        return isinstance(other, EdgeCol) and self.edge == other.edge

    def __hash__(self):
        return hash((EdgeCol, self.edge))

    def dimension(self):
        return 1

    def boundary(self):
        return [NodeCol(self.edge[0]), NodeCol(self.edge[1])]
