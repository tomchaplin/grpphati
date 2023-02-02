from .abstract import Column


class NodeCol(Column):
    def __init__(self, node, entrance_time=None):
        self.node = node
        self.entrance_time = entrance_time

    def __repr__(self):
        return f"Node {self.node} :: {self.entrance_time}"

    def __eq__(self, other):
        return isinstance(other, NodeCol) and self.node == other.node

    def __hash__(self):
        return hash((NodeCol, self.node))

    def dimension(self):
        return 0

    def boundary(self):
        return []
