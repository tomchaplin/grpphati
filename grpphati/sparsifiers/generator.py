from .abstract import Sparsifier


class GeneratorSparsifier(Sparsifier):
    def __init__(self, return_dimension=True):
        self.return_dimension = return_dimension

    def __iter__(self):
        return self

    def __call__(self, col_iter):
        self.col_iter = col_iter
        self.next_insertion_idx = 0
        self.col2idx_map = {}
        return self

    def __next__(self):
        col = next(self.col_iter)
        bdry = col.boundary()
        sparse_bdry = Sparsifier._sparsify(bdry, self.col2idx_map)
        if self.return_dimension:
            sparse_bdry = (col.dimension(), sparse_bdry)
        self.col2idx_map[col] = self.next_insertion_idx
        self.next_insertion_idx += 1
        return sparse_bdry
