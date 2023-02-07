from abc import ABC, abstractmethod


class Sparsifier(ABC):
    @abstractmethod
    def __call__(self, cols):
        pass

    @staticmethod
    def _sparsify(bdry, col2idx_map):
        sparse_bdry = []
        for col in bdry:
            idx = col2idx_map[col]
            sparse_bdry.append(idx)
        return sorted(sparse_bdry)
