from enum import Enum


class ColType(Enum):
    NODE = 1
    EDGE = 2
    DOUBLE_EDGE = 3
    EYEGLASSES = 4
    DIRECTED_TRIANGLE = 5
    LONG_SQUARE = 6


class Column:
    def __init__(self, col_type, data, entrance_time=None):
        self.col_type = col_type
        self.data = data
        self.entrance_time = entrance_time

    def __repr__(self):
        return f"{self.col_type.name}{self.data.__repr__()} at {self.entrance_time}"

    # Entrance time is just some data we attach to the column
    # We want to be able to hash by the basis element alone
    def __eq__(self, other):
        return (self.col_type, self.data) == (other.col_type, other.data)

    def __hash__(self):
        return hash((self.col_type, self.data))

    def dimension(self):
        if self.col_type == ColType.NODE:
            return 0
        elif self.col_type == ColType.EDGE:
            return 1
        else:
            return 2

    def sparse_boundary(self, col2idx_map):
        return (self.dimension(), Column._sparsify(self.boundary(), col2idx_map))

    def _sparsify(bdry, col2idx_map):
        sparse_bdry = []
        for col in bdry:
            idx = col2idx_map[col]
            sparse_bdry.append(idx)
        return sorted(sparse_bdry)

    def boundary(self):
        if self.col_type == ColType.NODE:
            return []
        if self.col_type == ColType.EDGE:
            return [Column.NODE(self.data[0]), Column.NODE(self.data[1])]
        if self.col_type == ColType.DOUBLE_EDGE:
            return [Column.EDGE((self.data)), Column.EDGE(tuple(reversed(self.data)))]
        if self.col_type == ColType.EYEGLASSES:
            return [
                Column.EDGE((self.data[0], self.data[1])),
                Column.EDGE((self.data[1], self.data[0])),
                Column.EDGE((self.data[0], self.data[2])),
                Column.EDGE((self.data[2], self.data[0])),
            ]
        if self.col_type == ColType.DIRECTED_TRIANGLE:
            return [
                Column.EDGE((self.data[0], self.data[1])),
                Column.EDGE((self.data[1], self.data[2])),
                Column.EDGE((self.data[0], self.data[2])),
            ]
        if self.col_type == ColType.LONG_SQUARE:
            return [
                Column.EDGE((self.data[0], self.data[1])),
                Column.EDGE((self.data[1], self.data[3])),
                Column.EDGE((self.data[0], self.data[2])),
                Column.EDGE((self.data[2], self.data[3])),
            ]


def _add_column_type_method(cls, col_type):
    def setter(data, entrance_time=None):
        return cls(col_type, data, entrance_time)

    setattr(cls, col_type.name, setter)


for c in ColType:
    _add_column_type_method(Column, c)


def convert_to_sparse(cols):
    sparse_cols = []
    col2idx_map = {}
    for col in cols:
        sparse_bdry = col.sparse_boundary(col2idx_map)
        insertion_idx = len(sparse_cols)
        sparse_cols.append(sparse_bdry)
        col2idx_map[col] = insertion_idx
    return sparse_cols
