from .abstract import Column
from .edge import EdgeCol


class DoubleEdgeCol(Column):
    def __init__(self, forward_edge, entrance_time=None):
        self.forward_edge = forward_edge
        self.entrance_time = entrance_time

    def __repr__(self):
        return f"Double Edge {(self.forward_edge[0], self.forward_edge[1], self.forward_edge[0])} :: {self.entrance_time}"

    def __eq__(self, other):
        return isinstance(other, DoubleEdgeCol) and (
            self.forward_edge[0],
            self.forward_edge[1],
        ) == (
            other.forward_edge[0],
            other.forward_edge[1],
        )

    def __hash__(self):
        return hash((DoubleEdgeCol, self.forward_edge))

    def dimension(self):
        return 2

    def boundary(self):
        return [EdgeCol(self.forward_edge), EdgeCol(tuple(reversed(self.forward_edge)))]
