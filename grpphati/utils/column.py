def convert_to_sparse(cols):
    sparse_cols = []
    col2idx_map = [{}, {}, {}]
    for col in cols:
        sparse_bdry = col.sparse_boundary(col2idx_map)
        insertion_idx = len(sparse_cols)
        sparse_cols.append(sparse_bdry)
        col2idx_map[col.dimension()][col] = insertion_idx
    return sparse_cols

class SparseConstructor:
    def __init__(self, basis_iter):
        self.basis_iter = basis_iter
        self.col2idx_map = [{}, {}, {}]
        self.next_insertion_idx = 0

    def __iter__(self):
        return self
    
    def __next__(self):
        # Might throw error which ripples through this iterator
        col = next(self.basis_iter)
        sparse_bdry = col.sparse_boundary(self.col2idx_map)
        self.col2idx_map[col.dimension()][col] = self.next_insertion_idx
        self.next_insertion_idx += 1
        return sparse_bdry

