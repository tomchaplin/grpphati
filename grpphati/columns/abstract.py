from abc import ABC, abstractmethod


class Column(ABC):
    @abstractmethod
    def __repr__(self):
        pass

    @abstractmethod
    def __eq__(self, other):
        pass

    @abstractmethod
    def __hash__(self):
        pass

    @abstractmethod
    def dimension(self):
        pass

    @abstractmethod
    def boundary(self):
        pass

    @staticmethod
    def _sparsify(bdry, col2idx_map):
        sparse_bdry = []
        for col in bdry:
            idx = col2idx_map[col.dimension()][col]
            sparse_bdry.append(idx)
        return sorted(sparse_bdry)

    def sparse_boundary(self, col2idx_map):
        return (self.dimension(), Column._sparsify(self.boundary(), col2idx_map))
