from .abstract import Sparsifier


class ListSparsifier(Sparsifier):
    def __init__(self, return_dimension=True):
        self.return_dimension = return_dimension

    def __call__(self, cols):
        sparse_cols = []
        col2idx_map = {}
        for col in cols:
            bdry = col.boundary()
            sparse_bdry = Sparsifier._sparsify(bdry, col2idx_map)
            if self.return_dimension:
                sparse_bdry = (col.dimension(), sparse_bdry)
            insertion_idx = len(sparse_cols)
            sparse_cols.append(sparse_bdry)
            col2idx_map[col] = insertion_idx
        return sparse_cols
