from .abstract import Column
from .edge import EdgeCol


class DirectedTriangleCol(Column):
    def __init__(self, two_path, entrance_time=None):
        self.two_path = two_path
        self.entrance_time = entrance_time

    def __repr__(self):
        return f"Directed Triangle {self.two_path} :: {self.entrance_time}"

    def __eq__(self, other):
        return (
            isinstance(other, DirectedTriangleCol) and self.two_path == other.two_path
        )

    def __hash__(self):
        return hash((DirectedTriangleCol, self.two_path))

    def dimension(self):
        return 2

    def boundary(self):
        return [
            EdgeCol((self.two_path[0], self.two_path[1])),
            EdgeCol((self.two_path[1], self.two_path[2])),
            EdgeCol((self.two_path[0], self.two_path[2])),
        ]
