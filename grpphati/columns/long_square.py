from .abstract import Column
from .edge import EdgeCol


class LongSquareCol(Column):
    def __init__(self, start, midpoints, end, entrance_time=None):
        self.start = start
        self.midpoints = midpoints
        self.end = end
        self.entrance_time = entrance_time

    def __repr__(self):
        return f"Long Square ({self.start},{self.midpoints},{self.end}) :: {self.entrance_time}"

    def __eq__(self, other):
        return isinstance(other, LongSquareCol) and (
            self.start == other.start
            and self.midpoints == other.midpoints
            and self.end == other.end
        )

    def __hash__(self):
        return hash((LongSquareCol, (self.start, self.midpoints, self.start)))

    def dimension(self):
        return 2

    def boundary(self):
        return [
            EdgeCol((self.start, self.midpoints[0])),
            EdgeCol((self.start, self.midpoints[1])),
            EdgeCol((self.midpoints[0], self.end)),
            EdgeCol((self.midpoints[1], self.end)),
        ]
